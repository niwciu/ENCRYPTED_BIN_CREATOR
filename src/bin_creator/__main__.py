from bin_creator.cli.parser import get_parsed_args
from bin_creator.core.config import Config
from bin_creator.core.builder import generate_bin


def main():
    args = get_parsed_args()
    config = Config.from_args(args)

    print("Parametry wczytane poprawnie:")
    config.print_summary()

    # Generowanie pliku bin
    try:
        generate_bin(
            input_path=config.input_path,
            output_path=config.output_path,
            product_id=config.device_id,
            app_version=config.app_version,
            prev_app_version=config.prev_app_version,
            bootloader_id=config.bootloader_id,
            key=config.key,
            page_length=config.page_length,
        )
        print(f"\nPlik wyjściowy '{config.output_path}' wygenerowany pomyślnie.")
    except Exception as e:
        print(f"\nBłąd podczas generowania pliku: {e}")
