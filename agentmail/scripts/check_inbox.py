#!/usr/bin/env python3
"""
Check AgentMail inbox for messages

Usage:
    # List recent messages
    python3 check_inbox.py --inbox "myagent@agentmail.to"

    # Get specific message
    python3 check_inbox.py --inbox "myagent@agentmail.to" --message "msg_123abc"

    # List threads
    python3 check_inbox.py --inbox "myagent@agentmail.to" --threads

    # Monitor for new messages (poll every N seconds)
    python3 check_inbox.py --inbox "myagent@agentmail.to" --monitor 30

Environment:
    AGENTMAIL_API_KEY: Your AgentMail API key
"""

import argparse
import os
import sys
import time
from datetime import datetime

try:
    from agentmail import AgentMail
except ImportError:
    print("Error: agentmail package not found. Install with: pip install agentmail")
    sys.exit(1)


def format_timestamp(iso_string):
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return iso_string


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


def print_message_summary(message):
    from_items = _get_attr(message, 'from', []) or []
    from_addr = _get_first_email(from_items)
    from_name = _get_first_name(from_items)
    subject = _get_attr(message, 'subject', '(no subject)')
    timestamp = format_timestamp(_get_attr(message, 'timestamp', ''))
    preview_source = _get_attr(message, 'preview', None)
    if preview_source is None:
        preview_source = _get_attr(message, 'text', '')
    preview = (preview_source or '')[:100]

    print(f"📧 {_get_attr(message, 'message_id', 'N/A')}")
    if from_name:
        print(f" From: {from_name} <{from_addr}>")
    else:
        print(f" From: {from_addr}")
    print(f" Subject: {subject}")
    print(f" Time: {timestamp}")
    if preview:
        print(f" Preview: {preview}{'...' if len(preview) == 100 else ''}")
    print()


def print_thread_summary(thread):
    subject = _get_attr(thread, 'subject', '(no subject)')
    participants = ', '.join(_get_attr(thread, 'participants', []) or [])
    count = _get_attr(thread, 'message_count', 0) or 0
    timestamp = format_timestamp(_get_attr(thread, 'last_message_at', ''))

    print(f"🧵 {_get_attr(thread, 'thread_id', 'N/A')}")
    print(f" Subject: {subject}")
    print(f" Participants: {participants}")
    print(f" Messages: {count}")
    print(f" Last: {timestamp}")
    print()


def main():
    parser = argparse.ArgumentParser(description='Check AgentMail inbox')
    parser.add_argument('--inbox', required=True, help='Inbox email address')
    parser.add_argument('--message', help='Get specific message by ID')
    parser.add_argument('--threads', action='store_true', help='List threads instead of messages')
    parser.add_argument('--monitor', type=int, metavar='SECONDS', help='Monitor for new messages (poll interval)')
    parser.add_argument('--limit', type=int, default=10, help='Number of items to fetch (default: 10)')
    args = parser.parse_args()

    api_key = os.getenv('AGENTMAIL_API_KEY')
    if not api_key:
        print("Error: AGENTMAIL_API_KEY environment variable not set")
        sys.exit(1)

    client = AgentMail(api_key=api_key)

    if args.monitor:
        print(f"🔍 Monitoring {args.inbox} (checking every {args.monitor} seconds)")
        print("Press Ctrl+C to stop\n")

        last_message_ids = set()

        try:
            while True:
                try:
                    messages = client.inboxes.messages.list(
                        inbox_id=args.inbox,
                        limit=args.limit,
                    )

                    new_messages = []
                    current_message_ids = set()

                    for message in messages.messages:
                        msg_id = _get_attr(message, 'message_id')
                        current_message_ids.add(msg_id)

                        if msg_id not in last_message_ids:
                            new_messages.append(message)

                    if new_messages:
                        print(f"🆕 Found {len(new_messages)} new message(s):")
                        for message in new_messages:
                            print_message_summary(message)

                    last_message_ids = current_message_ids

                except Exception as e:
                    print(f"❌ Error checking inbox: {e}")

                time.sleep(args.monitor)

        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            return

    elif args.message:
        try:
            message = client.inboxes.messages.get(
                inbox_id=args.inbox,
                message_id=args.message,
            )

            print(f"📧 Message Details:")
            print(f" ID: {message.get('message_id')}")
            print(f" Thread: {message.get('thread_id')}")

            from_addr = message.get('from', [{}])[0].get('email', 'Unknown')
            from_name = message.get('from', [{}])[0].get('name', '')
            print(f" From: {from_name} <{from_addr}>" if from_name else f" From: {from_addr}")

            to_addrs = ', '.join([addr.get('email', '') for addr in message.get('to', [])])
            print(f" To: {to_addrs}")

            print(f" Subject: {message.get('subject', '(no subject)')}")
            print(f" Time: {format_timestamp(message.get('timestamp', ''))}")

            labels_source = _get_attr(message, 'labels', []) or []
            if labels_source:
                print(f" Labels: {', '.join(labels_source)}")

            print("\n📝 Content:")
            text_value = _get_attr(message, 'text')
            if text_value:
                print(text_value)
            else:
                print("(No text content)")

            attachments = _get_attr(message, 'attachments', []) or []
            if attachments:
                print(f"\n📎 Attachments ({len(attachments)}):")
                for att in attachments:
                    print(f" • {_get_attr(att, 'filename', 'unnamed')} ({_get_attr(att, 'content_type', 'unknown type')})")

        except Exception as e:
            print(f"❌ Error getting message: {e}")
            sys.exit(1)

    elif args.threads:
        try:
            threads = client.inboxes.threads.list(
                inbox_id=args.inbox,
                limit=args.limit,
            )

            if not threads.threads:
                print(f"📭 No threads found in {args.inbox}")
                return

            print(f"🧵 Threads in {args.inbox} (showing {len(threads.threads)}):\n")
            for thread in threads.threads:
                print_thread_summary(thread)

        except Exception as e:
            print(f"❌ Error listing threads: {e}")
            sys.exit(1)

    else:
        try:
            messages = client.inboxes.messages.list(
                inbox_id=args.inbox,
                limit=args.limit,
            )

            if not messages.messages:
                print(f"📭 No messages found in {args.inbox}")
                return

            print(f"📧 Messages in {args.inbox} (showing {len(messages.messages)}):\n")
            for message in messages.messages:
                print_message_summary(message)

        except Exception as e:
            print(f"❌ Error listing messages: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()
