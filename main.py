"""Entry point for running the FastAPI server or a CLI demo."""
from __future__ import annotations

import argparse
import uvicorn

from app.api import app, conversations


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Launch the FastAPI server using Uvicorn."""

    uvicorn.run(app, host=host, port=port)


def run_cli() -> None:
    """Simple CLI conversation useful for manual testing."""

    session_id = "cli-demo"
    print("Asistente: ¡Hola! Soy tu asistente virtual de la clínica dental.")
    print("Asistente: ¿Cómo te llamas?")
    while True:
        try:
            user_input = input("Paciente: ")
        except (EOFError, KeyboardInterrupt):
            print("\nAsistente: Hasta luego.")
            break
        result = conversations.process_message(session_id=session_id, message=user_input)
        print("Asistente:", result["reply"])
        if result["status"] in {"scheduled", "completed"}:
            print("Asistente: Puedes escribir 'cancelar' para empezar de nuevo.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat de voz para clínica dental")
    parser.add_argument(
        "--mode",
        choices=["server", "cli"],
        default="cli",
        help="Modo de ejecución",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host del servidor")
    parser.add_argument("--port", type=int, default=8000, help="Puerto del servidor")
    args = parser.parse_args()

    if args.mode == "server":
        run_server(host=args.host, port=args.port)
    else:
        run_cli()


if __name__ == "__main__":
    main()
