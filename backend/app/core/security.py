from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/token")
