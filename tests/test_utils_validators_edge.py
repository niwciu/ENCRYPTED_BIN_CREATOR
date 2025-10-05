import pytest
from bin_creator.cli import utils, validators
import tempfile
import os

# -----------------------
# parse_int - błędne wartości
# -----------------------
def test_parse_int_errors():
    # za duża liczba
    with pytest.raises(SystemExit):
        utils.parse_int("0x1FFFFFFFF", name="test_param", max_bits=32)
    # niepoprawny format
    with pytest.raises(SystemExit):
        utils.parse_int("notanumber", name="test_param", max_bits=32)

# -----------------------
# parse_key - błędne formaty
# -----------------------
def test_parse_key_errors():
    # zbyt krótki klucz
    with pytest.raises(SystemExit):
        utils.parse_key("00 11 22")
    # zbyt długi
    with pytest.raises(SystemExit):
        utils.parse_key("00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF 00")

# -----------------------
# validate_file_paths - wyjście nieistniejący katalog
# -----------------------
def test_validate_output_path(tmp_path):
    input_file = tmp_path / "in.bin"
    input_file.write_bytes(b"\x00")

    invalid_output = tmp_path / "nonexistent_dir" / "out.bin"
    with pytest.raises(SystemExit):
        validators.validate_file_paths(str(input_file), str(invalid_output))
