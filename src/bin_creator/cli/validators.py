"""Functions for validating file paths and directories."""

import os
import sys


def validate_file_paths(input_path, output_path):
    """Checks the existence of the input file and validity of the output path."""
    if not os.path.isfile(input_path):
        sys.exit(f"Error: input file '{input_path}' does not exist.")
    if not input_path.lower().endswith(".bin"):
        sys.exit("Error: input file must have the '.bin' extension.")

    output_dir = os.path.dirname(output_path) or "."
    if not os.path.exists(output_dir):
        sys.exit(f"Error: output directory '{output_dir}' does not exist.")
    if not output_path.lower().endswith(".bin"):
        sys.exit("Error: output file must have the '.bin' extension.")
