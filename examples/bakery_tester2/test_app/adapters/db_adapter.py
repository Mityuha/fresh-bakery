"""Database adapter."""

from typing import Any, Mapping, Optional

from databases import Database
from databases.interfaces import Record
from loguru import logger


class ServiceDatabase:
    """Service database."""

    def __init__(self, connection: Database) -> None:
        self._connection: Database = connection

    async def __aenter__(self) -> "ServiceDatabase":
        """On startup."""
        await self._connection.connect()
        return self

    async def __aexit__(self, *_args: Any) -> None:
        """On shutdown."""
        await self._connection.disconnect()

    async def fetch_person(self, person_id: int) -> Mapping:
        """Fetch tenant table data by tenant name."""

        query: str = """
        SELECT *
        FROM person p
        WHERE p.id=:person_id;"""

        values: dict[str, int] = dict(person_id=person_id)

        logger.debug(f"Get person by id {query = }, {values = }")

        row: Optional[Record] = await self._connection.fetch_one(
            query=query,
            values=values,
        )
        return row if row else {}  # type: ignore

    async def insert_person(self, first_name: str, second_name: str, age: int) -> int:
        """Insert person."""
        query: str = """
        INSERT INTO person(first_name, second_name, age)
        VALUES (:first_name, :second_name, :age)
        RETURNING id"""

        values: dict = dict(
            first_name=first_name,
            second_name=second_name,
            age=age,
        )

        logger.debug(f"Insert into person table {query = }, {values = }")

        return await self._connection.fetch_val(query=query, values=values)
