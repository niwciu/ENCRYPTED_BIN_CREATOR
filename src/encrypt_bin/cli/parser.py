"""Module for handling CLI arguments and requirements file."""

import argparse
import sys
import shlex
from encrypt_bin.cli.validators import validate_file_paths
from encrypt_bin.cli.utils import parse_int, parse_key, find_key_in_file


def load_requirements_file(path):
    """Loads and parses a requirements file (e.g., params.txt)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        args = shlex.split(content, comments=True)
    except Exception as e:
        sys.exit(f"Error reading requirements file: {e}")
    return args


def merge_args(file_args, cli_args):
    """Merges arguments from the requirements file and CLI.
    If the same flag appears with different values, the program exits with an error.
    """

    def args_to_dict(args_list):
        d = {}
        key = None
        for arg in args_list:
            if arg.startswith("-"):
                key = arg
                d[key] = None
            else:
                if key is None:
                    sys.exit(f"Error: invalid parameter syntax ({arg})")
                d[key] = arg
                key = None
        return d

    file_dict = args_to_dict(file_args)
    cli_dict = args_to_dict(cli_args)

    for flag in file_dict:
        if flag in cli_dict and file_dict[flag] != cli_dict[flag]:
            sys.exit(
                f"Error: flag '{flag}' appears in both file and CLI with different values:\n"
                f" - from file:     {file_dict[flag]}\n"
                f" - from terminal: {cli_dict[flag]}"
            )

    merged = file_args + [item for item in cli_args if item not in file_args]
    return merged


def get_parsed_args():
    """Parse and validate all CLI arguments."""

    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument(
        "-c", "--config",
        metavar="FILE",
        help=(
            "Optional configuration file (.txt) containing CLI arguments.\n"
            "Each line should contain a valid flag, e.g.:\n"
            "    -i input.bin\n"
            "    -o output.bin\n"
            "    -d 0x1234567812345678\n"
            "    ...\n"
        )
    )

    pre_args, remaining = base_parser.parse_known_args()

    file_args = []
    if pre_args.config:
        file_args = load_requirements_file(pre_args.config)

    merged_args = merge_args(file_args, remaining)

    parser = argparse.ArgumentParser(
        parents=[base_parser],
        description="Encrypts and packages binary files for device firmware updates.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-i", "--input",
        required=True,
        metavar="FILE",
        help="Full path to the input .bin file (including filename, e.g. ./input/firmware.bin)"
    )

    parser.add_argument(
        "-o", "--output",
        required=True,
        metavar="FILE",
        help="Full path for the generated .bin file (e.g. ./output/encrypted.bin)"
    )
    parser.add_argument(
        "-d", "--device-id", required=True,
        metavar="ID",
        help="Device ID (uint64, decimal or hex, e.g. 0x0000123412341234)"
    )
    parser.add_argument(
        "-b", "--bootloader-id", required=True,
        metavar="ID",
        help="Bootloader ID (uint16, decimal or hex, e.g. 0x00001234)"
    )

    # Key group
    key_group = parser.add_mutually_exclusive_group(required=True)
    key_group.add_argument(
        "-k", "--key",
        metavar="HEX",
        help=(
            "16-byte encryption key as hexadecimal values.\n"
            "Formats accepted:\n"
            "  '00 11 22 33 ... FF'\n"
            "  '00112233445566778899AABBCCDDEEFF'\n"
            "  '0x00,0x11,...,0xFF'"
        )
    )
    key_group.add_argument(
        "-K", "--key-file",
        metavar="FILE",
        help="Path to a key mapping file containing pairs: device_id;key"
        "The script automatically looks up and uses the key matching the provided --device-id flag argument."
    )

    parser.add_argument(
        "-v", "--app-version", required=True,
        metavar="VER",
        help="Application version (uint32, decimal or hex, e.g. 0x20250103)"
    )
    parser.add_argument(
        "-p", "--prev-app-version", required=True,
        metavar="VER",
        help="Previous application version (uint32, decimal or hex, e.g. 0x20241231)"
    )
    parser.add_argument(
        "-l", "--page-length", default=2048, type=int,
        metavar="BYTES",
        help="Flash page size in bytes. Defines the size of a Flash memory page in the target microcontroller. (default: 2048)"
    )

    args = parser.parse_args(merged_args)

    # Validate file paths
    validate_file_paths(args.input, args.output)

    # Parse integers (device_id first — may be needed to locate the key)
    args.device_id = parse_int(args.device_id, "Device ID", 64)
    args.bootloader_id = parse_int(args.bootloader_id, "Bootloader ID", 32)
    args.app_version = parse_int(args.app_version, "App version", 32)
    args.prev_app_version = parse_int(args.prev_app_version, "Previous app version", 32)

    # Parse the key: use --key-file if provided, otherwise parse --key
    if getattr(args, "key_file", None):
        # find_key_in_file returns bytes or calls sys.exit on failure
        args.key = find_key_in_file(args.key_file, args.device_id)
    else:
        # parse_key returns bytes or calls sys.exit on failure
        args.key = parse_key(args.key)

    return args
