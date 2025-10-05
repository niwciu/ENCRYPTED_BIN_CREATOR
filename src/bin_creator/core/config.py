"""Moduł konfiguracji – przechowuje i drukuje parametry wejściowe."""


class Config:
    """Reprezentuje zestaw parametrów wejściowych skryptu."""

    def __init__(
        self,
        input_path,
        output_path,
        device_id,
        bootloader_id,
        key,
        app_version,
        prev_app_version,
        page_length,
    ):
        self.input_path = input_path
        self.output_path = output_path
        self.device_id = device_id
        self.bootloader_id = bootloader_id
        self.key = key
        self.app_version = app_version
        self.prev_app_version = prev_app_version
        self.page_length = page_length

    @classmethod
    def from_args(cls, args):
        """Tworzy obiekt Config z parsowanych argumentów argparse."""
        return cls(
            args.input,
            args.output,
            args.device_id,
            args.bootloader_id,
            args.key,
            args.app_version,
            args.prev_app_version,
            args.page_length,
        )

    def print_summary(self):
        """Wypisuje zestaw aktualnych parametrów konfiguracyjnych."""
        print(f" Input file:          {self.input_path}")
        print(f" Output file:         {self.output_path}")
        print(f" Device ID:           {self.device_id} (0x{self.device_id:X})")
        print(f" Bootloader ID:       {self.bootloader_id} (0x{self.bootloader_id:X})")
        print(f" App version:         {self.app_version} (0x{self.app_version:X})")
        print(
            f" Previous app ver:    {self.prev_app_version} (0x{self.prev_app_version:X})"
        )
        print(f" Page length:         {self.page_length}")
        print(f" Key (hex):           {' '.join(f'{b:02X}' for b in self.key)}")
