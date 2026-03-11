"""GUI module for the encrypt-bin application."""

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QComboBox,
    QGroupBox,
    QMessageBox,
    QTextEdit,
)

# from PyQt6.QtCore import Qt
import sys

# import os
from encrypt_bin.cli.parser import get_parsed_args
from encrypt_bin.core.config import Config
from encrypt_bin.core.builder import generate_bin


class EncryptBinGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Encrypt Bin Creator")
        self.setGeometry(100, 100, 600, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Input file
        input_group = QGroupBox("Input File")
        input_layout = QHBoxLayout(input_group)
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Select input .bin file")
        input_button = QPushButton("Browse...")
        input_button.clicked.connect(self.select_input_file)
        input_layout.addWidget(QLabel("Input:"))
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_button)
        layout.addWidget(input_group)

        # Output file
        output_group = QGroupBox("Output File")
        output_layout = QHBoxLayout(output_group)
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Select output .bin file")
        output_button = QPushButton("Browse...")
        output_button.clicked.connect(self.select_output_file)
        output_layout.addWidget(QLabel("Output:"))
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_button)
        layout.addWidget(output_group)

        # Device ID
        device_group = QGroupBox("Device ID")
        device_layout = QHBoxLayout(device_group)
        self.device_edit = QLineEdit()
        self.device_edit.setPlaceholderText("e.g. 0x00A0000BC22510E1")
        device_layout.addWidget(QLabel("Device ID (hex):"))
        device_layout.addWidget(self.device_edit)
        layout.addWidget(device_group)

        # Bootloader ID
        bootloader_group = QGroupBox("Bootloader ID")
        bootloader_layout = QHBoxLayout(bootloader_group)
        self.bootloader_edit = QLineEdit()
        self.bootloader_edit.setPlaceholderText("e.g. 0x00001001")
        bootloader_layout.addWidget(QLabel("Bootloader ID (hex):"))
        bootloader_layout.addWidget(self.bootloader_edit)
        layout.addWidget(bootloader_group)

        # Key selection (provide either hex key or key file; the alternative field is cleared automatically)
        key_group = QGroupBox("Encryption Key (hex or file)")
        key_layout = QVBoxLayout(key_group)
        # hint
        key_layout.addWidget(QLabel("Enter a hex key or choose a key file."))

        # Hex key input
        hex_layout = QHBoxLayout()
        self.hex_key_edit = QLineEdit()
        self.hex_key_edit.setPlaceholderText("e.g. D9 29 8A C1 0A 2F 68 2C62  B7 3F 73 08 26 F9 4D")
        self.hex_key_edit.textChanged.connect(self.clear_key_file)
        hex_layout.addWidget(QLabel("Hex Key:"))
        hex_layout.addWidget(self.hex_key_edit)
        key_layout.addLayout(hex_layout)

        # Key file input
        file_layout = QHBoxLayout()
        self.key_file_edit = QLineEdit()
        self.key_file_edit.setPlaceholderText("Select key file")
        self.key_file_edit.textChanged.connect(self.clear_hex_key)
        key_file_button = QPushButton("Browse...")
        key_file_button.clicked.connect(self.select_key_file)
        file_layout.addWidget(QLabel("Key File:"))
        file_layout.addWidget(self.key_file_edit)
        file_layout.addWidget(key_file_button)
        key_layout.addLayout(file_layout)

        layout.addWidget(key_group)

        # App Version
        version_group = QGroupBox("Application Version")
        version_layout = QHBoxLayout(version_group)
        self.version_edit = QLineEdit()
        self.version_edit.setPlaceholderText("e.g. 0x20260301")
        version_layout.addWidget(QLabel("App Version (hex):"))
        version_layout.addWidget(self.version_edit)
        layout.addWidget(version_group)

        # Previous App Version
        prev_version_group = QGroupBox("Previous Application Version")
        prev_version_layout = QHBoxLayout(prev_version_group)
        self.prev_version_edit = QLineEdit()
        self.prev_version_edit.setPlaceholderText("e.g. 0x20260201 or 0x00000000 wneh no prev ver")
        prev_version_layout.addWidget(QLabel("Prev App Version (hex):"))
        prev_version_layout.addWidget(self.prev_version_edit)
        layout.addWidget(prev_version_group)

        # Page Length
        page_group = QGroupBox("Page Length")
        page_layout = QHBoxLayout(page_group)
        self.page_combo = QComboBox()
        # common flash page sizes; default 2048
        self.page_combo.addItems(["512", "1024", "2048", "4096"])
        self.page_combo.setCurrentText("2048")
        page_layout.addWidget(QLabel("Page Length (bytes):"))
        page_layout.addWidget(self.page_combo)
        layout.addWidget(page_group)

        # Buttons
        button_layout = QHBoxLayout()
        load_config_button = QPushButton("Load Configuration")
        load_config_button.clicked.connect(self.load_configuration)
        save_config_button = QPushButton("Save Configuration")
        save_config_button.clicked.connect(self.save_configuration)
        generate_button = QPushButton("Generate Binary")
        generate_button.clicked.connect(self.generate_binary)
        button_layout.addWidget(load_config_button)
        button_layout.addWidget(save_config_button)
        button_layout.addWidget(generate_button)
        layout.addLayout(button_layout)

        # Log output
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_group)

    def select_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Input File", "", "Binary Files (*.bin);;All Files (*)")
        if file_path:
            self.input_edit.setText(file_path)

    def select_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Select Output File", "", "Binary Files (*.bin);;All Files (*)")
        if file_path:
            self.output_edit.setText(file_path)

    def select_key_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Key File", "", "All Files (*)")
        if file_path:
            self.key_file_edit.setText(file_path)

    def clear_key_file(self, _):
        # clear file field when hex key is entered
        if self.hex_key_edit.text():
            self.key_file_edit.clear()

    def clear_hex_key(self, _):
        # clear hex field when key file is selected
        if self.key_file_edit.text():
            self.hex_key_edit.clear()

    def log_message(self, message):
        self.log_text.append(message)

    def _validate_and_get_params(self):
        """Validate inputs and return a dictionary of all parameters."""
        # Required fields
        fields = {
            "Input file": self.input_edit.text(),
            "Output file": self.output_edit.text(),
            "Device ID": self.device_edit.text(),
            "Bootloader ID": self.bootloader_edit.text(),
            "App Version": self.version_edit.text(),
            "Previous App Version": self.prev_version_edit.text(),
        }

        for name, value in fields.items():
            if not value:
                raise ValueError(f"{name} is required")

        # Key handling
        hex_key = self.hex_key_edit.text()
        key_file = self.key_file_edit.text()

        if hex_key and key_file:
            raise ValueError("Provide either a hex key or a key file, not both")
        if not hex_key and not key_file:
            raise ValueError("Either hex key or key file is required")

        key_arg = f"-k \"{hex_key}\"" if hex_key else f"-K \"{key_file}\""

        return {
            "input": fields["Input file"],
            "output": fields["Output file"],
            "device": fields["Device ID"],
            "bootloader": fields["Bootloader ID"],
            "version": fields["App Version"],
            "prev_version": fields["Previous App Version"],
            "key_arg": key_arg,
            "page_length": self.page_combo.currentText(),
        }

    def generate_binary(self):
        try:
            params = self._validate_and_get_params()

            # Build command line args
            import shlex

            args = [
                "-i",
                params["input"],
                "-o",
                params["output"],
                "-d",
                params["device"],
                "-b",
                params["bootloader"],
                params["key_arg"],
                "-v",
                params["version"],
                "-p",
                params["prev_version"],
                "-l",
                params["page_length"],
            ]
            parsed_args = get_parsed_args(shlex.split(' '.join(args)))
            config = Config.from_args(parsed_args)

            self.log_message("Parameters loaded successfully:")
            self.log_message(str(config))

            # Generate binary
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

            self.log_message(f"\nOutput file '{config.output_path}' generated successfully.")
            QMessageBox.information(self, "Success", f"Binary file generated successfully: {config.output_path}")

        except Exception as e:
            self.log_message(f"Error: {e}")
            QMessageBox.critical(self, "Error", str(e))

    def save_configuration(self):
        try:
            params = self._validate_and_get_params()

            config_path, _ = QFileDialog.getSaveFileName(self, "Save Configuration", "", "Text Files (*.txt);;All Files (*)")
            if not config_path:
                return

            with open(config_path, "w") as f:
                f.write(f'-i "{params["input"]}"\n')
                f.write(f'-o "{params["output"]}"\n')
                f.write(f'-d "{params["device"]}"\n')
                f.write(f'-b "{params["bootloader"]}"\n')
                f.write(f'{params["key_arg"]}\n')
                f.write(f'-v "{params["version"]}"\n')
                f.write(f'-p "{params["prev_version"]}"\n')
                f.write(f'-l "{params["page_length"]}"\n')

            self.log_message(f"Configuration saved to {config_path}")
            QMessageBox.information(self, "Success", f"Configuration saved to {config_path}")

        except Exception as e:
            self.log_message(f"Error: {e}")
            QMessageBox.critical(self, "Error", str(e))

    def load_configuration(self):
        # read file created by save_configuration and fill fields
        try:
            path, _ = QFileDialog.getOpenFileName(self, "Load Configuration", "", "Text Files (*.txt);;All Files (*)")
            if not path:
                return

            # Read and fix the config file to handle unquoted paths with spaces
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            fixed_lines = []
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    fixed_lines.append(line)
                    continue
                # Split on first space to separate flag from value
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    flag, value = parts
                    # If value contains spaces and is not already quoted, quote it
                    if ' ' in value and not (value.startswith('"') and value.endswith('"')):
                        value = f'"{value}"'
                    fixed_lines.append(f'{flag} {value}')
                else:
                    fixed_lines.append(line)

            # Write fixed content to a temporary file
            import tempfile

            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write('\n'.join(fixed_lines))
                temp_path = temp_file.name

            try:
                # Use the parser's built-in config loading mechanism
                parsed_args = get_parsed_args(["-c", temp_path])
                # populate fields from parsed_args
                self.input_edit.setText(parsed_args.input)
                self.output_edit.setText(parsed_args.output)
                self.device_edit.setText(hex(parsed_args.device_id))
                self.bootloader_edit.setText(hex(parsed_args.bootloader_id))
                if getattr(parsed_args, 'key_file', None):
                    self.key_file_edit.setText(parsed_args.key_file)
                    self.hex_key_edit.clear()
                else:
                    # Convert bytes key back to hex string
                    key_hex = ' '.join(f'{b:02X}' for b in parsed_args.key)
                    self.hex_key_edit.setText(key_hex)
                    self.key_file_edit.clear()
                self.version_edit.setText(hex(parsed_args.app_version))
                self.prev_version_edit.setText(hex(parsed_args.prev_app_version))
                self.page_combo.setCurrentText(str(parsed_args.page_length))
                self.log_message(f"Configuration loaded from {path}")
            finally:
                # Clean up temp file
                import os

                os.unlink(temp_path)

        except (Exception, SystemExit) as e:
            error_msg = str(e) if isinstance(e, Exception) else "Invalid configuration file format"
            self.log_message(f"Error loading configuration: {error_msg}")
            QMessageBox.critical(self, "Error", f"Failed to load configuration: {error_msg}")


def main():

    app = QApplication(sys.argv)
    window = EncryptBinGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
