"""Funkcje pomocnicze do parsowania wartości liczbowych i kluczy."""
import re
import sys
import os
from typing import Optional


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

    # wersja 1-częściowa: ciąg 32-znakowy (np. "001122...")
    if len(cleaned) == 1 and len(cleaned[0]) > 2:
        hex_str = cleaned[0].replace("0x", "").replace(" ", "")
        # spróbuj przekonwertować parami - złapiemy niepoprawne znaki
        try:
            bytes_list = [int(hex_str[i:i + 2], 16) for i in range(0, len(hex_str), 2)]
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
        sys.exit(f"Błąd: klucz musi mieć dokładnie 16 bajtów (podano {len(bytes_list)}).")

    return bytes(bytes_list)


def find_key_in_file(key_file_path: str, device_id: int) -> bytes:
    """
    Wyszukuje i zwraca 16-bajtowy klucz dla podanego device_id w pliku.
    Obsługiwane formaty linii:
      - <device_id>;<hex bytes separated by spaces>
      - <device_id> <key> (space or comma separated or single 32-char hex)
    Linie zaczynające się od '#' są ignorowane.
    Zwraca klucz jako bytes lub wywołuje sys.exit w przypadku błędu.
    """
    # sprawdź czy plik istnieje
    try:
        st = os.stat(key_file_path)
    except Exception as e:
        sys.exit(f"Błąd odczytu pliku kluczy: {e}")

    # opcjonalne ostrzeżenie o uprawnieniach (world-readable)
    if st.st_mode & 0o077:
        # plik ma jakieś prawa dla group/other
        print(f"Uwaga: plik z kluczami '{key_file_path}' ma prawa grupy/others (sprawdź uprawnienia).")

    try:
        with open(key_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        sys.exit(f"Błąd odczytu pliku kluczy: {e}")

    for raw in lines:
        # usuń komentarz i białe znaki z końca/ początku
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue

        # obsłuż format z ';' jako separator
        if ";" in line:
            left, right = line.split(";", 1)
            id_str = left.strip()
            key_part = right.strip()
            # key_part może być: "65 E6 21 F2 ..." albo "00112233..."
        else:
            # normalny split — obsłużymy spacje/komy
            parts = re.split(r'[\s,]+', line)
            if len(parts) < 2:
                # niepoprawna linia — ignorujemy (można też logować)
                continue
            id_str = parts[0]
            key_part = " ".join(parts[1:])

        # spróbuj sparsować device_id (hex lub dec)
        try:
            id_val = int(id_str, 0)
        except ValueError:
            # ignorujemy linie z niepoprawnym device id
            continue

        if id_val != device_id:
            continue

        # jeśli trafiliśmy — zamieniamy key_part na format akceptowany przez parse_key
        # key_part może być:
        #  - ciągiem 32-znakowym bez spacji -> zostawiamy jako jest
        #  - bajty rozdzielone spacjami (np. "65 E6 21 ...")
        #  - bajty z 0x prefixami lub przecinkami (parse_key obsłuży)
        key_candidate = key_part.strip()

        # use parse_key to validate/convert to bytes (parse_key wywoła sys.exit przy błędzie)
        key_bytes = parse_key(key_candidate)
        return key_bytes

    sys.exit(f"Błąd: nie znaleziono klucza dla device_id {hex(device_id)} w pliku '{key_file_path}'.")
