from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import get_settings
from app.core.database import Base

# Import every module's models so Base.metadata is fully populated for
# autogenerate. Each domain module registers its own tables here.
from app.modules.animal import lookups as _animal_lookups  # noqa: F401
from app.modules.animal import models as _animal_models  # noqa: F401
from app.modules.pen import lookups as _pen_lookups  # noqa: F401
from app.modules.pen import models as _pen_models  # noqa: F401
from app.modules.genetic_resource import models as _genetic_resource_models  # noqa: F401
from app.modules.weight import lookups as _weight_lookups  # noqa: F401
from app.modules.weight import models as _weight_models  # noqa: F401
from app.modules.breeding import lookups as _breeding_lookups  # noqa: F401
from app.modules.breeding import models as _breeding_models  # noqa: F401
from app.modules.health import lookups as _health_lookups  # noqa: F401
from app.modules.health import models as _health_models  # noqa: F401
from app.modules.feed import lookups as _feed_lookups  # noqa: F401
from app.modules.feed import models as _feed_models  # noqa: F401
from app.modules.sale import lookups as _sale_lookups  # noqa: F401
from app.modules.sale import models as _sale_models  # noqa: F401
from app.modules.death import lookups as _death_lookups  # noqa: F401
from app.modules.death import models as _death_models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", get_settings().database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
