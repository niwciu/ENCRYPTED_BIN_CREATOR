"""Funkcje pomocnicze do parsowania wartości liczbowych i kluczy."""

import re
import sys
import os

# from typing import Optional


def parse_int(value, name, max_bits):
    """Konwertuje wartość dec/hex na int i sprawdza zakres."""
    try:
        val = int(value, 0)
    except ValueError:
        sys.exit(
            f"Błąd: {name} musi być liczbą dziesiętną lub szesnastkową (podano: {value})"
        )

    max_val = (1 << max_bits) - 1
    if not (0 <= val <= max_val):
        sys.exit(f"Błąd: {name} przekracza zakres uint{max_bits} ({val})")

    return val


def parse_key(value):
    """Parsuje 16-bajtowy klucz hex z różnych formatów."""
    cleaned = re.split(r"[\s,]+", value.strip())
    bytes_list = []

    # wersja 1-częściowa: ciąg 32-znakowy (np. "001122...")
    if len(cleaned) == 1 and len(cleaned[0]) > 2:
        hex_str = cleaned[0].replace("0x", "").replace(" ", "")
        # spróbuj przekonwertować parami - złapiemy niepoprawne znaki
        try:
            bytes_list = [
                int(hex_str[i : i + 2], 16) for i in range(0, len(hex_str), 2)
            ]
        except Exception:
            sys.exit("Błąd: klucz zawiera niepoprawne znaki hex.")
    else:
        # lista elementów (np. "0x00", "11", "22", ...)
        for item in cleaned:
            if item:
                item = item.replace("0x", "")
                try:
                    val = int(item, 16)
                except ValueError:
                    sys.exit(f"Błąd: '{item}' nie jest poprawnym bajtem hex.")
                bytes_list.append(val)

    if len(bytes_list) != 16:
        sys.exit(
            f"Błąd: klucz musi mieć dokładnie 16 bajtów (podano {len(bytes_list)})."
        )

    return bytes(bytes_list)


def _read_key_file_lines(path: str) -> list[str]:
    """Odczytuje linie z pliku kluczy, z obsługą błędów."""
    try:
        st = os.stat(path)
    except Exception as e:
        sys.exit(f"Błąd odczytu pliku kluczy: {e}")

    if st.st_mode & 0o077:
        print(
            f"Uwaga: plik z kluczami '{path}' ma prawa grupy/others (sprawdź uprawnienia)."
        )

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()
    except Exception as e:
        sys.exit(f"Błąd odczytu pliku kluczy: {e}")


def _parse_key_line(line: str):
    """Parsuje pojedynczą linię pliku kluczy i zwraca (device_id, key_str) lub None."""
    # usuń komentarze i białe znaki
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

    # spróbuj sparsować device_id
    try:
        device_id = int(id_str, 0)
    except ValueError:
        return None

    return device_id, key_str.strip()


def find_key_in_file(key_file_path: str, device_id: int) -> bytes:
    """
    Szuka 16-bajtowego klucza dla danego device_id w pliku.
    Obsługuje formaty:
      - <device_id>;<hex bytes>
      - <device_id> <hex bytes> (spacje, przecinki lub ciąg 32-znakowy)
    Linie z komentarzami (#) są ignorowane.
    """
    lines = _read_key_file_lines(key_file_path)

    for line in lines:
        parsed = _parse_key_line(line)
        if not parsed:
            continue

        parsed_id, key_str = parsed
        if parsed_id != device_id:
            continue

        # Walidacja i konwersja klucza
        return parse_key(key_str)

    sys.exit(
        f"Błąd: nie znaleziono klucza dla device_id {hex(device_id)} w pliku '{key_file_path}'."
    )
