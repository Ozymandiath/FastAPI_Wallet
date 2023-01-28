from fastapi import status, HTTPException


def bad_field(field: str, message: str) -> Exception:
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=[{
                            "loc": ["body", f"{field}"],
                            "msg": f"{message}",
                            "type": f"value_error.{field}"}])
