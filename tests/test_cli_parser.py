import pytest
import sys
from unittest.mock import patch
from bin_creator.cli import parser
import os

# -----------------------
# load_requirements_file
# -----------------------


def test_load_requirements_file_success(tmp_path):
    """Poprawne wczytanie pliku requirements"""
    path = tmp_path / "params.txt"
    path.write_text("-i input.bin -o output.bin")
    args = parser.load_requirements_file(str(path))
    assert args == ["-i", "input.bin", "-o", "output.bin"]


def test_load_requirements_file_missing(tmp_path):
    """Nieistniejący plik -> SystemExit"""
    bad_file = tmp_path / "does_not_exist.txt"
    with pytest.raises(SystemExit) as e:
        parser.load_requirements_file(str(bad_file))
    assert "Błąd odczytu pliku requirements" in str(e.value)


def test_load_requirements_file_open_exception(monkeypatch):
    """Błąd przy otwieraniu pliku (np. brak uprawnień)"""
    with patch("builtins.open", side_effect=OSError("mocked error")):
        with pytest.raises(SystemExit) as e:
            parser.load_requirements_file("dummy.txt")
        assert "Błąd odczytu pliku requirements" in str(e.value)


def test_load_requirements_file_shlex_exception(tmp_path, monkeypatch):
    """Błąd parsowania w shlex.split"""
    path = tmp_path / "params.txt"
    path.write_text("-i input.bin -o output.bin")
    monkeypatch.setattr(
        "shlex.split", lambda *_a, **_k: (_ for _ in ()).throw(ValueError("mocked"))
    )
    with pytest.raises(SystemExit) as e:
        parser.load_requirements_file(str(path))
    assert "Błąd odczytu pliku requirements" in str(e.value)


# -----------------------
# merge_args
# -----------------------


def test_merge_args_basic():
    """Poprawne połączenie argumentów bez konfliktów"""
    file_args = ["-i", "file1.bin"]
    cli_args = ["-o", "file2.bin"]
    merged = parser.merge_args(file_args, cli_args)
    assert merged == ["-i", "file1.bin", "-o", "file2.bin"]


def test_merge_args_conflict():
    """Ten sam klucz z różnymi wartościami -> błąd"""
    file_args = ["-i", "file1.bin"]
    cli_args = ["-i", "file2.bin"]
    with pytest.raises(SystemExit) as e:
        parser.merge_args(file_args, cli_args)
    assert "flaga '-i' występuje w pliku i terminalu z różnymi wartościami" in str(
        e.value
    )


def test_merge_args_bad_syntax():
    """Brak flagi przed wartością -> błąd składni"""
    file_args = ["value_without_flag"]
    cli_args = []
    with pytest.raises(SystemExit) as e:
        parser.merge_args(file_args, cli_args)
    assert "niepoprawna składnia parametrów" in str(e.value)


# -----------------------
# get_parsed_args
# -----------------------


def make_bin_file(tmp_path, name="in.bin"):
    f = tmp_path / name
    f.write_bytes(b"\x00" * 16)
    return f


