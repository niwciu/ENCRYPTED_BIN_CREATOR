import sys
import pytest
from unittest.mock import patch
from bin_creator.__main__ import main

def test_main_handles_missing_input_file(tmp_path, monkeypatch):
    output_file = tmp_path / "out.bin"
    missing_input = tmp_path / "missing.bin"

    argv = [
        "-i", str(missing_input),
        "-o", str(output_file),
        "-d", "0x1234",
        "-b", "0x10",
        "-k", "00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF",
        "-v", "0x1201",
        "-p", "0x1100"
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)

    # Spodziewamy się, że main wywoła sys.exit
    with pytest.raises(SystemExit) as e:
        main()

    # Opcjonalnie sprawdzamy komunikat
    assert "plik wejściowy" in str(e.value)
