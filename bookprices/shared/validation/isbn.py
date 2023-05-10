ISBN_13_LENGTH = 13
ISBN_DELIMITER = "-"


def check_isbn13(isbn13: str) -> bool:
    isbn13 = isbn13.replace(ISBN_DELIMITER, "")
    if len(isbn13) != ISBN_13_LENGTH:
        return False

    return _calculate_check_digit(isbn13) == int(isbn13[-1])


def _calculate_check_digit(isbn13: str) -> int:
    sum = 0
    for i in range(0, ISBN_13_LENGTH - 1):
        multiply_by = 1 if i % 2 == 0 else 3
        sum += int(isbn13[i]) * multiply_by

    return (10 - (sum % 10)) % 10
