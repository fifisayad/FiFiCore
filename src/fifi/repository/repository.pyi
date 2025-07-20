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

from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ..models.decorated_base import DecoratedBase

# Generic Type for Pydantic and SQLAlchemy
InterfaceEntityModel = TypeVar("InterfaceEntityModel", bound=DecoratedBase)
InterfaceEntitySchema = TypeVar("InterfaceEntitySchema", bound=BaseModel)

@dataclass
class Repository(Generic[InterfaceEntityModel]):
    model: Type[InterfaceEntityModel]

    async def create(
        self,
        data: Type[InterfaceEntitySchema],
        session: Optional[AsyncSession] = None,
    ) -> InterfaceEntityModel: ...
    @overload
    async def create_many(
        self,
        data: List[InterfaceEntitySchema],
        return_models: Literal[False],
        session: Optional[AsyncSession] = None,
    ) -> bool: ...
    @overload
    async def create_many(
        self,
        data: List[InterfaceEntitySchema],
        return_models: Literal[True],
        session: Optional[AsyncSession] = None,
    ) -> List[InterfaceEntityModel]: ...
    async def create_many(
        self,
        data: List[InterfaceEntitySchema],
        return_models: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> List[InterfaceEntityModel] | bool: ...
    async def get_one_by_id(
        self,
        id_: str,
        column: str = "id",
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> Optional[InterfaceEntityModel]: ...
    async def get_many_by_ids(
        self,
        ids: Optional[List[str]],
        column: str = "id",
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> list[InterfaceEntityModel]: ...
    async def update_entity(
        self,
        entity: InterfaceEntityModel,
        session: Optional[AsyncSession] = None,
    ) -> None: ...
    async def update_by_id(
        self,
        data: Type[InterfaceEntitySchema],
        id_: str,
        column: str = "id",
        session: Optional[AsyncSession] = None,
    ) -> InterfaceEntityModel: ...
    @overload
    async def update_many_by_ids(
        self,
        updates: Dict[str, InterfaceEntitySchema],
        column: str,
        return_models: Literal[False],
        session: Optional[AsyncSession] = None,
    ) -> bool: ...
    @overload
    async def update_many_by_ids(
        self,
        updates: Dict[str, InterfaceEntitySchema],
        column: str,
        return_models: Literal[True],
        session: Optional[AsyncSession] = None,
    ) -> List[InterfaceEntityModel]: ...
    async def update_many_by_ids(
        self,
        updates: Dict[str, InterfaceEntitySchema],
        column: str = "id",
        return_models: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> List[InterfaceEntityModel] | bool: ...
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
