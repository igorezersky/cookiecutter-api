import logging
import time

from sqlmodel import SQLModel, create_engine

from {{ cookiecutter.project_slug }}.configs import DatabaseConfigs
from {{ cookiecutter.project_slug }}.orm import models

_logger = logging.getLogger(__name__)


class Database:
    def __init__(self, configs: DatabaseConfigs):
        self.configs = configs
        self.models = models
        self.engine = None

    def connect(self, retry_count: int = None) -> 'Database':
        """ Connect to db. Will try to connect `retry_count` times if connection errors occur  """

        if retry_count is None:
            retry_count = self.configs.connect_retry_count

        try:
            self.engine = create_engine(self.configs.dsn, **self.configs.other)
            self.create_all()
        except Exception as e:
            if retry_count:
                _logger.warning(
                    f'Failed to connect to DB "{self.configs.name}" at {self.configs.host}:{self.configs.port}. '
                    f'Trying to reconnect after {self.configs.connect_retry_delay}s ({retry_count} attempts left)'
                )
                time.sleep(self.configs.connect_retry_delay)
                self.connect(retry_count=retry_count - 1)
            else:
                raise e
        return self

    def create_all(self) -> 'Database':
        """ Create all db and all tables  """

        SQLModel.metadata.create_all(self.engine)
        return self

    def drop_all(self) -> 'Database':
        SQLModel.metadata.drop_all(self.engine)
        return self
