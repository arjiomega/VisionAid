import uuid

from sqlalchemy import UUID, Boolean, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class APIKeyDB(Base):
    __tablename__ = "keys_table"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hashed_api_key = Column(String, nullable=False)
    key_fingerprint = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)
    total_requests = Column(Integer, default=0)
    max_requests = Column(Integer, default=5)