from fastapi import status


class SigninException(Exception):
    def __init__(self, email: str, message: str):
        self.retcode: int = status.HTTP_400_BAD_REQUEST
        self.email: str = email
        self.message: str = message

    def __str__(self) -> str:
        return f"{self.retcode}: {self.message} for User `{self.email}`"
