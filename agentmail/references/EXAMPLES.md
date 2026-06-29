# AgentMail Usage Examples

Common patterns and use cases for AgentMail in AI agent workflows.

## Basic Agent Email Setup

### 1. Create Agent Identity

```python
from agentmail import AgentMail
import os

client = AgentMail(api_key=os.getenv("AGENTMAIL_API_KEY"))

agent_inbox = client.inboxes.create(
    username="spike-assistant",
    display_name="Spike - AI Assistant",
    client_id="spike-main-inbox" # Prevents duplicates
)

print(f"Agent email: {agent_inbox.inbox_id}")
# Output: spike-assistant@agentmail.to
```

### 2. Send Status Updates (Ubuntu)

```bash
set -a
source ~/.agentmail/.env
set +a

python3 /path/to/agentmail/scripts/send_email.py \
  --inbox "spike-assistant@agentmail.to" \
  --to "user@example.com" \
  --subject "Task Completed: PDF Rotation" \
  --text "El PDF fue rotado y guardado en /tmp/resultado.pdf"
```

## Customer Support Automation

### Auto-Reply System

```python
def setup_support_auto_reply():
    support_inbox = client.inboxes.create(
        username="support",
        display_name="Customer Support",
        client_id="support-inbox"
    )
    
    webhook = client.webhooks.create(
        url="https://your-app.com/webhook/support",
        event_types=["message.received"],
        inbox_ids=[support_inbox.inbox_id],
        client_id="support-webhook"
    )
    
    return support_inbox, webhook
```

## Document Processing Workflow

### Email -> Process -> Reply

```python
import base64
import tempfile
from pathlib import Path

def process_pdf_attachment(message):
    processed_files = []
    
    for attachment in message.get('attachments', []):
        if attachment['content_type'] == 'application/pdf':
            pdf_data = base64.b64decode(attachment['content'])
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(pdf_data)
                temp_path = tmp.name
            
            try:
                extracted_text = extract_pdf_text(temp_path)
                output_path = f"/tmp/processed_{attachment['filename']}.txt"
                with open(output_path, 'w') as f:
                    f.write(extracted_text)
                
                processed_files.append({
                    'original': attachment['filename'],
                    'output': output_path,
                    'preview': extracted_text[:200] + '...'
                })
            finally:
                Path(temp_path).unlink()
            
            if processed_files:
                results_text = "\n".join([
                    f"Processed {f['original']}:\n{f['preview']}\n"
                    for f in processed_files
                ])
                
                attachments = []
                for f in processed_files:
                    with open(f['output'], 'r') as file:
                        content = base64.b64encode(file.read().encode()).decode()
                    attachments.append({
                        'filename': Path(f['output']).name,
                        'content': content,
                        'content_type': 'text/plain'
                    })
                
                client.inboxes.messages.send(
                    inbox_id=message['inbox_id'],
                    to=message['from'][0]['email'],
                    subject=f"Re: {message['subject']} - Processed",
                    text=f"I've processed your PDF files:\n\n{results_text}",
                    attachments=attachments
                )
```

## Task Assignment and Tracking

### Email-Based Task Management

```python
def create_task_tracker_inbox():
    inbox = client.inboxes.create(
        username="tasks",
        display_name="Task Assignment Bot",
        client_id="task-tracker"
    )
    
    webhook = client.webhooks.create(
        url="https://your-app.com/webhook/tasks",
        event_types=["message.received"],
        inbox_ids=[inbox.inbox_id]
    )
    
    return inbox
```

## Notification and Alert System

### Multi-Channel Alerts

```python
from datetime import datetime

def send_system_alert(alert_type, message, severity='info', recipients=None):
    if recipients is None:
        recipients = ['admin@company.com', 'ops@company.com']
    
    severity_emoji = {
        'critical': '🚨',
        'warning': '⚠️',
        'info': 'ℹ️',
        'success': '✅'
    }
    
    emoji = severity_emoji.get(severity, 'ℹ️')
    
    client.inboxes.messages.send(
        inbox_id="alerts@agentmail.to",
        to=recipients,
        subject=f"{emoji} [{severity.upper()}] {alert_type}",
        text=f"""System Alert

Type: {alert_type}
Severity: {severity}
Time: {datetime.now().isoformat()}

Message:
{message}

This is an automated alert from the monitoring system.
""",
        html=f"""
<h2>{emoji} System Alert</h2>
<table>
<tr><td><strong>Type:</strong></td><td>{alert_type}</td></tr>
<tr><td><strong>Severity:</strong></td><td style="color: {'red' if severity == 'critical' else 'orange' if severity == 'warning' else 'blue'}">{severity}</td></tr>
<tr><td><strong>Time:</strong></td><td>{datetime.now().isoformat()}</td></tr>
</table>

<h3>Message:</h3>
<p>{message.replace(chr(10), '<br>')}</p>

<p><em>This is an automated alert from the monitoring system.</em></p>
"""
    )
```

## Testing and Development

### Local Development Setup

```python
def setup_dev_environment():
    dev_inbox = client.inboxes.create(
        username="dev-test",
        display_name="Development Testing",
        client_id="dev-testing"
    )
    
    print(f"Development inbox: {dev_inbox.inbox_id}")
    print("Use this for testing email workflows locally")
    
    test_response = client.inboxes.messages.send(
        inbox_id=dev_inbox.inbox_id,
        to="your-personal-email@gmail.com",
        subject="AgentMail Development Test",
        text="This is a test email from your AgentMail development setup."
    )
    
    print(f"Test email sent: {test_response.message_id}")
    return dev_inbox
```
