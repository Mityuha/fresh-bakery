"""Cron base."""

from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from typing import Any, Iterator, Optional
from uuid import UUID

from aiocron import crontab  # type: ignore
from loguru import logger


class ProjectCapacityGetter(metaclass=ABCMeta):
    """Interfaces."""

    @abstractmethod
    def keys(self) -> set[UUID]:
        """Keys."""


def singleton(cls):
    """Singleton."""
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return get_instance


class DeploymentHandler(metaclass=ABCMeta):
    """Deployment handler."""

    def __init__(self, catalog_item: str, catalog_item_id: UUID):
        self.catalog_item: str = catalog_item
        self.catalog_item_id: UUID = catalog_item_id
        self.waiting_for_output: bool = False

    @abstractmethod
    async def fetch_deployments_output(self) -> bool:
        """Some abstact method."""

    def __str__(self) -> str:
        return self.catalog_item

    async def request_deployment(self, **kwargs: Any) -> None:  # pylint:disable=unused-argument
        """Request deployment."""
        self.waiting_for_output = True
        logger.debug(
            f"Deployment for catalog_item {self.catalog_item} ({self.catalog_item_id} requested)"
        )


class CronEvents:
    """Cron events class."""

    def __init__(
        self,
        handler: DeploymentHandler,
        fetch_deployments_output_spec: Optional[str],
        request_deployment_spec: Optional[str],
    ):
        self.handler = handler
        self.fetch_deployments_output_cron = crontab(
            fetch_deployments_output_spec, func=self.handler.fetch_deployments_output, start=False
        )
        self.request_deployment_cron = crontab(
            request_deployment_spec, func=self.handler.request_deployment, start=False
        )

    @classmethod
    @contextmanager
    def init_and_start(cls, *args: Any, **kwargs: Any) -> Iterator["CronEvents"]:
        """Create and start cron events, shutdown it after all."""
        cron_events: CronEvents = cls(*args, **kwargs)
        cron_events.start()
        yield cron_events
        cron_events.stop()

    def start(self) -> None:
        """Start cron."""
        print("starting...")
        if any([self.fetch_deployments_output_cron.spec, self.request_deployment_cron.spec]):
            logger.debug(f"Cron events with {self.handler} started.")
        if self.fetch_deployments_output_cron.spec:
            self.fetch_deployments_output_cron.start()
        if self.request_deployment_cron.spec:
            self.request_deployment_cron.start()

    def stop(self) -> None:
        """Stop cron."""
        logger.debug(f"Cron events with {self.handler} stopped.")
        self.fetch_deployments_output_cron.stop()
        self.request_deployment_cron.stop()
