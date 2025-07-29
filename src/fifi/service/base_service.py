from abc import ABC, abstractmethod
from typing import Dict, Generic, List, Optional, TypeVar

from ..repository.repository import Repository
from ..models.decorated_base import DecoratedBase
from pydantic import BaseModel


EntityModel = TypeVar("EntityModel", bound=DecoratedBase)
EntitySchema = TypeVar("EntitySchema", bound=BaseModel)


class BaseService(ABC, Generic[EntityModel, EntitySchema]):
    """
    Abstract base service class that defines generic CRUD operations for an entity.

    This class uses a repository pattern to abstract database interactions and operates
    on generic types for the entity model and its corresponding schema.

    Type Parameters:
        EntityModel: A subclass of `DecoratedBase`, representing the database model.
        EntitySchema: A subclass of `BaseModel`, representing the data schema used for input.

    Subclasses must implement the `repo` property to provide the concrete repository.
    """

    @property
    @abstractmethod
    def repo(self) -> Repository:
        """
        Abstract property to be implemented by subclasses to return the repository instance
        for the service to perform CRUD operations on.

        Returns:
            Repository: The repository handling data persistence.
        """
        pass

    async def create(self, data: EntitySchema) -> EntityModel:
        """
        Create a single entity record in the database.

        Args:
            data (EntitySchema): The data for the entity to be created.

        Returns:
            EntityModel: The created entity instance.
        """
        return await self.repo.create(data=data)

    async def create_many(self, data: List[EntitySchema]) -> List[EntityModel]:
        """
        Create multiple entity records in the database.

        Args:
            data (List[EntitySchema]): A list of data schemas for the entities to be created.

        Returns:
            List[EntityModel]: A list of created entity instances.
        """
        return await self.repo.create_many(data=data)

    async def read_by_id(self, id_: str) -> Optional[EntityModel]:
        """
        Retrieve a single entity by its ID.

        Args:
            id (str): The ID of the entity to retrieve.

        Returns:
            Optional[EntityModel]: The entity instance if found, otherwise None.
        """
        return await self.repo.get_one_by_id(id_=id_)

    async def read_many_by_ids(self, ids: List[str]) -> List[EntityModel]:
        """
        Retrieve multiple entities by their IDs.

        Args:
            ids (List[str]): A list of entity IDs to retrieve.

        Returns:
            List[EntityModel]: A list of found entity instances.
        """
        return await self.repo.get_many_by_ids(ids=ids)

    async def update_entity(self, entity: EntityModel) -> None:
        """
        Update an entity instance directly.

        Args:
            entity (EntityModel): The entity instance with updated values.

        Returns:
            None
        """
        return await self.repo.update_entity(entity=entity)

    async def update_by_id(self, id_: str, data: EntitySchema) -> EntityModel:
        """
        Update an entity by its ID using the provided data.

        Args:
            id (str): The ID of the entity to update.
            data (EntitySchema): The new data for the entity.

        Returns:
            EntityModel: The updated entity instance.
        """
        return await self.repo.update_by_id(id_=id_, data=data)

    async def update_many_by_ids(
        self, data: Dict[str, EntitySchema]
    ) -> List[EntityModel]:
        """
        Update multiple entities by their IDs with corresponding data.

        Args:
            ids (List[str]): The list of entity IDs to update.
            data (List[EntitySchema]): A list of new data schemas, one for each entity.

        Returns:
            List[EntityModel]: A list of updated entity instances.
        """
        return await self.repo.update_many_by_ids(updates=data)

    async def remove_by_id(self, id_: str) -> int:
        """
        Remove an entity by its ID.

        Args:
            id (str): The ID of the entity to delete.

        Returns:
            int: The number of entities removed (typically 1 or 0).
        """
        return await self.repo.remove_by_id(id_=id_)

    async def remove_many_by_ids(self, ids: List[str]) -> int:
        """
        Remove multiple entities by their IDs.

        Args:
            ids (List[str]): A list of IDs for entities to delete.

        Returns:
            int: The number of entities successfully removed.
        """
        return await self.repo.remove_many_by_ids(ids=ids)
