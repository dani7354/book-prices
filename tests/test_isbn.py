import pytest
import bookprices.shared.validation.isbn as isbn


@pytest.mark.parametrize("valid_isbn", ["9788740077315", "9788711553060", "9788711996782"])
def test_recognises_valid_isbn13(valid_isbn):
    assert isbn.check_isbn13(valid_isbn)


@pytest.mark.parametrize("valid_isbn", ["9788740077319", "9788711553065", "9788711996781"])
def test_recognises_invalid_check_digit(valid_isbn):
    assert not isbn.check_isbn13(valid_isbn)


@pytest.mark.parametrize("valid_isbn", ["978874", "", "-------------", "abcdefghijklm"])
def test_recognises_invalid_formats(valid_isbn):
    assert not isbn.check_isbn13(valid_isbn)


@pytest.mark.parametrize("valid_isbn", ["978-3-16-148410-0", "978871155306-0"])
def test_recognises_alternative_formats(valid_isbn):
    assert isbn.check_isbn13(valid_isbn)

