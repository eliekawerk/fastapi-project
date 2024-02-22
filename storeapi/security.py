import datetime
import logging
from typing import Optional

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext

from storeapi.database import database, user_table
from storeapi.models.user import UserIn

logger = logging.getLogger(__name__)

SECRET_KEY = "1234"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"])


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate exception"
)


def access_token_expire_minutes() -> int:
    return 30


def create_access_token(email: str):
    logger.debug("Creating access token", extra={"email": email})
    expire = datetime.datetime.now() + datetime.timedelta(
        minutes=access_token_expire_minutes()
    )
    jwt_data = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(email: str) -> Optional[UserIn]:
    logger.info("Fetching user from database", extra={"email": email})
    query = user_table.select().where(user_table.c.email == email)
    result = await database.fetch_one(query)
    if result:
        return result


async def authenticate_user(email: str, password: str):
    logger.debug("Authenticating user", extra={"email": email})
    user = await get_user(email)
    if not user:
        pass
    if not verify_password(password, user.password):
        pass
    return user
