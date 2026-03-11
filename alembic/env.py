from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

from app.core.config import settings
from app.db.session import Base
from app.models.user import User
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.issue import Issue
from app.models.comment import Comment
from app.models.activity_log import ActivityLog
from app.models.label import Label
from app.models.issue_label import IssueLabel

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use URL already provided to Alembic config if present.
# If not, fall back to the app DATABASE_URL.
database_url = config.get_main_option("sqlalchemy.url")
if not database_url or database_url == "driver://user:pass@localhost/dbname":
    database_url = settings.DATABASE_URL
    config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = database_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()