# tests/test_main.py
import sys
import pytest
from unittest.mock import patch
from bin_creator.__main__ import main

@pytest.mark.parametrize("argv", [
    [
        "-i", "tests/test_firmware.bin",
        "-o", "tests/out.bin",
        "-d", "0x12345678",
        "-b", "0x10",
        "-k", "00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF",
        "-v", "0x1201",
        "-p", "0x1100"
    ]
])
def test_main_runs(tmp_path, argv, monkeypatch):
    # Tworzymy plik wejściowy
    input_file = tmp_path / "test_firmware.bin"
    input_file.write_bytes(bytes(range(50)))
    output_file = tmp_path / "out.bin"

    # Zamieniamy ścieżki w argv
    argv[1] = str(input_file)
    argv[3] = str(output_file)
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)

    # Patchujemy print, żeby nie zaśmiecało terminala
    with patch("builtins.print") as mock_print:
        main()

    # Plik wyjściowy powinien istnieć
    assert output_file.exists()
