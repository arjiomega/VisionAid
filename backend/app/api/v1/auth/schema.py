from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    api_key: str | None = None

class APIKey(BaseModel):
    api_key: str
    disabled: bool | None = None
    remaining_secs: int | None = None

class APIKeyInDB(APIKey):
    hashed_api_key: str