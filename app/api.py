"""FastAPI application exposing the dental clinic voice assistant."""
from __future__ import annotations

import uuid
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .conversation import ConversationManager
from .scheduler import AppointmentScheduler
from .voice import VoiceGateway

app = FastAPI(title="Chat de Voz Clínica Dental")
scheduler = AppointmentScheduler()
conversations = ConversationManager(scheduler=scheduler)
voice_gateway = VoiceGateway()


class ChatRequest(BaseModel):
    message: Optional[str] = Field(None, description="Transcripción del paciente")
    session_id: Optional[str] = Field(
        None, description="Identificador de sesión para continuar la conversación"
    )
    audio_base64: Optional[str] = Field(
        None, description="Audio del paciente codificado en base64"
    )


class ChatResponse(BaseModel):
    reply: str
    status: str
    session_id: str
    audio_base64: Optional[str] = None


class AppointmentResponse(BaseModel):
    patient_name: str
    reason: str
    scheduled_at: str
    contact: str


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    """Process chat or voice input and return the assistant's reply."""

    session_id = payload.session_id or str(uuid.uuid4())
    text = payload.message

    if text is None:
        if payload.audio_base64 is None:
            raise HTTPException(
                status_code=400,
                detail="Debes proporcionar un mensaje de texto o audio_base64.",
            )
        if not voice_gateway.available:
            raise HTTPException(
                status_code=503,
                detail="El soporte de voz no está disponible: "
                + (voice_gateway.missing_dependencies or "desconocido"),
            )
        audio_bytes = _decode_base64(payload.audio_base64)
        text = voice_gateway.speech_to_text(audio_bytes)

    result = conversations.process_message(session_id=session_id, message=text)
    reply_audio = None
    if voice_gateway.available:
        try:
            reply_audio = voice_gateway.text_to_speech_base64(result["reply"])
        except RuntimeError:
            reply_audio = None

    return ChatResponse(
        reply=result["reply"],
        status=result["status"],
        session_id=session_id,
        audio_base64=reply_audio,
    )


@app.get("/appointments", response_model=Dict[str, Dict[str, str]])
def list_appointments() -> Dict[str, Dict[str, str]]:
    """Return scheduled appointments grouped by session id."""

    data: Dict[str, Dict[str, str]] = {}
    for appointment in scheduler.list_appointments():
        data_key = appointment.patient_name
        data[data_key] = {
            "reason": appointment.reason,
            "scheduled_at": appointment.scheduled_at.isoformat(),
            "contact": appointment.contact,
        }
    return data


def _decode_base64(encoded: str) -> bytes:
    import base64

    try:
        return base64.b64decode(encoded)
    except base64.binascii.Error as exc:  # type: ignore[attr-defined]
        raise HTTPException(status_code=400, detail="Audio inválido") from exc


__all__ = ["app"]
