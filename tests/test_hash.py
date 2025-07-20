import pytest
from news_aggregator import hash


def test_has_password_not_equal_to_plain():
    password = "test_password"
    hashed=hash.hash_password(password)
    assert hashed!=password
    assert isinstance(hashed, str)
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")


def test_verify_password_success():
    password = "test_password"
    hashed = hash.hash_password(password)
    assert hash.verify_password(password, hashed) is True

def test_verify_password_faliure():
    password = "plain_test_pwd"
    w_pwd = "w_password"
    hashed = hash.hash_password(password)
    assert hash.verify_password(w_pwd,hashed) is False
    assert hash.verify_password(password, hashed) is True

def test_different_hashes():
    password = "test_password"
    hashed1 = hash.hash_password(password)
    hashed2 = hash.hash_password(password)
    assert hashed1 != hashed2


def test_invalid_hash():
    pwd = "secret"
    with pytest.raises(ValueError):
        hash.verify_password(pwd,"hhhhhhhfnj")