from dataclasses import dataclass
from typing import (
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Type,
    TypeVar,
    overload,
)

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ..decorator.db_async_session import db_async_session

from ..models.decorated_base import DecoratedBase
from ..exceptions import *

# Generic Type for Pydantic and SQLAlchemy
EntityModel = TypeVar("EntityModel", bound=DecoratedBase)
EntitySchema = TypeVar("EntitySchema", bound=BaseModel)


@dataclass
class Repository(Generic[EntityModel, EntitySchema]):
    model: Type[EntityModel]
    db_session: AsyncSession

    async def create(
        self,
        data: EntitySchema,
    ) -> EntityModel:
        """Accepts a Pydantic model, creates a new record in the database, catches
        any integrity errors, and returns the record.

        Args:
            data (EntitySchema): Pydantic model

        Raises:
            IntegrityConflictException: if creation conflicts with existing data
            EntityException: if an unknown error occurs

        Returns:
            EntityModel: created SQLAlchemy model
        """
        try:
            db_model = self.model(**data.model_dump())
            self.db_session.add(db_model)
            await self.db_session.flush()
            return db_model
        except IntegrityError:
            raise IntegrityConflictException(
                f"{self.model.__tablename__} conflicts with existing data.",
            )
        except Exception as e:
            raise EntityException(f"Unknown error occurred: {e}") from e

    async def create_many(
        self,
        data: List[EntitySchema],
    ) -> List[EntityModel]:
        """_summary_

        Args:
            data (list[EntitySchema]): list of Pydantic models

        Raises:
            IntegrityConflictException: if creation conflicts with existing data
            EntityException: if an unknown error occurs

        Returns:
            list[EntityModel] | bool: list of created SQLAlchemy models or boolean
        """
        db_models = [self.model(**d.model_dump()) for d in data]
        if not data:
            return db_models
        try:
            self.db_session.add_all(db_models)
            await self.db_session.flush()
        except IntegrityError:
            raise IntegrityConflictException(
                f"{self.model.__tablename__} conflict with existing data.",
            )
        except Exception as e:
            raise EntityException(f"Unknown error occurred: {e}") from e
        return db_models

    async def get_one_by_id(
        self,
        id_: str,
        column: str = "id",
        with_for_update: bool = False,
    ) -> Optional[EntityModel]:
        """Fetches one record from the database based on a column value and returns
        it, or returns None if it does not exist. Raises an exception if the column
        doesn't exist.

        Args:
            id_ (str): value to search for in `column`.
            column (str, optional): the column name in which to search.
                Defaults to "uuid".
            with_for_update (bool, optional): Should the returned row be locked
                during the lifetime of the current open transactions.
                Defaults to False.

        Raises:
            EntityException: if the column does not exist on the model

        Returns:
            EntityModel: SQLAlchemy model or None
        """
        try:
            q = select(self.model).where(getattr(self.model, column) == id_)
        except AttributeError:
            raise EntityException(
                f"Column {column} not found on {self.model.__tablename__}.",
            )

        if with_for_update:
            q = q.with_for_update()

        results = await self.db_session.execute(q)
        return results.unique().scalar_one_or_none()

    async def get_many_by_ids(
        self,
        ids: Optional[List[str]],
        column: str = "id",
        with_for_update: bool = False,
    ) -> List[EntityModel]:
        """Fetches multiple records from the database based on a column value and
        returns them. Raises an exception if the column doesn't exist.

        Args:
            ids (list[str], optional): list of values to search for in
                `column`. Defaults to None.
            column (str, optional): the column name in which to search
                Defaults to "id".
            with_for_update (bool, optional): Should the returned rows be locked
                during the lifetime of the current open transactions.
                Defaults to False.

        Raises:
            EntityException: if the column does not exist on the model
            NotExistSessionException: if not session append to the calling this method

        Returns:
            list[EntityModel]: list of SQLAlchemy models
        """
        q = select(self.model)
        if ids:
            try:
                q = q.where(getattr(self.model, column).in_(ids))
            except AttributeError:
                raise EntityException(
                    f"Column {column} not found on {self.model.__tablename__}.",
                )

        if with_for_update:
            q = q.with_for_update()

        rows = await self.db_session.execute(q)
        return list(rows.unique().scalars().all())

    async def update_entities(
        self,
    ) -> None:
        """
        Update entities which are attaached to the current session.

        Args:
        Raises:
        Returns:
        """
        await self.db_session.flush()

    async def update_by_id(
        self,
        data: EntitySchema,
        id_: str,
        column: str = "id",
    ) -> EntityModel:
        """Updates a record in the database based on a column value and returns the
        updated record. Raises an exception if the record isn't found or if the
        column doesn't exist.

        Args:
            data (EntitySchema): Pydantic schema for the updated data.
            id_ (str | UUID): value to search for in `column`
            column (str, optional): the column name in which to search
                Defaults to "uuid".
        Raises:
            NotFoundException: if the record isn't found
            IntegrityConflictException: if the update conflicts with existing data

        Returns:
            EntityModel: updated SQLAlchemy model
        """
        db_model = await self.get_one_by_id(id_, column, True)
        if not db_model:
            raise NotFoundException(
                f"{self.model.__tablename__} {column}={id_} not found.",
            )

        values = data.model_dump(exclude_unset=True)
        for k, v in values.items():
            setattr(db_model, k, v)

        try:
            await self.db_session.flush()
            return db_model
        except IntegrityError:
            raise IntegrityConflictException(
                f"{self.model.__tablename__} {column}={id_} conflict with existing data.",
            )

    async def update_many_by_ids(
        self,
        updates: Dict[str, EntitySchema],
        column: str = "id",
    ) -> List[EntityModel]:
        """Updates multiple records in the database based on a column value and
        returns the updated records. Raises an exception if the column doesn't
        exist.

        Args:
            session (Optional[AsyncSession]): SQLAlchemy async session
            updates (dict[str  |  UUID, EntitySchema]): dictionary of id_ to
                Pydantic update schema
            column (str, optional): the column name in which to search.
                Defaults to "uuid".
            return_models (bool, optional): Should the created models be returned
                or a boolean indicating they have been created. Defaults to False.
                Defaults to False.

        Raises:
            IntegrityConflictException: if the update conflicts with existing data

        Returns:
            list[EntityModel] | bool: list of updated SQLAlchemy models or boolean
        """
        updates = {str(id): update for id, update in updates.items() if update}
        ids = list(updates.keys())
        db_models = await self.get_many_by_ids(
            ids=ids, column=column, with_for_update=True
        )

        for db_model in db_models:
            values = updates[str(getattr(db_model, column))].model_dump(
                exclude_unset=True
            )
            for k, v in values.items():
                setattr(db_model, k, v)

        try:
            await self.db_session.flush()
        except IntegrityError:
            raise IntegrityConflictException(
                f"{self.model.__tablename__} conflict with existing data.",
            )
        return db_models

    async def remove_by_id(
        self,
        id_: str,
        column: str = "id",
    ) -> int:
        """Removes a record from the database based on a column value. Raises an
        exception if the column doesn't exist.

        Args:
            id (str | UUID): value to search for in `column` and delete
            column (str, optional): the column name in which to search.
                Defaults to "uuid".

        Raises:
            EntityException: if the column does not exist on the model

        Returns:
            int: number of rows removed, 1 if successful, 0 if not. Can be greater
                than 1 if id_ is not unique in the column.
        """
        try:
            query = delete(self.model).where(getattr(self.model, column) == id_)
        except AttributeError:
            raise EntityException(
                f"Column {column} not found on {self.model.__tablename__}.",
            )

        rows = await self.db_session.execute(query)
        await self.db_session.flush()
        return rows.rowcount

    async def remove_many_by_ids(
        self,
        ids: List[str],
        column: str = "id",
    ) -> int:
        """Removes multiple records from the database based on a column value.
        Raises an exception if the column doesn't exist.

        Args:
            ids (list[str  |  UUID]): list of values to search for in `column` and
            column (str, optional): the column name in which to search.
                Defaults to "uuid".

        Raises:
            EntityException: if ids is empty to stop deleting an entire table
            EntityException: if column does not exist on the model

        Returns:
            int: _description_
        """
        if not ids:
            raise EntityException("No ids provided.")

        try:
            query = delete(self.model).where(getattr(self.model, column).in_(ids))
        except AttributeError:
            raise EntityException(
                f"Column {column} not found on {self.model.__tablename__}.",
            )

        rows = await self.db_session.execute(query)
        await self.db_session.flush()
        return rows.rowcount
