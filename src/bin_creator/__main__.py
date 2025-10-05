from bin_creator.cli.parser import get_parsed_args
from bin_creator.core.config import Config
from bin_creator.core.builder import generate_bin


def main():
    args = get_parsed_args()
    config = Config.from_args(args)

    print("Parameters loaded successfully:")
    config.print_summary()

    # Generate the binary file
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
        print(f"\nOutput file '{config.output_path}' generated successfully.")
    except Exception as e:
        print(f"\nError while generating the output file: {e}")