def test_get_parsed_args_with_key(monkeypatch, tmp_path):
    """Podanie bezpośredniego klucza przez -k"""
    inp = make_bin_file(tmp_path, "input.bin")
    out = tmp_path / "output.bin"
    argv = [
        "-i",
        str(inp),
        "-o",
        str(out),
        "-d",
        "0x1234",
        "-b",
        "0x10",
        "-k",
        "00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF",
        "-v",
        "0x1201",
        "-p",
        "0x1100",
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    args = parser.get_parsed_args()

    assert args.device_id == 0x1234
    assert isinstance(args.key, bytes)
    assert len(args.key) == 16


def test_get_parsed_args_with_key_file(monkeypatch, tmp_path):
    """Podanie klucza przez -K i wyszukiwanie w pliku"""
    inp = make_bin_file(tmp_path, "input.bin")
    out = tmp_path / "output.bin"
    key_file = tmp_path / "keys.txt"
    key_file.write_text("0x1234;00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF")

    argv = [
        "-i",
        str(inp),
        "-o",
        str(out),
        "-d",
        "0x1234",
        "-b",
        "0x10",
        "-K",
        str(key_file),
        "-v",
        "0x1201",
        "-p",
        "0x1100",
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    args = parser.get_parsed_args()
    assert isinstance(args.key, bytes)
    assert len(args.key) == 16


def test_get_parsed_args_with_requirements(monkeypatch, tmp_path):
    """Pokrywa ścieżkę if pre_args.requirements"""
    inp = make_bin_file(tmp_path)
    out = tmp_path / "output.bin"
    req_file = tmp_path / "params.txt"
    req_file.write_text(
        f"-i {inp} -o {out} -d 0x1234 -b 0x10 -k 00112233445566778899AABBCCDDEEFF -v 0x1201 -p 0x1100"
    )
    monkeypatch.setattr(sys, "argv", ["prog", "-r", str(req_file)])

    args = parser.get_parsed_args()
    assert args.device_id == 0x1234
    assert isinstance(args.key, bytes)
    assert len(args.key) == 16


def test_get_parsed_args_invalid_input(monkeypatch, tmp_path):
    """Nieistniejący plik wejściowy"""
    inp = tmp_path / "missing.bin"
    out = tmp_path / "output.bin"
    argv = [
        "-i",
        str(inp),
        "-o",
        str(out),
        "-d",
        "0x1",
        "-b",
        "0x2",
        "-k",
        "00" * 16,
        "-v",
        "1",
        "-p",
        "1",
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    with pytest.raises(SystemExit) as e:
        parser.get_parsed_args()
    assert "plik wejściowy" in str(e.value)


def test_get_parsed_args_invalid_output(monkeypatch, tmp_path):
    """Nieistniejący katalog dla pliku wyjściowego"""
    inp = make_bin_file(tmp_path)
    out = tmp_path / "no_dir" / "out.bin"
    argv = [
        "-i",
        str(inp),
        "-o",
        str(out),
        "-d",
        "1",
        "-b",
        "2",
        "-k",
        "00" * 16,
        "-v",
        "1",
        "-p",
        "1",
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    with pytest.raises(SystemExit) as e:
        parser.get_parsed_args()
    assert "katalog wyjściowy" in str(e.value)


def test_get_parsed_args_invalid_number(monkeypatch, tmp_path):
    """Niepoprawny Device ID"""
    inp = make_bin_file(tmp_path)
    out = tmp_path / "output.bin"
    argv = [
        "-i",
        str(inp),
        "-o",
        str(out),
        "-d",
        "BAD",
        "-b",
        "0x10",
        "-k",
        "00" * 16,
        "-v",
        "0x1201",
        "-p",
        "0x1100",
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    with pytest.raises(SystemExit) as e:
        parser.get_parsed_args()
    assert "Device ID" in str(e.value)


def test_get_parsed_args_invalid_key(monkeypatch, tmp_path):
    """Niepoprawny klucz (za krótki)"""
    inp = make_bin_file(tmp_path)
    out = tmp_path / "output.bin"
    argv = [
        "-i",
        str(inp),
        "-o",
        str(out),
        "-d",
        "0x1234",
        "-b",
        "0x10",
        "-k",
        "00",
        "-v",
        "0x1201",
        "-p",
        "0x1100",
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    with pytest.raises(SystemExit):
        parser.get_parsed_args()


def test_get_parsed_args_missing_key(monkeypatch, tmp_path):
    """Brak zarówno -k jak i -K"""
    inp = make_bin_file(tmp_path)
    out = tmp_path / "output.bin"
    argv = [
        "-i",
        str(inp),
        "-o",
        str(out),
        "-d",
        "0x1234",
        "-b",
        "0x10",
        "-v",
        "0x1201",
        "-p",
        "0x1100",
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    with pytest.raises(SystemExit):
        parser.get_parsed_args()
