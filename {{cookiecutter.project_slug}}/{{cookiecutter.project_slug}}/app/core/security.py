from datetime import datetime, timedelta
from typing import Dict, Optional

from fastapi import Request, Response, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from passlib.context import CryptContext

from {{ cookiecutter.project_slug }}.configs import SecurityConfigs
from {{ cookiecutter.project_slug }}.orm import Database


class Oauth2PasswordCookieBearer(OAuth2PasswordBearer):
    def __init__(self) -> None:
        self.configs: Optional[SecurityConfigs] = None

    def setup(self, configs: SecurityConfigs) -> 'Oauth2PasswordCookieBearer':
        """ Construct parent class with outer `configs`. This trick is necessary because of
        `Oauth2PasswordCookieBearer` object usage as a parameter in security methods """

        super().__init__(**configs.oauth2)
        self.configs = configs
        return self

    async def __call__(self, request: Request) -> Optional[str]:
        """ Perform two-step authorization for input `request`: extract Authorization token (Bearer) from headers,
        on fail - extract token from cookies """

        try:
            # parse auth headers
            token = await super().__call__(request)
        except HTTPException:
            # parse auth cookies
            cookie_authorization: str = request.cookies.get(self.configs.token_name)
            cookie_scheme, token = get_authorization_scheme_param(cookie_authorization)
            if not cookie_authorization or cookie_scheme.lower() != 'bearer':
                raise self.auth_error

        if not token:
            raise self.auth_error
        return token

    @property
    def auth_error(self) -> HTTPException:
        """ Return formatted HTTP exception for authorization error """

        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated',
            headers={'WWW-Authenticate': 'Bearer'},
        )


oauth2 = Oauth2PasswordCookieBearer()


class Security:
    def __init__(self, configs: SecurityConfigs, db: Database) -> None:
        self.configs = configs
        self.db = db
        oauth2.setup(configs=self.configs)
        self.pwd_context = CryptContext(**self.configs.crypt_context)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """ Check that encrypted `plain_password` is equal to `hashed_password` """

        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """ Encrypt `password` """

        return self.pwd_context.hash(password)

    def create_token_expires_delta(self) -> timedelta:
        """ Generate default expiring delta """

        return timedelta(hours=self.configs.access_token_expires_hours)

    def create_access_token(self, data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if not expires_delta:
            expires_delta = self.create_token_expires_delta()
        to_encode.update({'exp': datetime.utcnow() + expires_delta})
        return jwt.encode(
            to_encode,
            self.configs.secret_key.get_secret_value(),
            algorithm=self.configs.algorithm
        )

    def parse_access_token(self, token: str):
        try:
            payload = jwt.decode(
                token,
                self.configs.secret_key.get_secret_value(),
                algorithms=[self.configs.algorithm]
            )
            username = payload.get('sub')
        except JWTError:
            username = None

        if not username:
            raise oauth2.auth_error
        current_user = self.find_user(username)
        if not current_user:
            raise oauth2.auth_error

        return current_user

    def find_user(self, username: str, password: str = ''):
        """ Search for user in db with `username` and `password` (if presented) """

        with self.db.start_session() as session:
            user = self.db.read(filter_by={'username': username}, session=session, model=self.db.models.User)
        if not user or (password and not self.verify_password(password, user.password)):
            user = None
        return user

    def set_auth_cookie(self, user, response: Response) -> Response:
        """ Add auth cookie to response """

        expires = self.create_token_expires_delta()
        response.set_cookie(
            key=self.configs.token_name,
            value=f'Bearer {self.create_access_token(data={"sub": user.username}, expires_delta=expires)}'
        )
        return response
