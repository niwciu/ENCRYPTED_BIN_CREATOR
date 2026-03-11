# 🔒 encrypt-bin: Encrypted BIN File Generator for Embedded Devices

**encrypt-bin** is a lightweight, flexible Python CLI tool for generating encrypted binary firmware files.  
It supports configuration through parameter files (`custom_config_name.txt`) and AES-128-CBC encryption compatible with Tiny-AES-C.

This project is part of whole ecosystem that contain this encrypted bin file generator, update tool for embedded devices and custom tiny bootloader (consume less than 4kB of flash).

---

## 🚀 Features

- 🔐 **AES-128 CBC encryption** (Tiny-AES-C compatible)
- 🧩 **Parameter file support (`-r`)** – store CLI arguments in a text file
- 🗝️ **Key loading from file or CLI**
- 🧮 **Automatic CRC32 calculation**
- ⚙️ **Full input validation** (paths, integers, key format)
- 🧰 **Clean, argparse-based CLI**
- ✅ **Extensive test coverage** (pytest + coverage)
- 🧾 **PEP8-compliant** (flake8, black)

---

## 🧠 Project Structure

```
encrypt-bin/
├── cli/
│   ├── parser.py         # CLI argument handling
│   ├── utils.py          # Helper functions (parse_int, parse_key, etc.)
│   ├── validators.py     # Path and file validation
│
├── core/
│   ├── builder.py        # Core logic for BIN generation
│   ├── config.py         # Config class – stores parsed parameters
│
└── tests/
    ├── test_parser.py
    ├── test_utils.py
    ├── test_builder.py
    └── ...
```

---

## 🖼️ GUI Overlay (Qt6)

A simple graphical interface wraps the CLI tool and exposes all parameters in a form. The GUI is implemented with **PyQt6** and sits on top of the existing command‑line logic: when you click **Generate Binary** the same parser and builder code is invoked under the hood.

### Features

* Select input/output files with a file picker
* Enter device ID, bootloader ID, application versions, and page length
* Choose between entering a hex key or selecting a key file (fields are mutually exclusive)
* Save the current configuration to a text file (compatible with `-r`/`-c` parameter file)
* Load a previously saved configuration back into the form
* Log area shows progress and errors

### Launching the GUI

Because the package may not be installed in editable mode, run the GUI directly from source:

```bash
# activate your project virtualenv first
source .venv/bin/activate
python src/encrypt_bin/gui/main.py
```

Alternatively, add `src` to `PYTHONPATH` and use the module form:

```bash
PYTHONPATH=src python -m encrypt_bin.gui.main
```


## ⚙️ Installation

### 1️⃣ Requirements
- Python **3.9+**
- `pip`
- `venv`

### 2️⃣ Install from PyPI *(not available now)*
```bash
pip install encrypt-bin
```

### 3️⃣ Local installation with dev tools
```bash
git clone https://github.com/<your_repo>/encrypt-bin.git
cd encrypt-bin
pip install -e .[dev]
```

---

## 💻 Usage
### 1️⃣ How to use it -> start from help flag
```bash
python -m encrypt-bin -h
```

### 1️⃣ Command-line example

```bash
python -m encrypt-bin     -i firmware.bin     -o encrypted_out.bin     -d 0x12345678     -b 0x10     -k "00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF"     -v 0x1201     -p 0x1100
```

### 2️⃣ Using a parameter file (`params.txt`)

File contents:
```
-i firmware.bin
-o encrypted_out.bin
-d 0x12345678
-b 0x10
-k 00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF
-v 0x1201
-p 0x1100
```

Run:
```bash
python -m encrypt-bin -r params.txt
```

---

## 🗝️ Key file format (`keys.txt`)

Use the `-K` / `--key-file` option to specify a key mapping file:

```
# device_id ; key
0x12345678;00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF
0x87654321;11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF 00
```

---

## 🧪 Testing

### Run all tests
```bash
pytest -v
```

### Check coverage
```bash
pytest --cov=encrypt-bin --cov-report=term-missing
```

### Run linting
```bash
flake8 src
```

### Run formating
```bash
black src tests
```

---

## 🧰 CLI Parameters

| Flag | Description | Required | Example |
|------|--------------|-----------|----------|
| `-i`, `--input` | Input .bin file | ✅ | `-i firmware.bin` |
| `-o`, `--output` | Output .bin file | ✅ | `-o output.bin` |
| `-d`, `--device-id` | Device ID (uint32) | ✅ | `-d 0x12345678` |
| `-b`, `--bootloader-id` | Bootloader ID (uint16) | ✅ | `-b 0x10` |
| `-k`, `--key` | 16-byte hex key | ✅ (if no `--key-file`) | `-k "00 11 22 ..."` |
| `-K`, `--key-file` | File containing key map | ✅ (if no `--key`) | `-K keys.txt` |
| `-v`, `--app-version` | Application version | ✅ | `-v 0x1201` |
| `-p`, `--prev-app-version` | Previous app version | ✅ | `-p 0x1100` |
| `-l`, `--page-length` | Page length (default: 2048) | ❌ | `-l 1024` |
| `-r`, `--requirements` | Parameter file | ❌ | `-r params.txt` |

---

## 🧩 BIN File Structure

| Offset | Size | Field |
|--------|------|-------|
| 0x00 | 4 | Bootloader ID |
| 0x04 | 4 | Product ID (MSB) |
| 0x08 | 4 | Product ID (LSB) |
| 0x0C | 4 | App Version |
| 0x10 | 4 | Previous App Version |
| 0x14 | 4 | Num Pages |
| 0x18 | 4 | Page Length |
| 0x1C | 16 | IV (AES) |
| 0x2C | 4 | CRC32 |
| 0x30 | N | Encrypted Payload |

---

## 🧱 Contributing

1. Fork the repository  
2. Create a new branch:  
   ```bash
   git checkout -b feature/my-feature
   ```
3. Run tests locally (`pytest`)  
4. Submit a Pull Request 🚀

---

## 🪪 License

Licensed under the **MIT License**.  
You are free to use, modify, and distribute this software, provided that proper credit is given.

---

## 👤 Author

**encrypt-bin** was created by niwicu.  
💬 Contact: [niwciu@gmail.com / [website](https://github.com/niwciu)]  
📦 Distribution: [PyPI / GitHub / internal project]

> “Secure firmware means secure hardware.” 🔐

<br>
<div align="center">

***

![myEmbeddedWayBanerWhiteSmaller](https://github.com/user-attachments/assets/f4825882-e285-4e02-a75c-68fc86ff5716)
***
</div>