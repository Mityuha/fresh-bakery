"""Service controller."""

from typing import Mapping, Optional, Protocol

from loguru import logger
from pydantic import BaseModel  # pylint: disable=no-name-in-module


class DatabaseInterface(Protocol):
    """Database interface."""

    async def fetch_person(self, person_id: int) -> Mapping:
        """Fetch person."""

    async def insert_person(self, first_name: str, second_name: str, age: int) -> int:
        """Insert person."""


class PersonIn(BaseModel):
    """Person in."""

    first_name: str
    second_name: str
    age: int


class PersonOut(PersonIn):
    """Person out."""

    person_id: int


class ServiceController:
    """Service controller."""

    def __init__(
        self,
        *,
        database: DatabaseInterface,
        logger_name: str,
    ):
        """Init."""

        self._database = database
        self._logger_name = logger_name

    def __repr__(self) -> str:
        return self._logger_name

    async def insert_person(self, person: PersonIn, /) -> int:
        """Insert person.

        return id.
        """
        logger.debug(f"{self}: inserting person {person}")
        person_id: int = await self._database.insert_person(
            first_name=person.first_name,
            second_name=person.second_name,
            age=person.age,
        )
        logger.debug(f"{self}: person successfully inserted with id {person_id}")
        return person_id

    async def fetch_person(self, person_id: int, /) -> Optional[PersonOut]:
        """Fetch person by id."""
        logger.debug(f"{self}: fetching person by id {person_id}")
        person: Optional[Mapping] = await self._database.fetch_person(person_id)
        if not person:
            logger.info(f"{self}: person {person_id} not found.")
            return None

        res: PersonOut = PersonOut(
            first_name=person["first_name"],
            second_name=person["second_name"],
            age=person["age"],
            person_id=person["id"],
        )
        logger.info(f"{self}: person {person_id} found: {res}")
        return res
