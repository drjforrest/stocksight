import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, text
from alembic import context
from dotenv import load_dotenv

# Add the parent directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root)

# Load environment variables from .env file
dotenv_path = os.path.join(project_root, 'backend', '.env')
load_dotenv(dotenv_path)

# this is the Alembic Config object, which provides
# access to the values within the .env file in use.
config = context.config

# Set the database URL in the alembic.ini file
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")
if not isinstance(DATABASE_URL, str):
    raise TypeError("DATABASE_URL must be a string")

SCHEMA = "stocksight"

# Override sqlalchemy.url in alembic.ini
config.set_main_option('sqlalchemy.url', str(DATABASE_URL))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from config.database import Base

def include_object(object, name, type_, reflected, compare_to):
    """Determine which database objects should be included in the autogeneration."""
    # Include objects in our schema and exclude others
    if type_ == "table":
        return object.schema == SCHEMA
    return True

def process_revision_directives(context, revision, directives):
    """Process revision directives to ensure schema is set correctly."""
    if config.cmd_opts and config.cmd_opts.autogenerate:
        script = directives[0]
        if script.upgrade_ops.ops:
            # Set schema for create_table operations
            for op in script.upgrade_ops.ops:
                if hasattr(op, 'schema') and op.schema is None:
                    op.schema = SCHEMA

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=SCHEMA,
        include_schemas=True,
        include_object=include_object,
        process_revision_directives=process_revision_directives
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Add the search_path setting to the connection URL
    ini_section = config.get_section(config.config_ini_section)
    ini_section['sqlalchemy.url'] = f"{ini_section['sqlalchemy.url']}?options=-csearch_path%3D{SCHEMA}"

    connectable = engine_from_config(
        ini_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Create schema if it doesn't exist
        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}"))
        connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=SCHEMA,
            include_schemas=True,
            include_object=include_object,
            process_revision_directives=process_revision_directives
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 