from typing import Generic, Optional, TypeVar, Dict
from pydantic.generics import GenericModel

T = TypeVar("T")

class Result(GenericModel, Generic[T]):
    success: bool
    message: Optional[str] = None
    data: Optional[T] = None
    errorCode: Optional[str] = None
    meta: Optional[Dict[str, object]] = None

    @classmethod
    def ok(cls, data: T = None, message: str = "Success", meta: dict = None):
        return cls(success=True, message=message, data=data, meta=meta)

    @classmethod
    def fail(cls, errorCode: str = "ERROR", message: str = "Failed", meta: dict = None):
        return cls(success=False, errorCode=errorCode, message=message, meta=meta)