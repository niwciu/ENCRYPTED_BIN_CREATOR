# tests/test_config.py
from encrypt_bin.core.config import Config
from types import SimpleNamespace


def test_config_from_args_and_summary(tmp_path, capsys):
    args = SimpleNamespace(
        input=str(tmp_path / "in.bin"),
        output=str(tmp_path / "out.bin"),
        device_id=0x1234,
        bootloader_id=0x10,
        key=b"\x00" * 16,
        app_version=0x1201,
        prev_app_version=0x1100,
        page_length=2048,
    )
    cfg = Config.from_args(args)
    assert cfg.input_path == args.input
    assert cfg.output_path == args.output
    assert cfg.key == args.key

    cfg.print_summary()
    captured = capsys.readouterr()
    assert "Input" in captured.out
    assert "Device" in captured.out
