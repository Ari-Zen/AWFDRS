"""
Database models package.
Import all models here to ensure they are registered with SQLAlchemy.
"""

from src.awfdrs.db.models.tenants import Tenant
from src.awfdrs.db.models.workflows import Workflow
from src.awfdrs.db.models.vendors import Vendor
from src.awfdrs.db.models.events import Event
from src.awfdrs.db.models.incidents import Incident
from src.awfdrs.db.models.decisions import Decision
from src.awfdrs.db.models.actions import Action
from src.awfdrs.db.models.kill_switches import KillSwitch

__all__ = [
    "Tenant",
    "Workflow",
    "Vendor",
    "Event",
    "Incident",
    "Decision",
    "Action",
    "KillSwitch",
]