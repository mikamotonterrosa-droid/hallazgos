#!/usr/bin/env python3
"""
Analisis completo de inbox AgentMail siguiendo la skill (Ubuntu native edition).
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime

try:
    from agentmail import AgentMail
except ImportError:
    print("Error: agentmail package not found.")
    sys.exit(1)

INBOX = "skynetclaw@agentmail.to"


def _get_attr(obj, name, default=None):
    return getattr(obj, name, default)


def _parse_from_field(raw):
    if not raw:
        return '', 'Unknown'
    if isinstance(raw, list) and raw:
        raw = raw[0]
    if isinstance(raw, dict):
        return (
            raw.get('name') or raw.get('display_name') or '',
            raw.get('email') or raw.get('address') or 'Unknown',
        )
    if isinstance(raw, str):
        s = raw.strip()
        if '<' in s and '>' in s:
            name, rest = s.split('<', 1)
            return name.strip(), rest.split('>', 1)[0].strip()
        return '', s
    return '', 'Unknown'


def _clean_text(text):
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', ' ', text)
    text = text.replace('\r', ' ').replace('\n', ' ').strip()
    text = re.sub(r'\s+', ' ', text)
    return text


def _extract_article_url(text):
    if not text:
        return None
    urls = re.findall(r'https?://[^\s\)\]>]+', text)
    for url in urls:
        if re.search(r'\.(png|jpg|jpeg|gif|webp|svg)(\?|$)', url, re.IGNORECASE):
            continue
        if any(d in url for d in ['techpresso.co', 'beehiiv.com', 'blog', 'article', 'post', 'news']):
            return url
        if 'CDN-' not in url and 'media.' not in url:
            return url
    for url in urls:
        if not re.search(r'\.(png|jpg|jpeg|gif|webp|svg)(\?|$)', url, re.IGNORECASE):
            return url
    return None


def _generate_summary(subject, body):
    s = subject.strip() if subject else ''
    b = _clean_text(body).strip() if body else ''
    if s:
        summary = s
    else:
        summary = ''
    if b and b not in s and len(b) > 20:
        first_sentence = re.split(r'(?<=[.!?])\s+', b)[0]
        if first_sentence and first_sentence not in s:
            summary = f"{s}. {first_sentence}".strip()
    if not summary:
        summary = b[:200] if b else '(Sin información suficiente para resumir)'
    return summary


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
        from_raw = _get_attr(msg, 'from', None)
        from_name, from_addr = _parse_from_field(from_raw)
        from_str = f"{from_name} <{from_addr}>" if from_name else from_addr

        body_text = _get_attr(msg, 'text', '') or _get_attr(msg, 'preview', '') or ''
        body_html = _get_attr(msg, 'html', '') or ''
        body_clean = _clean_text(body_text or body_html)

        combined = f"{subject} {body_clean}".lower()

        score = 0
        for tema in TEMAS_RELEVANTES:
            if tema.lower() in combined:
                score += 1

        ai_keywords = [
            "ai ", "artificial intelligence", "llm", "modelo", "benchmark",
            "gpt", "claude", "gemini", "openai", "anthropic", "google ai",
            "agent", "autonomous", "consciousness", "emotion", "feeling",
        ]
        for kw in ai_keywords:
            if kw.lower() in combined:
                score += 1

        article_url = _extract_article_url(body_text or body_html)
        summary = _generate_summary(subject, body_clean)

        entry = {
            "idx": idx,
            "msg_id": msg_id,
            "subject": subject,
            "timestamp": timestamp,
            "from": from_str,
            "summary": summary,
            "article_url": article_url,
            "score": score,
            "relevante": score >= 2,
        }

        if entry["relevante"]:
            relevantes.append(entry)
        else:
            no_relevantes.append(entry)

    today = datetime.utcnow().strftime('%Y-%m-%d')
    report_path = Path.home() / 'agentmail' / 'reports' / f'analisis-inbox-{today}-bloque-1.md'
    report_path.parent.mkdir(parents=True, exist_ok=True)

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
            lines.append(f"### {r['idx']}. {r['subject']}\n\n")
            lines.append(f"- **ID:** `{r['msg_id']}`\n")
            lines.append(f"- **De:** {r['from']}\n")
            lines.append(f"- **Fecha:** {r['timestamp']}\n")
            lines.append(f"- **Score:** {r['score']}\n\n")
            lines.append(f"**Resumen:**\n\n{r['summary']}\n\n")
            if r['article_url']:
                lines.append(f"**Leer completa:** {r['article_url']}\n\n")
            lines.append("---\n\n")

    lines.append("## No relevantes\n\n")
    for nr in no_relevantes:
        lines.append(f"- {nr['idx']}. {nr['subject']} ({nr['timestamp']})\n")

    report_path.write_text("\n".join(lines), encoding='utf-8')
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
                print(f" No actualizable (404): {msg_id}")
                fallidos.append(msg_id)
            else:
                print(f" Error archivando {msg_id}: {e}")
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
