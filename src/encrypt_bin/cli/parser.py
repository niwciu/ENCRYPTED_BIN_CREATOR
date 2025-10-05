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
    """Returns a fully parsed and validated argparse.Namespace object."""
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument(
        "-r", "--requirements", help="Input parameters file (.txt)"
    )

    pre_args, remaining = base_parser.parse_known_args()

    file_args = []
    if pre_args.requirements:
        file_args = load_requirements_file(pre_args.requirements)

    merged_args = merge_args(file_args, remaining)

    parser = argparse.ArgumentParser(
        parents=[base_parser],
        description="Tool for handling binary files with device parameters.",
    )

    parser.add_argument(
        "-i", "--input", required=True, help="Path to input .bin file"
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to output .bin file"
    )
    parser.add_argument(
        "-d", "--device-id", required=True, help="Device ID (uint32, decimal or hex)"
    )
    parser.add_argument(
        "-b",
        "--bootloader-id",
        required=True,
        help="Bootloader ID (uint16, decimal or hex)",
    )

    # Use mutually exclusive group for key and key file
    key_group = parser.add_mutually_exclusive_group(required=True)
    key_group.add_argument(
        "-k", "--key", help="16-byte key in hex (if provided directly)"
    )
    key_group.add_argument(
        "-K",
        "--key-file",
        help="File with key map: device_id -> key (use when specifying a key directory)",
    )

    parser.add_argument(
        "-v",
        "--app-version",
        required=True,
        help="Application version (uint16, decimal or hex)",
    )
    parser.add_argument(
        "-p",
        "--prev-app-version",
        required=True,
        help="Previous application version (uint16, decimal or hex)",
    )
    parser.add_argument(
        "-l",
        "--page-length",
        default=2048,
        type=int,
        help="Page length (default: 2048)",
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
