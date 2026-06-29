#!/usr/bin/env python3
"""Prueba de listado por labels y recuperacion desde trash."""

import os
import sys

try:
    from agentmail import AgentMail
except ImportError:
    print("Error: agentmail package not found.")
    sys.exit(1)

INBOX = "skynetclaw@agentmail.to"


def _get_attr(obj, name, default=None):
    return getattr(obj, name, default)


def main():
    api_key = os.getenv("AGENTMAIL_API_KEY")
    if not api_key:
        print("Error: AGENTMAIL_API_KEY not set")
        sys.exit(1)

    client = AgentMail(api_key=api_key)

    print("Intentando listar mensajes con labels=['trash']...")
    try:
        response = client.inboxes.messages.list(
            inbox_id=INBOX,
            labels=["trash"],
            limit=200,
        )
        msgs = getattr(response, 'messages', [])
        print(f"Mensajes en trash: {len(msgs)}")
        for m in msgs:
            mid = _get_attr(m, 'message_id')
            subj = _get_attr(m, 'subject', '(sin asunto)')
            print(f" ID: {mid} | Asunto: {subj}")
    except Exception as e:
        print(f"Error listando con labels: {e}")
        return

    if not msgs:
        print("No hay mensajes en trash.")
        return

    print("\nRecuperando mensajes (remove_labels=['trash'])...")
    recuperados = 0
    fallidos = []
    for m in msgs:
        mid = _get_attr(m, 'message_id')
        if not mid:
            continue
        try:
            client.inboxes.messages.update(
                inbox_id=INBOX,
                message_id=mid,
                remove_labels=["trash"],
            )
            recuperados += 1
        except Exception as e:
            print(f" Error recuperando {mid}: {e}")
            fallidos.append(mid)

    print("\n=== RECUPERACIÓN ===")
    print(f"Intentados: {len(msgs)}")
    print(f"Recuperados: {recuperados}")
    print(f"Fallidos: {len(fallidos)}")


if __name__ == '__main__':
    main()
