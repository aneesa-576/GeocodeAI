from app.services.parser import AddressParserService


def test_parser_fallback_with_simple_address():
    parser = AddressParserService()
    parsed = parser._fallback_parse(
        "Shop 12, Near MG Road, Indiranagar, Bangalore 560038"
    )
    assert parsed.city is not None
    assert parsed.pincode == "560038"
    assert parsed.landmark is not None
    assert parsed.locality is not None
