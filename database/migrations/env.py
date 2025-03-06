import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, text
from alembic import context
from dotenv import load_dotenv

# Add the parent directory to Python path so we can import our models
import sys
# Get absolute path to the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)  # Insert at beginning of path to take precedence

# Load environment variables from backend/.env
load_dotenv(os.path.join(project_root, 'backend', '.env'))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the database URL in the alembic.ini file
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
SCHEMA = "stocksight"

# Override sqlalchemy.url in alembic.ini
config.set_main_option('sqlalchemy.url', 
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from backend.models.stock import Base

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