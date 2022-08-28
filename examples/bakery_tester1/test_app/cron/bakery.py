"""Bakery."""


from uuid import UUID

from bakery import Bakery, Cake

from .base import CronEvents
from .projects_capacity import ProjectCapacity


class CapacityBakery(Bakery):
    """Project capacity facade."""

    catalog_item_id: UUID = UUID(int=0)
    capacity: ProjectCapacity = Cake(
        ProjectCapacity,
        catalog_item_id=catalog_item_id,
    )


class CronBakery(Bakery):
    """Cron handler."""

    # callable and then contextmanager
    _cron_events = Cake(
        Cake(
            CronEvents.init_and_start,
            handler=CapacityBakery.capacity,
            request_deployment_spec="*/1 * * * *",
            fetch_deployments_output_spec="* * * * * 25",
        )
    )
