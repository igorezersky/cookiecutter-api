import logging
import time
from typing import Optional, Type

from sqlalchemy import func
from sqlmodel import SQLModel, create_engine, Session, select

from {{ cookiecutter.project_slug }}.configs import DatabaseConfigs
from {{ cookiecutter.project_slug }}.orm import models

_logger = logging.getLogger(__name__)


class Database:
    def __init__(self, configs: DatabaseConfigs):
        self.configs = configs
        self.models = models
        self.engine = None
        self.start_session = lambda engine = None: Session(engine or self.engine)

    def connect(self, retry_count: int = None) -> 'Database':
        """ Connect to db. Will try to connect `retry_count` times if connection errors occur  """

        if retry_count is None:
            retry_count = self.configs.connect_retry_count

        try:
            self.engine = create_engine(self.configs.dsn, **self.configs.other)
            self.create_db()
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

    def create_db(self) -> 'Database':
        """ Create db tables  """

        SQLModel.metadata.create_all(self.engine)
        return self

    def drop_db(self) -> 'Database':
        """ Drop all db tables """

        SQLModel.metadata.drop_all(self.engine)
        return self

    @staticmethod
    def create(instance: SQLModel, session: Session, refresh: bool = False) -> SQLModel:
        """ Write `instance` to db """

        if instance.id is None:
            instance.id = session.query(func.count(instance.__class__.id)).scalar() + 1
        session.add(instance)
        session.commit()
        if refresh:
            session.refresh(instance)
        return instance

    @staticmethod
    def create_many(instances: list[SQLModel], session: Session, refresh: bool = False) -> list[SQLModel]:
        """ Write `instances` to db """

        session.add_all(instances)
        session.commit()
        if refresh:
            for instance in instances:
                session.refresh(instance)
        return instances

    @staticmethod
    def read(
        query: Optional[tuple],
        session: Session,
        model: Type[SQLModel],
        order_by=None,
        offset: int = None,
        limit: int = None
    ):
        """ Find (filtering by `query`) records in db """

        statement = select(model)
        if query is not None:
            statement = statement.where(query)
        if order_by is not None:
            statement = statement.order_by(order_by)
        if offset is not None:
            statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return session.exec(statement)

    def update(self, instance: SQLModel, session: Session) -> SQLModel:
        """ Update `instance` in db """

        return self.create(instance, session, refresh=True)

    def update_many(self, instances: list[SQLModel], session: Session) -> list[SQLModel]:
        """ Update `instances` in db """

        return self.create_many(instances, session, refresh=True)

    @staticmethod
    def delete(instance: SQLModel, session: Session):
        """ Delete `instance` from db """

        session.delete(instance)
        session.commit()

    @staticmethod
    def delete_many(instances: list[SQLModel], session: Session):
        """ Delete `instance` from db """

        for instance in instances:
            session.delete(instance)
        session.commit()
