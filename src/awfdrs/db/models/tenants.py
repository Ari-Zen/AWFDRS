"""
Tenant model for multi-tenancy support.
"""

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.awfdrs.db.base import BaseModel


class Tenant(BaseModel):
    """
    Tenant model for isolating customer data.

    Attributes:
        name: Tenant name
        encryption_key_id: Reference to encryption key for sensitive data
        is_active: Whether tenant is active
        workflows: Associated workflows
    """

    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    encryption_key_id: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships will be added when we create the related models
    # workflows: Mapped[list["Workflow"]] = relationship(back_populates="tenant")
    # events: Mapped[list["Event"]] = relationship(back_populates="tenant")
