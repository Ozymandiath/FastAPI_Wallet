from fastapi import status, HTTPException


def bad_field(field: str, message: str) -> Exception:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                         detail=[{
                             "loc": ["body", f"{field}"],
                             "msg": f"{message}",
                             "type": f"value_error.{field}"}])


def unauthorized_field(field: str, message: str) -> Exception:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail=[{
                             "loc": ["body", f"{field}"],
                             "msg": f"{message}",
                             "type": f"value_error.{field}"}])


def unauthorized(field: str, message: str) -> Exception:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail=[{
                             "loc": f"{field}",
                             "msg": f"{message}",
                             "type": "error"}])
