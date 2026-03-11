"""GUI module for the encrypt-bin application."""

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QComboBox, QGroupBox, QRadioButton,
    QButtonGroup, QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt
import sys
import os
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
        self.device_edit.setPlaceholderText("e.g. 0x0000000102201001")
        device_layout.addWidget(QLabel("Device ID (hex):"))
        device_layout.addWidget(self.device_edit)
        layout.addWidget(device_group)

        # Bootloader ID
        bootloader_group = QGroupBox("Bootloader ID")
        bootloader_layout = QHBoxLayout(bootloader_group)
        self.bootloader_edit = QLineEdit()
        self.bootloader_edit.setPlaceholderText("e.g. 0x00000001")
        bootloader_layout.addWidget(QLabel("Bootloader ID (hex):"))
        bootloader_layout.addWidget(self.bootloader_edit)
        layout.addWidget(bootloader_group)

        # Key selection
        key_group = QGroupBox("Encryption Key")
        key_layout = QVBoxLayout(key_group)

        # Radio buttons for key type
        self.key_radio_group = QButtonGroup(key_group)
        self.hex_key_radio = QRadioButton("Hex Key")
        self.file_key_radio = QRadioButton("Key File")
        self.hex_key_radio.setChecked(True)
        self.key_radio_group.addButton(self.hex_key_radio)
        self.key_radio_group.addButton(self.file_key_radio)

        key_layout.addWidget(self.hex_key_radio)
        key_layout.addWidget(self.file_key_radio)

        # Hex key input
        hex_layout = QHBoxLayout()
        self.hex_key_edit = QLineEdit()
        self.hex_key_edit.setPlaceholderText("e.g. 2F 73 08 68 62 2C D9 8A 29 C1 0A B7 3F 26 4D F9")
        hex_layout.addWidget(QLabel("Hex Key:"))
        hex_layout.addWidget(self.hex_key_edit)
        key_layout.addLayout(hex_layout)

        # Key file input
        file_layout = QHBoxLayout()
        self.key_file_edit = QLineEdit()
        self.key_file_edit.setPlaceholderText("Select key file")
        self.key_file_edit.setEnabled(False)
        key_file_button = QPushButton("Browse...")
        key_file_button.clicked.connect(self.select_key_file)
        key_file_button.setEnabled(False)
        file_layout.addWidget(QLabel("Key File:"))
        file_layout.addWidget(self.key_file_edit)
        file_layout.addWidget(key_file_button)
        key_layout.addLayout(file_layout)

        # Connect radio buttons
        self.hex_key_radio.toggled.connect(self.toggle_key_input)
        self.file_key_radio.toggled.connect(self.toggle_key_input)

        layout.addWidget(key_group)

        # App Version
        version_group = QGroupBox("Application Version")
        version_layout = QHBoxLayout(version_group)
        self.version_edit = QLineEdit()
        self.version_edit.setPlaceholderText("e.g. 0x20260300")
        version_layout.addWidget(QLabel("App Version (hex):"))
        version_layout.addWidget(self.version_edit)
        layout.addWidget(version_group)

        # Previous App Version
        prev_version_group = QGroupBox("Previous Application Version")
        prev_version_layout = QHBoxLayout(prev_version_group)
        self.prev_version_edit = QLineEdit()
        self.prev_version_edit.setPlaceholderText("e.g. 0x00000000")
        prev_version_layout.addWidget(QLabel("Prev App Version (hex):"))
        prev_version_layout.addWidget(self.prev_version_edit)
        layout.addWidget(prev_version_group)

        # Page Length
        page_group = QGroupBox("Page Length")
        page_layout = QHBoxLayout(page_group)
        self.page_combo = QComboBox()
        self.page_combo.addItems(["512", "1024", "2048", "4096", "8192", "16384", "32768", "65536"])
        page_layout.addWidget(QLabel("Page Length (bytes):"))
        page_layout.addWidget(self.page_combo)
        layout.addWidget(page_group)

        # Buttons
        button_layout = QHBoxLayout()
        generate_button = QPushButton("Generate Binary")
        generate_button.clicked.connect(self.generate_binary)
        save_config_button = QPushButton("Save Configuration")
        save_config_button.clicked.connect(self.save_configuration)
        button_layout.addWidget(generate_button)
        button_layout.addWidget(save_config_button)
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

    def toggle_key_input(self):
        if self.hex_key_radio.isChecked():
            self.hex_key_edit.setEnabled(True)
            self.key_file_edit.setEnabled(False)
        else:
            self.hex_key_edit.setEnabled(False)
            self.key_file_edit.setEnabled(True)

    def log_message(self, message):
        self.log_text.append(message)

    def generate_binary(self):
        try:
            # Validate inputs
            if not self.input_edit.text():
                raise ValueError("Input file is required")
            if not self.output_edit.text():
                raise ValueError("Output file is required")
            if not self.device_edit.text():
                raise ValueError("Device ID is required")
            if not self.bootloader_edit.text():
                raise ValueError("Bootloader ID is required")
            if not self.version_edit.text():
                raise ValueError("App Version is required")
            if not self.prev_version_edit.text():
                raise ValueError("Previous App Version is required")

            if self.hex_key_radio.isChecked():
                if not self.hex_key_edit.text():
                    raise ValueError("Hex key is required")
                key_arg = f"-k \"{self.hex_key_edit.text()}\""
            else:
                if not self.key_file_edit.text():
                    raise ValueError("Key file is required")
                key_arg = f"-K \"{self.key_file_edit.text()}\""

            # Build command line arguments
            args = [
                "-i", self.input_edit.text(),
                "-o", self.output_edit.text(),
                "-d", self.device_edit.text(),
                "-b", self.bootloader_edit.text(),
                key_arg,
                "-v", self.version_edit.text(),
                "-p", self.prev_version_edit.text(),
                "-l", self.page_combo.currentText()
            ]

            # Parse arguments
            import shlex
            parsed_args = get_parsed_args.__wrapped__(shlex.split(' '.join(args)))

            # Create config
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
            # Validate inputs
            if not self.input_edit.text():
                raise ValueError("Input file is required")
            if not self.output_edit.text():
                raise ValueError("Output file is required")
            if not self.device_edit.text():
                raise ValueError("Device ID is required")
            if not self.bootloader_edit.text():
                raise ValueError("Bootloader ID is required")
            if not self.version_edit.text():
                raise ValueError("App Version is required")
            if not self.prev_version_edit.text():
                raise ValueError("Previous App Version is required")

            if self.hex_key_radio.isChecked():
                if not self.hex_key_edit.text():
                    raise ValueError("Hex key is required")
                key_line = f"-k {self.hex_key_edit.text()}"
            else:
                if not self.key_file_edit.text():
                    raise ValueError("Key file is required")
                key_line = f"-K {self.key_file_edit.text()}"

            # Get save location
            config_path, _ = QFileDialog.getSaveFileName(self, "Save Configuration", "", "Text Files (*.txt);;All Files (*)")
            if not config_path:
                return

            # Write configuration file
            with open(config_path, 'w') as f:
                f.write(f"-i {self.input_edit.text()}\n")
                f.write(f"-o {self.output_edit.text()}\n")
                f.write(f"-d {self.device_edit.text()}\n")
                f.write(f"-b {self.bootloader_edit.text()}\n")
                f.write(f"{key_line}\n")
                f.write(f"-v {self.version_edit.text()}\n")
                f.write(f"-p {self.prev_version_edit.text()}\n")
                f.write(f"-l {self.page_combo.currentText()}\n")

            self.log_message(f"Configuration saved to {config_path}")
            QMessageBox.information(self, "Success", f"Configuration saved to {config_path}")

        except Exception as e:
            self.log_message(f"Error: {e}")
            QMessageBox.critical(self, "Error", str(e))


def main():
    app = QApplication(sys.argv)
    window = EncryptBinGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()