
from datetime import datetime, timedelta

import jwt

from fastapi import HTTPException, status
from passlib.context import CryptContext


from core.settings import settings


class Auth:
    hasher = CryptContext(schemes=["bcrypt"])
    secret = settings.SECRET_KEY

    def hash_password(self, password):
        return self.hasher.hash(password)

    def verify_password(self, password, encoded_password):
        return self.hasher.verify(password, encoded_password)

    def encode_token(self, username):
        payload = {
            "exp": datetime.utcnow()
            + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRY_SECONDS),
            "iat": datetime.utcnow(),
            "scope": "access_token",
            "sub": username,
        }
        return jwt.encode(payload, self.secret, algorithm=settings.ALGORITHM)

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=[settings.ALGORITHM])
            if payload["scope"] == "access_token":
                return payload["sub"]
            raise HTTPException(401, detail="Scope for the token is invalid")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def encode_refresh_token(self, username):
        payload = {
            "exp": datetime.utcnow()
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRY_DAYS),
            "iat": datetime.utcnow(),
            "scope": "refresh_token",
            "sub": username,
        }
        return jwt.encode(payload, self.secret, algorithm=settings.ALGORITHM)


# ...

    def refresh_token(self, refresh_token):
        try:
            payload = jwt.decode(
                refresh_token, self.secret, algorithms=[settings.ALGORITHM]
            )

            if payload["scope"] == "refresh_token":
                username = payload["sub"]
                new_token = self.encode_token(username)
                new_refresh_token = self.encode_refresh_token(username)
                return new_token, new_refresh_token
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid scope for token"
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Refresh token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid refresh token"
            )

    def encode_verification_token(self, username):
        payload = {
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.EMAIL_TOKEN_EXPIRY_MINUTES),
            "iat": datetime.utcnow(),
            "scope": "email_verification",
            "sub": username,
        }
        return jwt.encode(payload, self.secret, algorithm=settings.ALGORITHM)

    def verify_email(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=[settings.ALGORITHM])

            if payload["scope"] == "email_verification":
                username = payload["sub"]
                return username
            raise HTTPException(status_code=401, detail="Invalid scope for token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Email token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid email token")

    def encode_reset_token(self, username):
        payload = {
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.RESET_TOKEN_EXPIRY_MINUTES),
            "iat": datetime.utcnow(),
            "scope": "reset_token",
            "sub": username,
        }
        return jwt.encode(payload, self.secret, algorithm=settings.ALGORITHM)

    def verify_reset_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=[settings.ALGORITHM])

            if payload["scope"] == "reset_token":
                username = payload["sub"]
                return username
            raise HTTPException(status_code=401, detail="Invalid scope for token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Reset token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid reset token")


auth = Auth()
