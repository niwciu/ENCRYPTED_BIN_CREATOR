import pytest
from bin_creator.cli import validators


def test_validate_file_paths(tmp_path):
    input_file = tmp_path / "in.bin"
    input_file.write_bytes(b"\x00")
    output_file = tmp_path / "out.bin"

    # poprawny przypadek
    validators.validate_file_paths(str(input_file), str(output_file))

    # brak input_file -> SystemExit
    with pytest.raises(SystemExit):
        validators.validate_file_paths(str(tmp_path / "missing.bin"), str(output_file))

    # input file bez rozszerzenia .bin -> SystemExit
    input_txt = tmp_path / "in.txt"
    input_txt.write_bytes(b"\x00")
    with pytest.raises(SystemExit) as e:
        validators.validate_file_paths(str(input_txt), str(output_file))
    assert "rozszerzenie '.bin'" in str(e.value)

    # nieistniejący katalog dla output -> SystemExit
    invalid_output = tmp_path / "nonexistent_dir" / "out.bin"
    with pytest.raises(SystemExit):
        validators.validate_file_paths(str(input_file), str(invalid_output))

    # output file bez rozszerzenia .bin -> SystemExit
    output_txt = tmp_path / "out.txt"
    with pytest.raises(SystemExit) as e:
        validators.validate_file_paths(str(input_file), str(output_txt))
    assert "rozszerzenie '.bin'" in str(e.value)
