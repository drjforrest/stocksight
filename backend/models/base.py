from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

# Create a metadata object with naming conventions for constraints
convention = {
    "ix": "ix_%(column_0_label)s",  # Index
    "uq": "uq_%(table_name)s_%(column_0_name)s",  # Unique constraint
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # Check constraint
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # Foreign key
    "pk": "pk_%(table_name)s"  # Primary key
}

# Create MetaData instance with naming convention
metadata = MetaData(naming_convention=convention)

# Create declarative base that uses this metadata
Base = declarative_base(metadata=metadata)
