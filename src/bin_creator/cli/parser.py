"""Moduł obsługi argumentów CLI i pliku requirements."""
import argparse
import sys
import shlex
from bin_creator.cli.validators import validate_file_paths
from bin_creator.cli.utils import parse_int, parse_key


def load_requirements_file(path):
    """Wczytuje i parsuje plik z argumentami (np. params.txt)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        args = shlex.split(content, comments=True)
    except Exception as e:
        sys.exit(f"Błąd odczytu pliku requirements: {e}")
    return args


def merge_args(file_args, cli_args):
    """Łączy argumenty z pliku i CLI. W przypadku konfliktu z różnymi wartościami -> błąd."""
    def args_to_dict(args_list):
        d = {}
        key = None
        for arg in args_list:
            if arg.startswith('-'):
                key = arg
                d[key] = None
            else:
                if key is None:
                    sys.exit(f"Błąd: niepoprawna składnia parametrów ({arg})")
                d[key] = arg
                key = None
        return d

    file_dict = args_to_dict(file_args)
    cli_dict = args_to_dict(cli_args)

    for flag in file_dict:
        if flag in cli_dict and file_dict[flag] != cli_dict[flag]:
            sys.exit(
                f"Błąd: flaga '{flag}' występuje w pliku i terminalu z różnymi wartościami:\n"
                f" - z pliku:     {file_dict[flag]}\n"
                f" - z terminala: {cli_dict[flag]}"
            )

    merged = file_args + [item for item in cli_args if item not in file_args]
    return merged


def get_parsed_args():
    """Zwraca gotowy obiekt argparse.Namespace z parsowanymi i zweryfikowanymi wartościami."""
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument("-r", "--requirements", help="Plik z parametrami wejściowymi (.txt)")

    pre_args, remaining = base_parser.parse_known_args()

    file_args = []
    if pre_args.requirements:
        file_args = load_requirements_file(pre_args.requirements)

    merged_args = merge_args(file_args, remaining)

    parser = argparse.ArgumentParser(
        parents=[base_parser],
        description="Skrypt do obsługi plików binarnych z parametrami urządzenia."
    )

    parser.add_argument("-i", "--input", required=True, help="Ścieżka do pliku wejściowego .bin")
    parser.add_argument("-o", "--output", required=True, help="Ścieżka do pliku wyjściowego .bin")
    parser.add_argument("-d", "--device-id", required=True, help="Device ID (uint32, dec lub hex)")
    parser.add_argument("-b", "--bootloader-id", required=True, help="Bootloader ID (uint16, dec lub hex)")
    parser.add_argument("-k", "--key", required=True, help="Klucz 16 bajtów w hex")
    parser.add_argument("-v", "--app-version", required=True, help="Wersja aplikacji (uint16, dec lub hex)")
    parser.add_argument("-p", "--prev-app-version", required=True, help="Poprzednia wersja aplikacji (uint16, dec lub hex)")
    parser.add_argument("-l", "--page-length", default=2048, type=int, help="Długość strony (domyślnie 2048)")

    args = parser.parse_args(merged_args)

    # Walidacja ścieżek
    validate_file_paths(args.input, args.output)

    # Parsowanie liczb i klucza
    args.device_id = parse_int(args.device_id, "Device ID", 32)
    args.bootloader_id = parse_int(args.bootloader_id, "Bootloader ID", 16)
    args.app_version = parse_int(args.app_version, "App version", 16)
    args.prev_app_version = parse_int(args.prev_app_version, "Previous app version", 16)
    args.key = parse_key(args.key)

    return args
