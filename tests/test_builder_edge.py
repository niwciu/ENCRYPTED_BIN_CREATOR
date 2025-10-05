import pytest
from bin_creator.core.builder import encrypt_aes_cbc

def test_encrypt_aes_cbc_assertion():
    # Dane niepodzielne przez 16
    data = b"\x00" * 15  # padding nie został jeszcze dodany
    key = b"\x00" * 16
    iv = b"\x00" * 16
    with pytest.raises(AssertionError):
        encrypt_aes_cbc(data, key, iv)
