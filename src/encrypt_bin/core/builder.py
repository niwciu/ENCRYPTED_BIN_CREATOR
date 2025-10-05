import os
import struct
import zlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


def pad_bytes(data: bytes, page_length: int) -> bytes:
    """Pads the data with zeros to make its length a multiple of page_length."""
    pad_len = (page_length - len(data) % page_length) % page_length
    return data + b"\x00" * pad_len


def encrypt_aes_cbc(input_bytes: bytes, key: bytes, iv: bytes) -> bytes:
    """Encrypts data using AES-128 CBC, compatible with Tiny-AES-C."""
    assert len(key) == 16
    assert len(iv) == 16
    assert len(input_bytes) % 16 == 0  # padding must ensure multiple of 16

    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(input_bytes)


def generate_bin(
    input_path: str,
    output_path: str,
    product_id: int,
    app_version: int,
    prev_app_version: int,
    bootloader_id: int,
    key: bytes,
    page_length: int = 2048,
):
    # 1. Read the entire input file
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file '{input_path}' does not exist.")

    with open(input_path, "rb") as f:
        input_bytes = f.read()

    # 2. Pad to a multiple of page_length
    input_bytes = pad_bytes(input_bytes, page_length)

    # 3. Generate random IV (16 bytes)
    iv = get_random_bytes(16)

    # 4. Encrypt with AES-128 CBC
    enc_bytes = encrypt_aes_cbc(input_bytes, key, iv)

    # 5. Compute CRC32 of the entire input (after padding)
    crc32_val = zlib.crc32(input_bytes) & 0xFFFFFFFF

    # 6. Write to the output file
    with open(output_path, "wb") as f:
        # Little Endian
        f.write(struct.pack("<I", bootloader_id))
        f.write(struct.pack("<I", (product_id >> 32) & 0xFFFFFFFF))  # MSB of product_id
        f.write(struct.pack("<I", product_id & 0xFFFFFFFF))  # LSB of product_id
        f.write(struct.pack("<I", app_version))
        f.write(struct.pack("<I", prev_app_version))
        num_pages = len(input_bytes) // page_length
        f.write(struct.pack("<I", num_pages))
        f.write(struct.pack("<I", page_length))
        f.write(iv)
        f.write(struct.pack("<I", crc32_val))
        f.write(enc_bytes)
