from dataclasses import dataclass
from typing import Generic, Optional, Type, TypeAlias, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ..decorator.db_async_session import db_async_session

from ..models.decorated_base import DecoratedBase
from ..exceptions import *


# Generic Type for Pydantic and SQLAlchemy
FiFiModel = TypeVar("FiFiModel", bound=DecoratedBase)
FiFiSchema: TypeAlias = BaseModel


@dataclass
class Repository(Generic[FiFiModel]):
    model: Type[FiFiModel]

    @db_async_session
    async def create(
        self,
        data: FiFiSchema,
        session: Optional[AsyncSession] = None,
    ) -> FiFiModel:
        """Accepts a Pydantic model, creates a new record in the database, catches
        any integrity errors, and returns the record.

        Args:
            data (FiFiSchema): Pydantic model
            session (Optional[AsyncSession]): SQLAlchemy async session

        Raises:
            IntegrityConflictException: if creation conflicts with existing data
            FiFiException: if an unknown error occurs

        Returns:
            FiFiModel: created SQLAlchemy model
        """
        if not session:
            raise NotExistedSessionException("session is not existed")
        try:
            db_model = self.model(**data.model_dump())
            session.add(db_model)
            await session.commit()
            await session.refresh(db_model)
            return db_model
        except IntegrityError:
            raise IntegrityConflictException(
                f"{self.model.__tablename__} conflicts with existing data.",
            )
        except Exception as e:
            raise FiFiException(f"Unknown error occurred: {e}") from e

    @db_async_session
    async def create_many(
        self,
        data: list[FiFiSchema],
        return_models: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> list[FiFiModel] | bool:
        """_summary_

        Args:
            session (Optional[AsyncSession]): SQLAlchemy async session
            data (list[FiFiSchema]): list of Pydantic models
            return_models (bool, optional): Should the created models be returned
                or a boolean indicating they have been created. Defaults to False.

        Raises:
            IntegrityConflictException: if creation conflicts with existing data
            FiFiException: if an unknown error occurs

        Returns:
            list[FiFiModel] | bool: list of created SQLAlchemy models or boolean
        """
        if not session:
            raise NotExistedSessionException("session is not existed")
        db_models = [self.model(**d.model_dump()) for d in data]
        if not data:
            if not return_models:
                return False
            return db_models
        try:
            session.add_all(db_models)
            await session.commit()
        except IntegrityError:
            raise IntegrityConflictException(
                f"{self.model.__tablename__} conflict with existing data.",
            )
        except Exception as e:
            raise FiFiException(f"Unknown error occurred: {e}") from e

        if not return_models:
            return True

        for m in db_models:
            await session.refresh(m)

        return db_models

    @db_async_session
    async def get_one_by_id(
        self,
        id_: str,
        column: str = "id",
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> Optional[FiFiModel]:
        """Fetches one record from the database based on a column value and returns
        it, or returns None if it does not exist. Raises an exception if the column
        doesn't exist.

        Args:
            session (Optional[AsyncSession], optional): SQLAlchemy async session
            id_ (str): value to search for in `column`.
            column (str, optional): the column name in which to search.
                Defaults to "uuid".
            with_for_update (bool, optional): Should the returned row be locked
                during the lifetime of the current open transactions.
                Defaults to False.

        Raises:
            FiFiException: if the column does not exist on the model

        Returns:
            FiFiModel: SQLAlchemy model or None
        """
        if not session:
            raise NotExistedSessionException("session is not existed")
        try:
            q = select(self.model).where(getattr(self.model, column) == id_)
        except AttributeError:
            raise FiFiException(
                f"Column {column} not found on {self.model.__tablename__}.",
            )

        if with_for_update:
            q = q.with_for_update()

        results = await session.execute(q)
        return results.unique().scalar_one_or_none()

    @db_async_session
    async def get_many_by_ids(
        self,
        ids: Optional[list[str]],
        column: str = "id",
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> list[FiFiModel]:
        """Fetches multiple records from the database based on a column value and
        returns them. Raises an exception if the column doesn't exist.

        Args:
            session (Optional[AsyncSession]): SQLAlchemy async session
            ids (list[str], optional): list of values to search for in
                `column`. Defaults to None.
            column (str, optional): the column name in which to search
                Defaults to "id".
            with_for_update (bool, optional): Should the returned rows be locked
                during the lifetime of the current open transactions.
                Defaults to False.

        Raises:
            FiFiException: if the column does not exist on the model
            NotExistSessionException: if not session append to the calling this method

        Returns:
            list[FiFiModel]: list of SQLAlchemy models
        """
        if not session:
            raise NotExistedSessionException("session is not existed")
        q = select(self.model)
        if ids:
            try:
                q = q.where(getattr(self.model, column).in_(ids))
            except AttributeError:
                raise FiFiException(
                    f"Column {column} not found on {self.model.__tablename__}.",
                )

        if with_for_update:
            q = q.with_for_update()

        rows = await session.execute(q)
        return list(rows.unique().scalars().all())

    @db_async_session
    async def update_by_id(
        self,
        data: FiFiSchema,
        id_: str,
        column: str = "id",
        session: Optional[AsyncSession] = None,
    ) -> FiFiModel:
        """Updates a record in the database based on a column value and returns the
        updated record. Raises an exception if the record isn't found or if the
        column doesn't exist.

        Args:
            session (Optional[AsyncSession]): SQLAlchemy async session
            data (FiFiSchema): Pydantic schema for the updated data.
            id_ (str | UUID): value to search for in `column`
            column (str, optional): the column name in which to search
                Defaults to "uuid".
        Raises:
            NotFoundException: if the record isn't found
            IntegrityConflictException: if the update conflicts with existing data

        Returns:
            FiFiModel: updated SQLAlchemy model
        """
        if not session:
            raise NotExistedSessionException("session is not existed")
        db_model = await self.get_one_by_id(
            session, id_, column=column, with_for_update=True
        )
        if not db_model:
            raise NotFoundException(
                f"{self.model.__tablename__} {column}={id_} not found.",
            )

        values = data.model_dump(exclude_unset=True)
        for k, v in values.items():
            setattr(db_model, k, v)

        try:
            await session.commit()
            await session.refresh(db_model)
            return db_model
        except IntegrityError:
            raise IntegrityConflictException(
                f"{self.model.__tablename__} {column}={id_} conflict with existing data.",
            )

    @db_async_session
    async def update_many_by_ids(
        self,
        updates: dict[str, FiFiSchema],
        column: str = "id",
        return_models: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> list[FiFiModel] | bool:
        """Updates multiple records in the database based on a column value and
        returns the updated records. Raises an exception if the column doesn't
        exist.

        Args:
            session (Optional[AsyncSession]): SQLAlchemy async session
            updates (dict[str  |  UUID, FiFiSchema]): dictionary of id_ to
                Pydantic update schema
            column (str, optional): the column name in which to search.
                Defaults to "uuid".
            return_models (bool, optional): Should the created models be returned
                or a boolean indicating they have been created. Defaults to False.
                Defaults to False.

        Raises:
            IntegrityConflictException: if the update conflicts with existing data

        Returns:
            list[FiFiModel] | bool: list of updated SQLAlchemy models or boolean
        """
        if not session:
            raise NotExistedSessionException("session is not existed")
        updates = {str(id): update for id, update in updates.items() if update}
        ids = list(updates.keys())
        db_models = await self.get_many_by_ids(
            session, ids=ids, column=column, with_for_update=True
        )

        for db_model in db_models:
            values = updates[str(getattr(db_model, column))].model_dump(
                exclude_unset=True
            )
            for k, v in values.items():
                setattr(db_model, k, v)
            session.add(db_model)

        try:
            await session.commit()
        except IntegrityError:
            raise IntegrityConflictException(
                f"{self.model.__tablename__} conflict with existing data.",
            )

        if not return_models:
            return True

        for db_model in db_models:
            await session.refresh(db_model)

        return db_models

    @db_async_session
    async def remove_by_id(
        self,
        id_: str,
        column: str = "id",
        session: Optional[AsyncSession] = None,
    ) -> int:
        """Removes a record from the database based on a column value. Raises an
        exception if the column doesn't exist.

        Args:
            session (Optional[AsyncSession]): SQLAlchemy async session
            id (str | UUID): value to search for in `column` and delete
            column (str, optional): the column name in which to search.
                Defaults to "uuid".

        Raises:
            FiFiException: if the column does not exist on the model

        Returns:
            int: number of rows removed, 1 if successful, 0 if not. Can be greater
                than 1 if id_ is not unique in the column.
        """
        if not session:
            raise NotExistedSessionException("session is not existed")
        try:
            query = delete(self.model).where(getattr(self.model, column) == id_)
        except AttributeError:
            raise FiFiException(
                f"Column {column} not found on {self.model.__tablename__}.",
            )

        rows = await session.execute(query)
        await session.commit()
        return rows.rowcount

    @db_async_session
    async def remove_many_by_ids(
        self,
        ids: list[str],
        column: str = "id",
        session: Optional[AsyncSession] = None,
    ) -> int:
        """Removes multiple records from the database based on a column value.
        Raises an exception if the column doesn't exist.

        Args:
            session (Optional[AsyncSession]): SQLAlchemy async session
            ids (list[str  |  UUID]): list of values to search for in `column` and
            column (str, optional): the column name in which to search.
                Defaults to "uuid".

        Raises:
            FiFiException: if ids is empty to stop deleting an entire table
            FiFiException: if column does not exist on the model

        Returns:
            int: _description_
        """
        if not session:
            raise NotExistedSessionException("session is not existed")
        if not ids:
            raise FiFiException("No ids provided.")

        try:
            query = delete(self.model).where(getattr(self.model, column).in_(ids))
        except AttributeError:
            raise FiFiException(
                f"Column {column} not found on {self.model.__tablename__}.",
            )

        rows = await session.execute(query)
        await session.commit()
        return rows.rowcount
