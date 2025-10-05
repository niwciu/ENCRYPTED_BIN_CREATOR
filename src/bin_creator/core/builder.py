import os
import struct
import zlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


def pad_bytes(data: bytes, page_length: int) -> bytes:
    """Dopasowuje długość danych do wielokrotności page_length zerami."""
    pad_len = (page_length - len(data) % page_length) % page_length
    return data + b"\x00" * pad_len


def encrypt_aes_cbc(input_bytes: bytes, key: bytes, iv: bytes) -> bytes:
    """Szyfruje dane AES-128 CBC, tak jak Tiny-AES-C."""
    assert len(key) == 16
    assert len(iv) == 16
    assert len(input_bytes) % 16 == 0  # padding musi zapewnić wielokrotność 16

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
    # 1. Wczytaj cały plik
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Plik '{input_path}' nie istnieje.")

    with open(input_path, "rb") as f:
        input_bytes = f.read()

    # 2. Padding do wielokrotności page_length
    input_bytes = pad_bytes(input_bytes, page_length)

    # 3. Generuj losowy IV (16 bajtów)
    iv = get_random_bytes(16)

    # 4. Szyfrujemy AES-128 CBC
    enc_bytes = encrypt_aes_cbc(input_bytes, key, iv)

    # 5. Oblicz CRC32 całego wejścia (po padzie)
    crc32_val = zlib.crc32(input_bytes) & 0xFFFFFFFF

    # 6. Zapis do pliku wyjściowego
    with open(output_path, "wb") as f:
        # Little Endian
        f.write(struct.pack("<I", bootloader_id))
        f.write(struct.pack("<I", (product_id >> 32) & 0xFFFFFFFF))  # MSB product_id
        f.write(struct.pack("<I", product_id & 0xFFFFFFFF))          # LSB product_id
        f.write(struct.pack("<I", app_version))
        f.write(struct.pack("<I", prev_app_version))
        num_pages = len(input_bytes) // page_length
        f.write(struct.pack("<I", num_pages))
        f.write(struct.pack("<I", page_length))
        f.write(iv)
        f.write(struct.pack("<I", crc32_val))
        f.write(enc_bytes)
