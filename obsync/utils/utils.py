from jose import jwt
import string
import hashlib
import random
from obsync.config import config
from loguru import logger


def get_jwt_email(jwt_string):
    try:
        decoded = jwt.decode(jwt_string, config.Secret)
        print(decoded)
        email = decoded.get("email")
        if email is None:
            raise ValueError("Invalid token: email not found")
        return email
    except Exception as e:
        logger.error(f"Error decoding JWT: {e}")
        raise ValueError("Invalid token")


def to_int(s):
    try:
        if s is None:
            return 0
        if isinstance(s, str):
            return int(s)
        elif isinstance(s, (int, float)):
            return int(s)
        else:
            raise TypeError(f"Unsupported type: {type(s)}")
    except ValueError as e:
        logger.error(f"Error converting to int: {e}")
        return 0
    except TypeError as e:
        logger.error(f"Error converting to int: {e}")
        raise


def generate_password(length, num_digits, num_symbols, no_upper, allow_repeat):
    """
    Generates a random password with the specified criteria.

    Args:
        length (int): The length of the password.
        num_digits (int): The number of digits in the password.
        num_symbols (int): The number of symbols in the password.
        no_upper (bool): Whether to exclude uppercase letters from the password.
        allow_repeat (bool): Whether repeated characters are allowed in the password.

    Returns:
        str: The generated password.

    Raises:
        ValueError: If the total length of the password exceeds the specified length.
        ValueError: If the number of required characters exceeds the available characters.
    """
    lower_letters = string.ascii_lowercase
    upper_letters = string.ascii_uppercase
    digits = string.digits
    symbols = string.punctuation

    letters = lower_letters + upper_letters if not no_upper else lower_letters

    chars = length - num_digits - num_symbols
    if chars < 0:
        raise ValueError("Total length exceeds the specified length.")

    if not allow_repeat and (
        chars > len(letters) or num_digits > len(digits) or num_symbols > len(symbols)
    ):
        raise ValueError("Number of required characters exceeds the available characters.")

    def random_element(elements, existing_elements):
        element = random.choice(elements)
        while not allow_repeat and element in existing_elements:
            element = random.choice(elements)
        return element

    result = []

    for _ in range(chars):
        result.append(random_element(letters, result))

    for _ in range(num_digits):
        result.append(random_element(digits, result))

    for _ in range(num_symbols):
        result.append(random_element(symbols, result))

    random.shuffle(result)
    return "".join(result)


def getKey(
    e: str,
    t: str,
    N: int = 32,
    r: int = 8,
    p: int = 1,
    key_len: int = 32,
    maxmem: int = 2
    << 25,  # If not specified, it will cause a ValueError: [digital envelope routines] memory limit exceeded
) -> bytes:
    normalizedE = e.encode()
    normalizedT = t.encode()

    return hashlib.scrypt(
        password=normalizedE,
        salt=normalizedT,
        n=N,
        r=r,
        p=p,
        dklen=key_len,
        maxmem=maxmem,
    )


def MakeKeyHash(e: str, t: str) -> str:
    n = getKey(e, t)
    return hashlib.sha256(n).hexdigest()
