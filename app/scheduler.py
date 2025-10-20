"""Appointment scheduling utilities for the dental clinic voice assistant."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional


@dataclass
class Appointment:
    """Represents a single appointment entry."""

    patient_name: str
    reason: str
    scheduled_at: datetime
    contact: str
    metadata: Dict[str, str] = field(default_factory=dict)

    @property
    def date_key(self) -> str:
        """Return a calendar day identifier for grouping appointments."""

        return self.scheduled_at.strftime("%Y-%m-%d")


class AppointmentScheduler:
    """In-memory scheduler with simple conflict management."""

    def __init__(self, slot_duration_minutes: int = 30) -> None:
        self._slot_duration = timedelta(minutes=slot_duration_minutes)
        self._appointments: List[Appointment] = []

    def add_appointment(self, appointment: Appointment) -> None:
        """Add an appointment if the desired slot is available."""

        if not self.is_slot_available(appointment.scheduled_at):
            raise ValueError("El horario solicitado no está disponible.")
        self._appointments.append(appointment)

    def is_slot_available(self, scheduled_at: datetime) -> bool:
        """Return True when the time slot does not overlap with another appointment."""

        for existing in self._appointments:
            delta = abs(existing.scheduled_at - scheduled_at)
            if delta < self._slot_duration:
                return False
        return True

    def find_appointment(self, patient_name: str) -> Optional[Appointment]:
        """Locate an appointment by patient name."""

        for appointment in self._appointments:
            if appointment.patient_name.lower() == patient_name.lower():
                return appointment
        return None

    def list_appointments(self) -> List[Appointment]:
        """Return a snapshot of all scheduled appointments."""

        return list(self._appointments)


__all__ = [
    "Appointment",
    "AppointmentScheduler",
]
