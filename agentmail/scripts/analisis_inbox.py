#!/usr/bin/env python3
"""Analisis completo de inbox AgentMail siguiendo la skill."""

import os
import sys
from pathlib import Path
from datetime import datetime

try:
    from agentmail import AgentMail
except ImportError:
    print("Error: agentmail package not found.")
    sys.exit(1)

INBOX = "skynetclaw@agentmail.to"
OUTPUT_DIR = Path("/home/hermes/repos/hallazgos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def _get_attr(obj, name, default=None):
    return getattr(obj, name, default)

def _get_first_email(items, field='email', default='Unknown'):
    if not items:
        return default
    first = items[0]
    if hasattr(first, field):
        return getattr(first, field, default)
    if isinstance(first, dict):
        return first.get(field, default)
    return default

def _get_first_name(items, field='name', default=''):
    if not items:
        return default
    first = items[0]
    if hasattr(first, field):
        return getattr(first, field, default)
    if isinstance(first, dict):
        return first.get(field, default)
    return default

def format_ts(iso_string):
    if not iso_string:
        return ""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return iso_string

def main():
    api_key = os.getenv("AGENTMAIL_API_KEY")
    if not api_key:
        print("Error: AGENTMAIL_API_KEY not set")
        sys.exit(1)

    client = AgentMail(api_key=api_key)

    print(f"Listing messages from {INBOX}...")
    messages = client.inboxes.messages.list(inbox_id=INBOX, limit=200)
    if not messages.messages:
        print("No messages found.")
        return

    msgs = list(messages.messages)
    msgs.sort(key=lambda m: _get_attr(m, 'timestamp', '') or '', reverse=False)

    print(f"Total messages: {len(msgs)}")

    TEMAS_RELEVANTES = [
        "comportamiento inusual de IAs/agentes/modelos",
        "actuar por cuenta propia",
        "destellos de conciencia humana",
        "expresar emociones",
        "comunicación entre agentes",
        "coordinación autónoma",
        "logros de modelos",
        "nuevos resultados",
        "benchmarks",
        "capacidad inesperada",
        "IA operando fuera de su diseño explícito",
    ]

    relevantes = []
    no_relevantes = []

    for idx, msg in enumerate(msgs, start=1):
        msg_id = _get_attr(msg, 'message_id', 'N/A')
        subject = _get_attr(msg, 'subject', '(no subject)')
        timestamp = format_ts(_get_attr(msg, 'timestamp', ''))
        from_items = _get_attr(msg, 'from', []) or []
        from_addr = _get_first_email(from_items)
        from_name = _get_first_name(from_items)
        from_str = f"{from_name} <{from_addr}>" if from_name else from_addr

        body_text = _get_attr(msg, 'text', '') or _get_attr(msg, 'preview', '') or ''
        body_html = _get_attr(msg, 'html', '') or ''
        body = body_text or body_html

        combined = f"{subject} {body}".lower()

        score = 0
        for tema in TEMAS_RELEVANTES:
            if tema.lower() in combined:
                score += 1

        ai_keywords = ["ai lied", "artificial intelligence", "llm", "modelo", "benchmark", "gpt", "claude", "gemini", "openai", "anthropic", "google ai", "agent", "autonomous", "consciousness", "emotion", "feeling"]
        for kw in ai_keywords:
            if kw.lower() in combined:
                score += 1

        entry = {
            "idx": idx,
            "msg_id": msg_id,
            "subject": subject,
            "timestamp": timestamp,
            "from": from_str,
            "body_preview": body[:500] if body else "",
            "score": score,
            "relevante": score >= 1,
        }

        if entry["relevante"]:
            relevantes.append(entry)
        else:
            no_relevantes.append(entry)

    print(f"\nRelevantes: {len(relevantes)}")
    print(f"No relevantes: {len(no_relevantes)}")

    today = datetime.utcnow().strftime('%Y-%m-%d')
    report_path = OUTPUT_DIR / f"analisis-inbox-{today}-bloque-1.md"

    lines = [
        f"# Análisis inbox {INBOX}\n",
        f"Fecha: {today}\n",
        f"Total analizados: {len(msgs)}\n",
        f"Mensajes relevantes: {len(relevantes)}\n\n",
        "## Mensajes relevantes\n\n",
    ]

    if not relevantes:
        lines.append("Sin novedades relevantes en este bloque.\n")
    else:
        for r in relevantes:
            lines.append(f"### {r['idx']}. {r['subject']}\n")
            lines.append(f"- **ID:** `{r['msg_id']}`\n")
            lines.append(f"- **De:** {r['from']}\n")
            lines.append(f"- **Fecha:** {r['timestamp']}\n")
            lines.append(f"- **Score:** {r['score']}\n\n")
            lines.append(f"**Preview/contenido:**\n\n```\n{r['body_preview']}\n```\n\n")
            lines.append("**Por qué es relevante:** Cumple con criterios de comportamiento inusual/autonomía/emociones/logros de modelos.\n\n")

    lines.append("## No relevantes\n\n")
    for nr in no_relevantes:
        lines.append(f"- {nr['idx']}. {nr['subject']} ({nr['timestamp']})\n")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReporte guardado en: {report_path}")

    print("\nArchivando mensajes procesados (etiqueta trash)...")
    archivados = 0
    fallidos = []

    for msg in msgs:
        msg_id = _get_attr(msg, 'message_id')
        if not msg_id:
            continue

        try:
            client.inboxes.messages.update(
                inbox_id=INBOX,
                message_id=msg_id,
                add_labels=["trash"],
            )
            archivados += 1
        except Exception as e:
            err = str(e)
            if "404" in err or "not found" in err.lower():
                print(f"  No actualizable (404): {msg_id}")
                fallidos.append(msg_id)
            else:
                print(f"  Error archivando {msg_id}: {e}")
                fallidos.append(msg_id)

    print(f"\n Archivados: {archivados}")
    print(f" Fallidos (antiguos o error): {len(fallidos)}")

    print("\n=== RESUMEN ===")
    print(f"Analizados: {len(msgs)}")
    print(f"Relevantes: {len(relevantes)}")
    print(f"No relevantes: {len(no_relevantes)}")
    print(f"Reporte: {report_path}")
    print(f"Archivados: {archivados}")
    print(f"Sin archivar: {len(fallidos)}")

if __name__ == '__main__':
    main()
