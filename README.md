# Chat de Voz para Clínica Dental

Este proyecto implementa un asistente conversacional enfocado en la agenda de una
clínica dental. Incluye:

- **API REST con FastAPI** para conversar vía texto o audio.
- **Motor de diálogo** con flujo guiado para agendar citas.
- **Integración opcional de voz** mediante `SpeechRecognition` y `pyttsx3` para
  convertir audio a texto y respuestas a audio.
- **CLI de demostración** para interactuar desde la terminal.

## Requisitos

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **Nota:** La síntesis y reconocimiento de voz requieren dependencias de
> `pyttsx3` y `SpeechRecognition`. En algunos sistemas podrías necesitar
> instalar paquetes del sistema (por ejemplo `portaudio`) para que funcionen
> correctamente.

## Uso rápido

### Ejecutar el modo CLI

```bash
python main.py --mode cli
```

### Ejecutar el servidor FastAPI

```bash
python main.py --mode server --host 0.0.0.0 --port 8000
```

Una vez en marcha, puedes enviar mensajes al endpoint `/chat`:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola", "session_id": "usuario-1"}'
```

La respuesta incluirá el mensaje del asistente, el estado del flujo y, si las
bibliotecas de voz están disponibles, el audio generado en base64.

### Listar citas

```bash
curl http://localhost:8000/appointments
```

## Flujo conversacional

1. El asistente saluda y solicita el nombre del paciente.
2. Pregunta el motivo de la visita.
3. Solicita fecha y hora deseada y valida la disponibilidad.
4. Pide un medio de contacto.
5. Confirma la cita y la guarda en memoria.

Puedes escribir `cancelar` en cualquier momento para reiniciar el proceso.

## Personalización

- Ajusta la duración de las citas modificando el parámetro
  `slot_duration_minutes` en `AppointmentScheduler`.
- Amplía el flujo conversacional en `app/conversation.py`, por ejemplo
  agregando preguntas de prediagnóstico o recordatorios.
- Integra un almacenamiento persistente reemplazando el scheduler en memoria
  por una base de datos.

## Pruebas manuales sugeridas

1. Interactúa con el modo CLI para validar el flujo de preguntas.
2. Usa una herramienta como Hoppscotch o curl para probar el endpoint `/chat`.
3. Verifica que al confirmar una cita se refleje en `/appointments`.
