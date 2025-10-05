import pytest
from unittest.mock import patch, mock_open
import pytest
import stat
from bin_creator.cli import utils, validators
from bin_creator.cli.utils import find_key_in_file


# -----------------------
# parse_int
# -----------------------
@pytest.mark.parametrize("value, expected", [
    ("42", 42),
    ("0x10", 16),
])
def test_parse_int_valid(value, expected):
    assert utils.parse_int(value, name="test_param", max_bits=32) == expected


@pytest.mark.parametrize("value", [
    "0x1FFFFFFFF",  # za duża liczba
    "notanumber",   # niepoprawny format
])
def test_parse_int_invalid(value):
    with pytest.raises(SystemExit):
        utils.parse_int(value, name="test_param", max_bits=32)


# -----------------------
# parse_key
# -----------------------
@pytest.mark.parametrize("key_str", [
    "00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF",
    "00112233445566778899AABBCCDDEEFF",
    "0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xAA,0xBB,0xCC,0xDD,0xEE,0xFF",
])
def test_parse_key_valid(key_str):
    key = utils.parse_key(key_str)
    assert isinstance(key, bytes)
    assert len(key) == 16


@pytest.mark.parametrize("key_str, msg", [
    ("00112233", "dokładnie 16 bajtów"),  # za krótki
    ("00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF 00", "dokładnie 16 bajtów"),  # za długi
    ("00 11 22 33 44 55 66 77 88 99 GG BB CC DD EE FF", "nie jest poprawnym bajtem hex"),
    ("00112233445566778899AABBCCDDEZZ", "niepoprawne znaki hex"),  # 32 znaki, ostatnie ZZ niepoprawne
])
def test_parse_key_invalid(key_str, msg):
    with pytest.raises(SystemExit) as e:
        utils.parse_key(key_str)
    assert msg in str(e.value)


# -----------------------
# validate_file_paths
# -----------------------
def test_validate_file_paths(tmp_path):
    input_file = tmp_path / "in.bin"
    input_file.write_bytes(b"\x00")
    output_file = tmp_path / "out.bin"

    # poprawny przypadek
    validators.validate_file_paths(str(input_file), str(output_file))

    # brak input_file -> SystemExit
    with pytest.raises(SystemExit):
        validators.validate_file_paths(str(tmp_path / "missing.bin"), str(output_file))

    # nieistniejący katalog dla output -> SystemExit
    invalid_output = tmp_path / "nonexistent_dir" / "out.bin"
    with pytest.raises(SystemExit):
        validators.validate_file_paths(str(input_file), str(invalid_output))


# -----------------------
# find_key_in_file
# -----------------------
def test_find_key_in_file_various_formats(tmp_path, capsys):
    content = (
        "\n"  # pusty wiersz
        "# komentarz\n"
        "BADLINE\n"  # mniej niż 2 elementy po split
        "0xZZZZ;00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF\n"  # invalid device_id
        "0x1234;00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF\n"  # poprawna linia
        "0x5678 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF 00\n"  # format space-separated
    )
    key_file = tmp_path / "keys.txt"
    key_file.write_text(content)
    key_file.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)  # world-readable

    # powinniśmy znaleźć key dla device_id 0x1234
    key = utils.find_key_in_file(str(key_file), 0x1234)
    captured = capsys.readouterr()
    assert len(key) == 16
    assert "Uwaga: plik z kluczami" in captured.out

    # znajdź key w formacie space-separated
    key2 = utils.find_key_in_file(str(key_file), 0x5678)
    assert len(key2) == 16

    # brak pasującego device_id
    with pytest.raises(SystemExit) as e:
        utils.find_key_in_file(str(key_file), 0x9999)
    assert "nie znaleziono klucza" in str(e.value)

    # brak pliku
    with pytest.raises(SystemExit) as e:
        utils.find_key_in_file(str(tmp_path / "missing.txt"), 0x1234)
    assert "Błąd odczytu pliku kluczy" in str(e.value)



def test_find_key_in_file_open_exception(tmp_path):
    key_file = tmp_path / "keys.txt"
    key_file.write_text("0x1234;00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF")

    # Patchujemy open, żeby rzucał OSError
    with patch("builtins.open", side_effect=OSError("mocked error")):
        with pytest.raises(SystemExit) as e:
            utils.find_key_in_file(str(key_file), 0x1234)
        assert "Błąd odczytu pliku kluczy: mocked error" in str(e.value)




# -----------------------
# parse_int
# -----------------------
@pytest.mark.parametrize("value, expected", [
    ("42", 42),
    ("0x10", 16),
])
def test_parse_int_valid(value, expected):
    assert utils.parse_int(value, name="test_param", max_bits=32) == expected

@pytest.mark.parametrize("value", [
    "0x1FFFFFFFF",  # przekroczenie bitów
    "notanumber",   # niepoprawny format
])
def test_parse_int_invalid(value):
    with pytest.raises(SystemExit):
        utils.parse_int(value, name="test_param", max_bits=32)


# -----------------------
# parse_key
# -----------------------
@pytest.mark.parametrize("key_str", [
    "00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF",
    "00112233445566778899AABBCCDDEEFF",
    "0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xAA,0xBB,0xCC,0xDD,0xEE,0xFF",
])
def test_parse_key_valid(key_str):
    key = utils.parse_key(key_str)
    assert isinstance(key, bytes)
    assert len(key) == 16

@pytest.mark.parametrize("key_str, msg", [
    ("00112233", "dokładnie 16 bajtów"),  # za krótki
    ("00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF 00", "dokładnie 16 bajtów"),  # za długi
    ("00 11 22 33 44 55 66 77 88 99 GG BB CC DD EE FF", "nie jest poprawnym bajtem hex"),
    ("00112233445566778899AABBCCDDEZZ", "niepoprawne znaki hex"),
])
def test_parse_key_invalid(key_str, msg):
    with pytest.raises(SystemExit) as e:
        utils.parse_key(key_str)
    assert msg in str(e.value)

