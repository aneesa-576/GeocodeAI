📍 GeocodeAI (Pata AI) — Location Intelligence for Last-Mile Delivery

> **AI Build 2026 · E-Commerce in India · Student Edition**  
> **Track 1: Pata · Category: Last Mile & Field Operations**

An agentic location intelligence system engineered to resolve unstructured, landmark-relative Indian addresses into precise spatial coordinates in **under 500ms**, eliminating last-mile delivery failures.

---

## 📑 Table of Contents
- [Problem Statement](#-problem-statement)
- [The GeocodeAI Solution](#-the-geocodeai-solution)
- [System Architecture](#-system-architecture)
- [Repository Structure](#-repository-structure)
- [How It Works (Agent Breakdown)](#-how-it-works-agent-breakdown)
- [Guardrails & Compliance](#-guardrails--compliance)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [API Reference](#-api-reference)
- [Business Impact & Performance Metrics](#-business-impact--performance-metrics)

---

## 🎯 Problem Statement

In India, e-commerce addresses are messy, unstructured free-text strings. They rely heavily on:
* **Relative landmark directions:** *"opposite Ganesh temple"*, *"near SBI ATM"*, *"behind government school"*
* **Informal colony names & regional spellings:** Hinglish, transliterated names, and regional scripts
* **Inaccurate or missing pincodes:** Incorrect 6-digit postal codes entered by customers

Standard commercial geocoders (e.g., standard Google Maps or Mapbox search) often fail on these inputs. They default to dropping generic map pins at **pincode centroids**—often hundreds of meters away from the actual doorstep. 

### The Cost of Failure
A delivery partner handling **60–100 drops per day** loses hours to:
1. Frequent phone calls to customers for directions.
2. Circling the block trying to find informal landmarks.
3. Marking shipments as *"Customer Not Available"* or returning parcels back to hub.

---

## 💡 The GeocodeAI Solution

**GeocodeAI** replaces blind spatial guessing with a **multi-agent hybrid pipeline** that grounds messy address strings against real-world spatial anchors and government pincode databases.

### Core Objectives Achieved:
* ⚡ **Sub-500ms Latency:** Fast enough to execute at checkout/order-placement time without degrading UX.
* 📍 **Landmark Grounding:** Uses OpenStreetMap (Overpass API) to locate real-world POIs and calculate exact spatial offsets.
* 🔎 **Evidence-Based Audit Trail:** Shows *why* a geocode was chosen (matching landmark node ID, pincode mutation history, confidence scores).
* 🚩 **Confidence Thresholding:** Automatically flags low-confidence results (< 0.50) for field verification instead of silently outputting bad pins.

---

## 🏗️ System Architecture
┌────────────────────────────────────────────────────────────────────────┐│                        RAW MESSY INDIAN ADDRESS                        ││   "Flat 302, opp Ganesh temple, near SBI ATM, Mg road, 500038 hyd"     │└─────────────────────────────────┬──────────────────────────────────────┘│▼┌────────────────────────────────────────────────────────────────────────┐│  AGENT 1: Multilingual Address Parser (< 120ms)                        ││  • Parses: Door No, Landmarks, Sub-locality, City, Pincode             │└─────────────────────────────────┬──────────────────────────────────────┘│▼┌────────────────────────────────────────────────────────────────────────┐│  AGENT 2: DuckDB Pincode & Locality Ground-Truthing (< 80ms)           ││  • Matches All India Pincode Directory CSV in-memory                   ││  • Auto-corrects invalid or mismatched pincodes                        │└─────────────────────────────────┬──────────────────────────────────────┘│▼┌────────────────────────────────────────────────────────────────────────┐│  AGENT 3: Overpass OSM Spatial Anchor Finder (< 200ms)                 ││  • Bounding-box search around centroid for real POIs (temples, ATMs)   ││  • Computes relative spatial offset coordinates                        │└─────────────────────────────────┬──────────────────────────────────────┘│▼┌────────────────────────────────────────────────────────────────────────┐│  AGENT 4: Confidence Scoring & Self-Check (< 50ms)                      ││  • Calculates Geocode Confidence Score (0.0 – 1.0)                     ││  • Returns High-Confidence Geocode OR Flags for Field Verification     │└─────────────────────────────────┬──────────────────────────────────────┘
---

## 📁 Repository Structure

```text
GeocodeAI/
├── data/
│   └── pincodes_india_2025.csv    # All India Pincode Directory ground truth
├── src/
│   ├── main.py                    # FastAPI Application Orchestrator & Endpoints
│   ├── schemas.py                 # Pydantic Schemas (Requests, Responses, Audit Logs)
│   └── agents/
│       ├── __init__.py
│       ├── parser.py              # Agent 1: Fast Regex & Entity Address Parser
│       ├── pincode_matcher.py     # Agent 2: DuckDB Ground-Truth Pincode Engine
│       ├── overpass_agent.py      # Agent 3: OSM Spatial Anchor Finder
│       └── scoring_agent.py       # Agent 4: Confidence Scoring & Self-Check Engine
├── static/
│   └── index.html                 # Leaflet.js Interactive Field Operations Dashboard
├── requirements.txt               # Python package dependencies
└── README.md                      # Complete project documentation
🧩 How It Works (Agent Breakdown)1️⃣ Agent 1: Multilingual Address Parser (src/agents/parser.py)Strips noise and parses free-text into structural tokens:Extracts door/flat numbers (Flat 302)Isolates spatial landmark trigger phrases (opp Ganesh temple, near SBI ATM)Identifies pincodes and locality strings
2️⃣ Agent 2: Pincode Ground-Truth Engine (src/agents/pincode_matcher.py)Loads the All India Pincode Directory 2025 into an in-memory DuckDB instance.Performs sub-10ms queries to verify if the provided pincode exists and matches the state/district.If the pincode is missing or wrong, it uses fuzzy sub-locality matching to correct the pincode automatically and logs a pincode_mutated flag in the audit trail.
3️⃣ Agent 3: Overpass OSM Spatial Anchor Finder (src/agents/overpass_agent.py)Takes the landmark string extracted by Agent 1 (Ganesh temple) and builds a 1km bounding box around the pincode centroid from Agent 2.Executes a targeted live Overpass API query to search OpenStreetMap for matching POIs (amenity, place_of_worship, building).Adjusts latitude and longitude coordinates based on the retrieved POI node location.
4️⃣ Agent 4: Confidence Scoring & Self-Check (src/agents/scoring_agent.py)Computes a weighted confidence score ($S$) based on data quality:$$S = 0.45 \cdot C_{\text{pincode\_match}} + 0.15 \cdot C_{\text{pincode\_valid}} + 0.40 \cdot C_{\text{landmark\_found}}$$HIGH (0.85 – 1.00): Auto-assigned direct delivery pin.MEDIUM (0.50 – 0.84): Validated geocode with landmark highlighted.LOW (< 0.50): Flagged for driver confirmation / customer verification.
🛡️ Guardrails & ComplianceData Residency (DPDP Act India): Configured for hosting on India-resident cloud infrastructure (ap-south-1 Mumbai). No address data leaves regional boundaries.Data Privacy: Raw customer address strings are processed in RAM and immediately dropped once coordinates and hashes are generated.Auditability: Every single automated correction retains a full, transparent audit trail linking back to the original raw address.
🛠️ Tech StackBackend: Python 3.11, FastAPI, Uvicorn, PydanticIn-Memory Analytics: DuckDB, RapidFuzzSpatial Anchor Data: OpenStreetMap Overpass APIFrontend: Leaflet.js, TailwindCSS, HTML5/JavaScript
🚀 Getting StartedPrerequisitesPython 3.11 or higher installed on your machine.Git
