import pytest
import os
from bin_creator.core.builder import generate_bin

def test_generate_bin(tmp_path):
    # Pliki tymczasowe
    input_file = tmp_path / "firmware.bin"
    output_file = tmp_path / "out.bin"

    # Tworzymy testowy input (50 bajtów)
    input_file.write_bytes(bytes(range(50)))

    # Klucz 16-bajtowy
    key = bytes(range(16))

    # Wywołanie generate_bin
    generate_bin(
        input_path=str(input_file),
        output_path=str(output_file),
        product_id=0x12345678ABCDEF00,
        app_version=0x1201,
        prev_app_version=0x1100,
        bootloader_id=0x10,
        key=key,
        page_length=16  # mała strona dla testu
    )

    # Sprawdzenie czy plik wyjściowy powstał
    assert output_file.exists()
    out_data = output_file.read_bytes()

    # Nagłówek powinien mieć:
    # 4 (bootloader) + 4 + 4 (product id) + 4 + 4 (app versions) + 4 + 4 (page_length) + 16 (iv) + 4 (crc) = 48 bajtów
    header_len = 4 + 4 + 4 + 4 + 4 + 4 + 4 + 16 + 4
    assert len(out_data) > header_len  # szyfrowany payload powinien być większy niż nagłówek

    # Liczba stron w nagłówku (offset 20) = len(input_padded) // page_length
    num_pages = int.from_bytes(out_data[20:24], "little")
    padded_len = ((50 + 16 - 1) // 16) * 16
    expected_pages = padded_len // 16
    assert num_pages == expected_pages
