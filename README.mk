# bin-tool

Narzędzie w Pythonie do analizy i modyfikacji plików binarnych firmware’u.

## Uruchamianie

Z poziomu źródeł:
```bash
python -m bin_tool -i firmware.bin -o output.bin -d 0x12345678 -b 0x0100 \
  -k "00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF" \
  -v 0x1201 -p 0x1100
