import pytest
import os
from encrypt_bin.core.builder import generate_bin
from encrypt_bin.cli import parser


def test_generate_bin(tmp_path):
    # Temporary files
    input_file = tmp_path / "firmware.bin"
    output_file = tmp_path / "out.bin"

    # Create test input (50 bytes)
    input_file.write_bytes(bytes(range(50)))

    # 16-byte key
    key = bytes(range(16))

    # Call generate_bin
    generate_bin(
        input_path=str(input_file),
        output_path=str(output_file),
        product_id=0x12345678ABCDEF00,
        app_version=0x1201,
        prev_app_version=0x1100,
        bootloader_id=0x10,
        key=key,
        page_length=16,  # small page for test
    )

    # Check if output file exists
    assert output_file.exists()
    out_data = output_file.read_bytes()

    # Header length: 4+4+4+4+4+4+4+16+4 = 48 bytes
    header_len = 4 + 4 + 4 + 4 + 4 + 4 + 4 + 16 + 4
    assert len(out_data) > header_len  # encrypted payload should be larger than header

    # Number of pages in header (offset 20)
    num_pages = int.from_bytes(out_data[20:24], "little")
    padded_len = ((50 + 16 - 1) // 16) * 16
    expected_pages = padded_len // 16
    assert num_pages == expected_pages


def test_generate_bin_input_file_missing(tmp_path):
    input_file = tmp_path / "missing.bin"
    output_file = tmp_path / "out.bin"
    key = bytes(range(16))

    with pytest.raises(FileNotFoundError) as e:
        generate_bin(
            input_path=str(input_file),
            output_path=str(output_file),
            product_id=0x12345678ABCDEF00,
            app_version=0x1201,
            prev_app_version=0x1100,
            bootloader_id=0x10,
            key=key,
            page_length=16,
        )
    assert "does not exist" in str(e.value)


def test_load_requirements_file_success(tmp_path):
    # Create temporary file with valid arguments
    path = tmp_path / "params.txt"
    path.write_text("-i input.bin -o output.bin")

    args = parser.load_requirements_file(str(path))

    assert args == ["-i", "input.bin", "-o", "output.bin"]
