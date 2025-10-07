"""Helper functions for parsing numeric values and encryption keys."""

import re
import sys
import os


def parse_int(value, name, max_bits):
    """Converts a decimal/hex value to int and validates its range."""
    try:
        val = int(value, 0)
    except ValueError:
        sys.exit(f"Error: {name} must be a decimal or hexadecimal number (given: {value})")

    max_val = (1 << max_bits) - 1
    if not (0 <= val <= max_val):
        sys.exit(f"Error: {name} exceeds uint{max_bits} range ({val})")

    return val


def parse_key(value):
    """Parses a 16-byte hex key from various formats."""
    cleaned = re.split(r"[\s,]+", value.strip())
    bytes_list = []

    # Single continuous hex string (e.g. "001122...").
    if len(cleaned) == 1 and len(cleaned[0]) > 2:
        hex_str = cleaned[0].replace("0x", "").replace(" ", "")
        try:
            bytes_list = [int(hex_str[i : i + 2], 16) for i in range(0, len(hex_str), 2)]
        except Exception:
            sys.exit("Error: key contains invalid hex characters.")
    else:
        # List of bytes (e.g. "0x00", "11", "22", ...)
        for item in cleaned:
            if item:
                item = item.replace("0x", "")
                try:
                    val = int(item, 16)
                except ValueError:
                    sys.exit(f"Error: '{item}' is not a valid hex byte.")
                bytes_list.append(val)

    if len(bytes_list) != 16:
        sys.exit(f"Error: key must be exactly 16 bytes long (got {len(bytes_list)}).")

    return bytes(bytes_list)


def _read_key_file_lines(path: str) -> list[str]:
    """Reads lines from a key file, with error handling."""
    try:
        st = os.stat(path)
    except Exception as e:
        sys.exit(f"Error reading key file: {e}")

    if st.st_mode & 0o077:
        print(f"Warning: key file '{path}' has group/other permissions (check file security).")

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()
    except Exception as e:
        sys.exit(f"Error reading key file: {e}")


def _parse_key_line(line: str):
    """Parses a single key file line and returns (device_id, key_str) or None."""
    # Remove comments and whitespace
    line = line.split("#", 1)[0].strip()
    if not line:
        return None

    if ";" in line:
        left, right = line.split(";", 1)
        id_str, key_str = left.strip(), right.strip()
    else:
        parts = re.split(r"[\s,]+", line)
        if len(parts) < 2:
            return None
        id_str, key_str = parts[0], " ".join(parts[1:])

    # Try parsing device_id
    try:
        device_id = int(id_str, 0)
    except ValueError:
        return None

    return device_id, key_str.strip()


def find_key_in_file(key_file_path: str, device_id: int) -> bytes:
    """
    Searches for a 16-byte key for the given device_id in a key file.
    Supported formats:
      - <device_id>;<hex bytes>
      - <device_id> <hex bytes> (spaces, commas, or continuous 32-character string)
    Lines with comments (#) are ignored.
    """
    lines = _read_key_file_lines(key_file_path)

    for line in lines:
        parsed = _parse_key_line(line)
        if not parsed:
            continue

        parsed_id, key_str = parsed
        if parsed_id != device_id:
            continue

        # Validate and convert the key
        return parse_key(key_str)

    sys.exit(f"Error: could not find key for device_id {hex(device_id)} in file '{key_file_path}'.")
