"""Funkcje pomocnicze do parsowania wartości liczbowych i kluczy."""
import re
import sys


def parse_int(value, name, max_bits):
    """Konwertuje wartość dec/hex na int i sprawdza zakres."""
    try:
        val = int(value, 0)
    except ValueError:
        sys.exit(f"Błąd: {name} musi być liczbą dziesiętną lub szesnastkową (podano: {value})")

    max_val = (1 << max_bits) - 1
    if not (0 <= val <= max_val):
        sys.exit(f"Błąd: {name} przekracza zakres uint{max_bits} ({val})")

    return val


def parse_key(value):
    """Parsuje 16-bajtowy klucz hex z różnych formatów."""
    cleaned = re.split(r'[\s,]+', value.strip())
    bytes_list = []

    if len(cleaned) == 1 and len(cleaned[0]) > 2:
        hex_str = cleaned[0].replace("0x", "").replace(" ", "")
        try:
            bytes_list = [int(hex_str[i:i + 2], 16) for i in range(0, len(hex_str), 2)]
        except ValueError:
            sys.exit("Błąd: klucz zawiera niepoprawne znaki hex.")
        if len(bytes_list) != 16:
            sys.exit("Błąd: klucz musi mieć dokładnie 16 bajtów (32 znaki hex).")

    else:
        for item in cleaned:
            if item:
                item = item.replace("0x", "")
                try:
                    val = int(item, 16)
                except ValueError:
                    sys.exit(f"Błąd: '{item}' nie jest poprawnym bajtem hex.")
                bytes_list.append(val)

    if len(bytes_list) != 16:
        sys.exit(f"Błąd: klucz musi mieć dokładnie 16 bajtów (podano {len(bytes_list)}).")

    return bytes(bytes_list)
