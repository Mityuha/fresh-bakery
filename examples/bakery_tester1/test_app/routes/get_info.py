"""Get info routes."""

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..bakery import MainBakery
from ..cron.base import ProjectCapacityGetter


router: APIRouter = APIRouter()


class Response(BaseModel):
    """Response."""

    projects: list[UUID]
    networks: list[str]


@router.get("/", response_model=Response)
async def info(
    projects_capacity: ProjectCapacityGetter = Depends(MainBakery.projects.capacity),
) -> dict:
    """Info endpoint."""
    return dict(projects=projects_capacity.keys(), networks=[])
