from fastapi import HTTPException, status


class BaseHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class UserAlreadyExistsError(BaseHTTPException):
    def __init__(self):
        super().__init__(status.HTTP_409_CONFLICT, "User already exists")


class InvalidCredentialsError(BaseHTTPException):
    def __init__(self):
        super().__init__(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")


class InvalidTokenError(BaseHTTPException):
    def __init__(self):
        super().__init__(status.HTTP_401_UNAUTHORIZED, "Invalid token")


class TokenExpiredError(BaseHTTPException):
    def __init__(self):
        super().__init__(status.HTTP_401_UNAUTHORIZED, "Token expired")


class UserNotFoundError(BaseHTTPException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND, "User not found")


class PermissionDeniedError(BaseHTTPException):
    def __init__(self):
        super().__init__(status.HTTP_403_FORBIDDEN, "Permission denied")
