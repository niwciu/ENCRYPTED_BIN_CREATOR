from bin_creator.cli.parser import get_parsed_args
from bin_creator.cli import parser
import sys
import pytest
import tempfile
import os

def test_required_flags(monkeypatch, tmp_path):
    # Tworzymy tymczasowy plik bin
    input_file = tmp_path / "firmware.bin"
    input_file.write_bytes(b"\x00" * 16)  # np. 16 bajtów

    output_file = tmp_path / "out.bin"

    argv = [
        "-i", str(input_file),
        "-o", str(output_file),
        "-d", "0x1234",
        "-b", "0x10",
        "-k", "00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF",
        "-v", "0x1201",
        "-p", "0x1100"
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    args = get_parsed_args()

    assert args.device_id == 0x1234
    assert args.bootloader_id == 0x10
    assert isinstance(args.key, bytes)
    assert len(args.key) == 16



def test_load_requirements_file_error(tmp_path):
    bad_file = tmp_path / "does_not_exist.txt"
    with pytest.raises(SystemExit) as e:
        parser.load_requirements_file(str(bad_file))
    assert "Błąd odczytu pliku requirements" in str(e.value)

def test_args_to_dict_syntax_error():
    file_args = ["value_without_flag"]
    cli_args = []
    with pytest.raises(SystemExit) as e:
        parser.merge_args(file_args, cli_args)
    assert "niepoprawna składnia parametrów" in str(e.value)

def test_merge_args_conflict():
    file_args = ["-i", "file1.bin"]
    cli_args = ["-i", "file2.bin"]
    with pytest.raises(SystemExit) as e:
        parser.merge_args(file_args, cli_args)
    assert "flaga '-i' występuje w pliku i terminalu z różnymi wartościami" in str(e.value)

def test_load_requirements_file_exception(tmp_path):
    bad_file = tmp_path / "nonexistent.txt"
    with pytest.raises(SystemExit) as e:
        from bin_creator.cli import parser
        parser.load_requirements_file(str(bad_file))
    assert "Błąd odczytu pliku requirements" in str(e.value)

def test_validate_file_paths_system_exit(tmp_path):
    from bin_creator.cli import validators
    input_file = tmp_path / "missing.bin"
    output_file = tmp_path / "out.bin"
    import pytest
    with pytest.raises(SystemExit) as e:
        validators.validate_file_paths(str(input_file), str(output_file))
    assert "plik wejściowy" in str(e.value)
