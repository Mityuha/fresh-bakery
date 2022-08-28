"""Almost auto-generated file."""


from pydantic import BaseSettings, Field, PostgresDsn

from alembic import context


from sqlalchemy import create_engine  # pylint: disable=wrong-import-order  # isort:skip


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None  # pylint: disable=invalid-name

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


class ServiceSettings(BaseSettings):
    """Service settings."""

    postgres_dsn: PostgresDsn = Field(
        default="postgresql://bakery_tester:bakery_tester@0.0.0.0/bakery_tester"
    )


def get_dsn():
    """Get database DSN."""
    return ServiceSettings().postgres_dsn


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    context.configure(
        url=get_dsn(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = create_engine(get_dsn())

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
