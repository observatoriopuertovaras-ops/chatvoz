"""Rule-based conversation flow for the dental clinic assistant."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

from dateutil import parser

from .scheduler import Appointment, AppointmentScheduler


@dataclass
class ConversationContext:
    """Stores collected information for a single conversation."""

    patient_name: Optional[str] = None
    reason: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    contact: Optional[str] = None
    confirmed: bool = False

    metadata: Dict[str, str] = field(default_factory=dict)

    def is_ready_for_confirmation(self) -> bool:
        return all(
            [
                self.patient_name,
                self.reason,
                self.scheduled_at,
                self.contact,
            ]
        )


class ConversationManager:
    """Handle stateful conversations for multiple sessions."""

    def __init__(self, scheduler: AppointmentScheduler) -> None:
        self.scheduler = scheduler
        self.sessions: Dict[str, ConversationContext] = {}

    def get_context(self, session_id: str) -> ConversationContext:
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationContext()
        return self.sessions[session_id]

    def reset_context(self, session_id: str) -> None:
        if session_id in self.sessions:
            del self.sessions[session_id]

    def process_message(self, session_id: str, message: str) -> Dict[str, str]:
        """Process the next user input and return the assistant's response."""

        context = self.get_context(session_id)
        cleaned = message.strip().lower()

        # Allow the user to cancel the current process.
        if "cancelar" in cleaned or "cancel" in cleaned:
            self.reset_context(session_id)
            return {
                "reply": "He cancelado la cita en curso. ¿Necesitas algo más?",
                "status": "cancelled",
            }

        # Confirmation branch
        if context.is_ready_for_confirmation() and not context.confirmed:
            if "si" in cleaned or "sí" in cleaned:
                appointment = Appointment(
                    patient_name=context.patient_name or "",
                    reason=context.reason or "",
                    scheduled_at=context.scheduled_at or datetime.now(),
                    contact=context.contact or "",
                    metadata=context.metadata,
                )
                try:
                    self.scheduler.add_appointment(appointment)
                except ValueError as error:
                    context.confirmed = False
                    return {
                        "reply": str(error)
                        + " ¿Deseas intentar con otro horario?",
                        "status": "conflict",
                    }
                context.confirmed = True
                return {
                    "reply": (
                        "Perfecto, he agendado tu cita para "
                        f"{appointment.scheduled_at:%d/%m/%Y a las %H:%M}."
                        " ¿En qué más puedo ayudarte?"
                    ),
                    "status": "scheduled",
                }

            if "no" in cleaned:
                context.scheduled_at = None
                context.confirmed = False
                return {
                    "reply": "Sin problema. Indícame otra fecha y hora que prefieras.",
                    "status": "needs_datetime",
                }

        # Collect missing fields sequentially
        if context.patient_name is None:
            context.patient_name = message.strip()
            return {
                "reply": "Encantado, {0}. ¿Cuál es el motivo de tu visita?".format(
                    context.patient_name
                ),
                "status": "needs_reason",
            }

        if context.reason is None:
            context.reason = message.strip()
            return {
                "reply": (
                    "Perfecto. ¿Qué día y hora te gustaría venir?"
                    " (por ejemplo: '15 de mayo a las 10 am')."
                ),
                "status": "needs_datetime",
            }

        if context.scheduled_at is None:
            parsed_date = _parse_datetime(message)
            if not parsed_date:
                return {
                    "reply": (
                        "No pude entender la fecha y hora."
                        " Intenta con un formato como '20 de junio a las 16:30'."
                    ),
                    "status": "invalid_datetime",
                }
            if not self.scheduler.is_slot_available(parsed_date):
                return {
                    "reply": "Ese horario no está disponible. ¿Quieres elegir otro?",
                    "status": "conflict",
                }
            context.scheduled_at = parsed_date
            return {
                "reply": "Anotado. ¿Cuál es tu número de contacto?",
                "status": "needs_contact",
            }

        if context.contact is None:
            context.contact = message.strip()
            return {
                "reply": (
                    "Gracias. ¿Confirmamos la cita para {0:%d/%m/%Y a las %H:%M}?"
                ).format(context.scheduled_at),
                "status": "awaiting_confirmation",
            }

        # Already scheduled, continue conversation generically
        return {
            "reply": "Tu cita sigue confirmada. ¿Necesitas algo más?",
            "status": "completed",
        }


def _parse_datetime(text: str) -> Optional[datetime]:
    """Parse natural language dates using dateutil, returning None on failure."""

    try:
        dt = parser.parse(text, dayfirst=True, fuzzy=True)
    except (ValueError, OverflowError, TypeError):
        return None
    return dt


__all__ = ["ConversationManager", "ConversationContext"]
