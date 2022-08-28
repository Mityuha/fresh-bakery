"""Get projects capacity."""
from uuid import UUID, uuid4

from loguru import logger

from .base import DeploymentHandler, ProjectCapacityGetter


class ProjectCapacity(ProjectCapacityGetter, DeploymentHandler):
    """Project capacity."""

    def __init__(self, catalog_item_id: UUID):
        super().__init__(catalog_item="PROJECTS_CAPACITY_BOTH", catalog_item_id=catalog_item_id)
        self.project_cache: dict[UUID, str] = {}

    async def fetch_deployments_output(self) -> bool:
        """Override."""
        if not self.waiting_for_output:
            return False

        self.project_cache[uuid4()] = f"[{self.catalog_item}] some project 1"
        self.project_cache[uuid4()] = f"[{self.catalog_item}] some project 2"

        logger.debug(f"{self}: project cache updated")

        self.waiting_for_output = False
        return True

    def keys(self) -> set[UUID]:
        """All projects uuid."""
        return set(self.project_cache.keys())
