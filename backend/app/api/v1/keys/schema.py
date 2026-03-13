from pydantic import BaseModel

class APIKeyCreate(BaseModel):
    api_key: str
    disabled: bool = False