"""Funkcje walidujące ścieżki plików i katalogi."""
import os
import sys


def validate_file_paths(input_path, output_path):
    """Sprawdza istnienie pliku wejściowego i poprawność ścieżki wyjściowej."""
    if not os.path.isfile(input_path):
        sys.exit(f"Błąd: plik wejściowy '{input_path}' nie istnieje.")
    if not input_path.lower().endswith('.bin'):
        sys.exit("Błąd: plik wejściowy musi mieć rozszerzenie '.bin'.")

    output_dir = os.path.dirname(output_path) or "."
    if not os.path.exists(output_dir):
        sys.exit(f"Błąd: katalog wyjściowy '{output_dir}' nie istnieje.")
    if not output_path.lower().endswith('.bin'):
        sys.exit("Błąd: plik wyjściowy musi mieć rozszerzenie '.bin'.")
