# AgentMail API Reference

Base URL: `https://api.agentmail.to/v0`

## Authentication

All requests require Bearer token authentication:

```http
Authorization: Bearer ***
```

## Inboxes

### Create Inbox

```http
POST /v0/inboxes
```

**Request:**

```json
{
  "username": "my-agent",
  "domain": "agentmail.to",
  "display_name": "My Agent",
  "client_id": "unique-id"
}
```

**Response:**

```json
{
  "pod_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "inbox_id": "my-agent@agentmail.to",
  "display_name": "My Agent",
  "created_at": "2024-01-10T08:15:00Z",
  "updated_at": "2024-01-10T08:15:00Z",
  "client_id": "unique-id"
}
```

### List Inboxes

```http
GET /v0/inboxes?limit=10&page_token=***==
```

**Response:**

```json
{
  "count": 2,
  "inboxes": [...],
  "limit": 10,
  "next_page_token": "***=="
}
```

### Get Inbox

```http
GET /v0/inboxes/{inbox_id}
```

## Messages

### Send Message

```http
POST /v0/inboxes/{inbox_id}/messages
```

**Request:**

```json
{
  "to": ["recipient@example.com"],
  "cc": ["cc@example.com"],
  "bcc": ["bcc@example.com"],
  "reply_to": "reply@example.com",
  "subject": "Email subject",
  "text": "Plain text body",
  "html": "<p>HTML body</p>",
  "labels": ["sent", "important"],
  "attachments": [{
    "filename": "document.pdf",
    "content": "base64-encoded-content",
    "content_type": "application/pdf"
  }],
  "headers": {
    "X-Custom-Header": "value"
  }
}
```

**Response:**

```json
{
  "message_id": "msg_123abc",
  "thread_id": "thd_789ghi"
}
```

### List Messages

```http
GET /v0/inboxes/{inbox_id}/messages?limit=10&page_token=token
```

### Get Message

```http
GET /v0/inboxes/{inbox_id}/messages/{message_id}
```

### Update Message Labels / Flags

Some environments support updating labels on a message. If available, use it to tag processed messages such as `trash` or `to-trash`.

```http
PATCH /v0/inboxes/{inbox_id}/messages/{message_id}
```

**Request body contract (reported shape):**

```json
{
  "add_labels": ["trash"],
  "remove_labels": ["inbox"]
}
```

Observed successful response:

```json
{
  "message_id": "msg_...",
  "thread_id": "thd_...",
  "labels": ["sent", "to-trash", "trash"]
}
```

Notes:
- Adding `"trash"` archives the message.
- An intermediate `"to-trash"` may appear before `"trash"`.
- Older messages can return `404` and are not recoverable via this endpoint.

## Threads

### List Threads

```http
GET /v0/inboxes/{inbox_id}/threads?limit=10
```

### Get Thread

```http
GET /v0/inboxes/{inbox_id}/threads/{thread_id}
```

**Response:**

```json
{
  "thread_id": "thd_789ghi",
  "inbox_id": "support@example.com",
  "subject": "Question about my account",
  "participants": ["jane@example.com", "support@example.com"],
  "labels": ["customer-support"],
  "message_count": 3,
  "last_message_at": "2023-10-27T14:30:00Z",
  "created_at": "2023-10-27T10:00:00Z",
  "updated_at": "2023-10-27T14:30:00Z"
}
```

## Webhooks

### Create Webhook

```http
POST /v0/webhooks
```

**Request:**

```json
{
  "url": "https://your-domain.com/webhook",
  "client_id": "webhook-identifier",
  "enabled": true,
  "event_types": ["message.received"],
  "inbox_ids": ["inbox1@domain.com"]
}
```

### List Webhooks

```http
GET /v0/webhooks
```

### Update Webhook

```http
PUT /v0/webhooks/{webhook_id}
```

### Delete Webhook

```http
DELETE /v0/webhooks/{webhook_id}
```

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "type": "validation_error",
    "message": "Invalid email address",
    "details": {
      "field": "to",
      "code": "INVALID_EMAIL"
    }
  }
}
```

Common error codes:
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid API key)
- `404` - Not Found (resource doesn't exist)
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

## Python SDK

```python
from agentmail import AgentMail
import os

client = AgentMail(api_key=os.getenv("AGENTMAIL_API_KEY"))
```
