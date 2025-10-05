# tests/test_utils_validators.py
import pytest
import os
from bin_creator.cli import utils, validators


def test_parse_int():
    # parsowanie liczby dziesiętnej
    assert utils.parse_int("42", name="test_param", max_bits=32) == 42
    # parsowanie liczby szesnastkowej
    assert utils.parse_int("0x10", name="test_param", max_bits=32) == 16

    # sprawdzenie błędu przy przekroczeniu bitów
    with pytest.raises(SystemExit):
        utils.parse_int("0x1FFFFFFFF", name="test_param", max_bits=32)  # ponad 32 bity

    # sprawdzenie błędu przy niepoprawnym formacie
    with pytest.raises(SystemExit):
        utils.parse_int("notanumber", name="test_param", max_bits=32)

def test_parse_key_formats():
    key1 = utils.parse_key("00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF")
    key2 = utils.parse_key("00112233445566778899AABBCCDDEEFF")
    assert key1 == key2
    assert len(key1) == 16

def test_validate_file_paths(tmp_path):
    input_file = tmp_path / "in.bin"
    input_file.write_bytes(b"\x00")
    output_file = tmp_path / "out.bin"

    # Powinno przejść bez błędu
    validators.validate_file_paths(str(input_file), str(output_file))

    # Brak input_file -> powinien wywołać SystemExit
    with pytest.raises(SystemExit):
        validators.validate_file_paths(str(tmp_path / "missing.bin"), str(output_file))



# -----------------------
# parse_int już mamy pokryte w poprzednich testach
# -----------------------

# -----------------------
# parse_key – klucz za krótki
# -----------------------
def test_parse_key_too_short():
    with pytest.raises(SystemExit) as e:
        utils.parse_key("00112233")  # za krótki
    assert "dokładnie 16 bajtów" in str(e.value)

# -----------------------
# parse_key – niepoprawne znaki hex
# -----------------------
def test_parse_key_invalid_hex():
    with pytest.raises(SystemExit) as e:
        utils.parse_key("00 11 22 33 44 55 66 77 88 99 GG BB CC DD EE FF")
    assert "nie jest poprawnym bajtem hex" in str(e.value)

# -----------------------
# parse_key – zły format w jednym ciągu
# -----------------------
def test_parse_key_invalid_hex_single_string():
    with pytest.raises(SystemExit) as e:
        utils.parse_key("00112233445566778899AABBCCDDEZZ")  # 'ZZ' nie jest hex
    assert "niepoprawne znaki hex" in str(e.value)

# -----------------------
# parse_key – prawidłowy przypadek
# -----------------------
def test_parse_key_valid_formats():
    key1 = utils.parse_key("00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF")
    key2 = utils.parse_key("00112233445566778899AABBCCDDEEFF")
    key3 = utils.parse_key("0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xAA,0xBB,0xCC,0xDD,0xEE,0xFF")
    assert key1 == key2 == key3
    assert len(key1) == 16
