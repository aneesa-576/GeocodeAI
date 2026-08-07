import glob
import logging
import os

import kagglehub
import pandas as pd
from app.config import settings
from app.models.address import ParsedAddress
from app.utils.normalization import normalize_component

logger = logging.getLogger(__name__)


class PincodeResult:
    def __init__(self, parsed: ParsedAddress | None = None):
        self.parsed = parsed
        self.requested_pincode = parsed.pincode if parsed else None
        self.matched_pincode = None
        self.centroid = None
        self.state = None
        self.district = None
        self.locality = None
        self.conflict = False
        self.corrections = []

    def add_correction(self, original: str, corrected: str, reason: str):
        self.corrections.append(
            {
                "original_component": original,
                "corrected_component": corrected,
                "reason": reason,
            }
        )


class PincodeService:
    loaded = False
    data: pd.DataFrame | None = None

    def __init__(self):
        if not self.__class__.loaded:
            self.__class__.load_dataset()
        self.loaded = self.__class__.loaded

    @classmethod
    def load_dataset(cls):
        """
        Dynamically downloads or locates the cached Kaggle dataset on startup
        and reads it safely into a shared class-level DataFrame.
        """
        try:
            logger.info("Initializing Pincode dataset verification service...")
            # Prefer a CSV path provided via environment (tests set PINCODE_CSV_PATH),
            # falling back to the value in settings if not present.
            csv_path = os.getenv("PINCODE_CSV_PATH") or getattr(
                settings, "pincode_csv_path", None
            )
            if csv_path and os.path.exists(csv_path):
                target_csv = csv_path
                logger.info(
                    f"Loading pincode ground truth into memory from settings path: {target_csv}"
                )
                df = pd.read_csv(target_csv)
            else:
                # Fall back to downloading via kagglehub
                download_path = kagglehub.dataset_download(
                    "shibin007/all-india-pincode-directory2025"
                )
                csv_files = glob.glob(os.path.join(download_path, "*.csv"))
                if not csv_files:
                    raise FileNotFoundError(
                        f"No CSV file found in kagglehub path: {download_path}"
                    )
                target_csv = csv_files[0]
                logger.info(
                    f"Loading pincode ground truth into memory from: {target_csv}"
                )
                df = pd.read_csv(target_csv)

            # Standardize expected columns to match the Kaggle dataset structure
            expected = [
                "pincode",
                "state_name",
                "district_name",
                "office_name",
                "latitude",
                "longitude",
            ]
            for col in expected:
                if col not in df.columns:
                    raise ValueError(f"Missing required pincode column: {col}")

            df = df.astype({"pincode": str})
            cls.data = df
            cls.loaded = True
            logger.info(
                f"Successfully loaded {len(df)} pincode records into shared memory."
            )
        except Exception as e:
            logger.critical(f"Critical error loading Pincode Service dataset: {str(e)}")
            cls.data = None
            cls.loaded = False

    def verify(self, parsed: ParsedAddress) -> PincodeResult:
        result = PincodeResult(parsed)

        # Fixed the structural logic bug from the original code statement
        if not parsed.pincode or self.data is None:
            result.matched_pincode = None
            return result

        mask = self.data["pincode"] == str(parsed.pincode).strip()
        if mask.any():
            row = self.data[mask].iloc[0]
            result.matched_pincode = parsed.pincode
            result.centroid = {
                "lat": float(row["latitude"]),
                "lon": float(row["longitude"]),
            }
            result.state = normalize_component(str(row["state_name"]))
            result.district = normalize_component(str(row["district_name"]))
            result.locality = normalize_component(str(row["office_name"]))

            if parsed.state and normalize_component(parsed.state) != result.state:
                result.conflict = True
                result.add_correction(
                    parsed.state, str(row["state_name"]), "pincode-state mismatch"
                )

            if (
                parsed.district
                and normalize_component(parsed.district) != result.district
            ):
                result.conflict = True
                result.add_correction(
                    parsed.district,
                    str(row["district_name"]),
                    "pincode-district mismatch",
                )
        else:
            # Pincode entered does not exist; try deterministic locality-based resolution
            nearest = self._find_nearest_pincode(parsed)
            if nearest is not None:
                result.matched_pincode = str(nearest["pincode"])
                result.centroid = {
                    "lat": float(nearest["latitude"]),
                    "lon": float(nearest["longitude"]),
                }
                result.state = normalize_component(str(nearest["state_name"]))
                result.district = normalize_component(str(nearest["district_name"]))
                result.locality = normalize_component(str(nearest["office_name"]))

                if parsed.pincode:
                    result.conflict = True
                    result.add_correction(
                        parsed.pincode,
                        str(nearest["pincode"]),
                        "invalid or incorrect pincode corrected by centroid match",
                    )
        return result

    def _find_nearest_pincode(self, parsed: ParsedAddress) -> pd.Series | None:
        if not parsed.locality or self.data is None:
            return None

        norm_locality = normalize_component(parsed.locality)
        office_norm = self.data["office_name"].astype(str).map(normalize_component)
        matches = self.data[office_norm == norm_locality]

        if not matches.empty:
            return matches.iloc[0]
        return None
