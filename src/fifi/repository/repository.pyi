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

from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ..models.decorated_base import DecoratedBase

# Generic Type for Pydantic and SQLAlchemy
EntityModel = TypeVar("EntityModel", bound=DecoratedBase)
EntitySchema = TypeVar("EntitySchema", bound=BaseModel)

class Repository(Generic[EntityModel]):
    model: Type[EntityModel]

    async def create(
        self,
        data: Type[EntitySchema],
        session: Optional[AsyncSession] = None,
    ) -> EntityModel: ...
    @overload
    async def create_many(
        self,
        data: list[EntitySchema],
        return_models: Literal[False],
        session: Optional[AsyncSession] = None,
    ) -> bool: ...
    @overload
    async def create_many(
        self,
        data: list[EntitySchema],
        return_models: Literal[True],
        session: Optional[AsyncSession] = None,
    ) -> List[EntityModel]: ...
    async def create_many(
        self,
        data: list[EntitySchema],
        return_models: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> List[EntityModel] | bool: ...
    async def get_one_by_id(
        self,
        id_: str,
        column: str = "id",
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> Optional[EntityModel]: ...
    async def get_many_by_ids(
        self,
        ids: Optional[list[str]],
        column: str = "id",
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> list[EntityModel]: ...
    async def update_entity(
        self,
        entity: EntityModel,
        session: Optional[AsyncSession] = None,
    ) -> None: ...
    async def update_by_id(
        self,
        data: Type[EntitySchema],
        id_: str,
        column: str = "id",
        session: Optional[AsyncSession] = None,
    ) -> EntityModel: ...
    @overload
    async def update_many_by_ids(
        self,
        updates: Dict[str, EntitySchema],
        column: str,
        return_models: Literal[False],
        session: Optional[AsyncSession] = None,
    ) -> bool: ...
    @overload
    async def update_many_by_ids(
        self,
        updates: Dict[str, EntitySchema],
        column: str,
        return_models: Literal[True],
        session: Optional[AsyncSession] = None,
    ) -> List[EntityModel]: ...
    async def update_many_by_ids(
        self,
        updates: Dict[str, EntitySchema],
        column: str = "id",
        return_models: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> List[EntityModel] | bool: ...
    async def remove_by_id(
        self,
        id_: str,
        column: str = "id",
        session: Optional[AsyncSession] = None,
    ) -> int: ...
    async def remove_many_by_ids(
        self,
        ids: List[str],
        column: str = "id",
        session: Optional[AsyncSession] = None,
    ) -> int: ...
