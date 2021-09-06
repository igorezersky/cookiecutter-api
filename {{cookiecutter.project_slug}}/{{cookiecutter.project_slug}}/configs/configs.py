""" This module contains settings containers. Different settings are stored in different containers, main access is
provided with `Configs` class help.
"""

import logging.config
from pathlib import Path
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, SecretStr
from ruamel.yaml import YAML
from starlette.config import Config as StarletteConfig

__all__ = ['ServerConfigs', 'DatabaseConfigs', 'SecurityConfigs', 'ValidationConfigs', 'PathConfigs', 'Configs']


class Context(BaseModel):
    yml: Any
    env: Any
    package_dir: Path

    @classmethod
    def load(
        cls,
        package_dir: Union[str, Path],
        yml_path: Union[str, Path] = None,
        env_path: Union[str, Path] = None
    ) -> 'Context':
        """ Load configs from environment and YAML file """

        package_dir = Path(package_dir)
        if not package_dir.exists():
            raise FileNotFoundError(package_dir)

        env_path = Path(env_path or f'{package_dir.parent}/.env')
        env_config = StarletteConfig(env_path if env_path.exists() else '')

        yaml = YAML()
        yml_path = Path(yml_path or f'{package_dir}/configs/configs.yml')
        with yml_path.open('r', encoding='utf-8') as fp:
            yml_config = yaml.load(fp)
        return cls(yml=yml_config, env=env_config, package_dir=package_dir)


class ServerConfigs(BaseModel):
    host: str
    port: int
    enable_cors: bool

    @classmethod
    def from_context(cls, context: Context) -> 'ServerConfigs':
        return cls(
            host=context.env.get('HOST', default=context.yml['server']['host'], cast=str),
            port=context.env.get('PORT', default=context.yml['server']['port'], cast=int),
            enable_cors=context.env.get('ENABLE_CORS', default=context.yml['server']['enable_cors'], cast=bool)
        )


class DatabaseConfigs(BaseModel):
    dialect: str
    username: SecretStr
    password: SecretStr
    host: str
    port: int
    name: str
    connect_retry_count: int
    connect_retry_delay: int
    other: Dict = Field(default_factory=dict)

    @classmethod
    def from_context(cls, context: Context) -> 'DatabaseConfigs':
        return cls(
            dialect=context.env.get('DB_DIALECT', default=context.yml['db']['dialect'], cast=str),
            username=context.env.get('DB_USERNAME', cast=str),
            password=context.env.get('DB_PASSWORD', cast=str),
            host=context.env.get('DB_HOST', default=context.yml['db']['host'], cast=str),
            port=context.env.get('DB_PORT', default=context.yml['db']['port'], cast=int),
            name=context.env.get('DB_NAME', default=context.yml['db']['name'], cast=str),
            connect_retry_count=context.yml['db']['connect_retry']['count'],
            connect_retry_delay=context.yml['db']['connect_retry']['delay'],
            other=context.yml['db'].get('other', {})
        )

    @property
    def dsn(self) -> str:
        return f'{self.dialect}://{self.username.get_secret_value()}:{self.password.get_secret_value()}' \
               f'@{self.host}:{self.port}/{self.name}'


class SecurityConfigs(BaseModel):
    secret_key: SecretStr
    algorithm: str
    access_token_expires_hours: int
    token_name: str
    crypt_context: Dict = {}
    oauth2: Dict = {}

    @classmethod
    def from_context(cls, context: Context) -> 'SecurityConfigs':
        return cls(
            secret_key=context.env.get('SECRET_KEY', cast=str),
            **context.yml['security']
        )


class ValidationConfigs(BaseModel):
    email: Dict
    password: Dict

    @classmethod
    def from_context(cls, context: Context) -> 'ValidationConfigs':
        return cls(**context.yml['validation'])


class PathConfigs(BaseModel):
    logs: Path
    static: Optional[Path] = None
    templates: Optional[Path] = None

    @classmethod
    def from_context(cls, context: Context) -> 'PathConfigs':
        obj = cls(
            logs=Path(context.yml['path']['logs']),
            static=Path(f'{context.package_dir}/app/static'),
            templates=Path(f'{context.package_dir}/app/templates')
        )
        obj.logs.mkdir(parents=True, exist_ok=True)
        return obj


class Configs:
    """ Container of all system configs """

    def __init__(self, package_dir: Union[str, Path], **kwargs) -> None:
        self._context = Context.load(package_dir, **kwargs)

        self.server = ServerConfigs.from_context(self._context)
        self.db = DatabaseConfigs.from_context(self._context)
        self.security = SecurityConfigs.from_context(self._context)
        self.validation = ValidationConfigs.from_context(self._context)
        self.path = PathConfigs.from_context(self._context)

        self.configure_logging()

    def configure_logging(self) -> 'Configs':
        """ Add logs directory path to all file handlers and apply logging configs """

        if 'handlers' in self._context.yml['logging']:
            for key in self._context.yml['logging']['handlers']:
                handler_fname = self._context.yml['logging']['handlers'][key].get('filename')
                if handler_fname:
                    self._context.yml['logging']['handlers'][key]['filename'] = f'{self.path.logs}/{handler_fname}'
        logging.config.dictConfig(self._context.yml['logging'])
        return self
