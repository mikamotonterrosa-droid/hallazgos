# Label workflow notes — experimentado en sesion

## Update por etiqueta (forma que anduvo)

```python
client.inboxes.messages.update(
    inbox_id=inbox_id,
    message_id=message_id,
    add_labels=["trash"],
    # remove_labels=["inbox"], # opcional
)
```

- `inbox_id`: direccion completa del inbox (ej: `skynetclaw@agentmail.to`)
- `message_id`: ID del mensaje, NO el thread ID
- `add_labels=["trash"]`: agrega etiqueta trash
- `remove_labels=["inbox"]`: opcional, quita inbox

## Respuesta OK observada

```
OK UpdateMessageResponse <0100019dd092b89d-...> ['sent', 'to-trash', 'trash']
```

- Importante: el sistema hace aparecer primero `to-trash` y luego `trash`.
- `to-trash` es un estado intermedio de procesamiento.
- `trash` es la etiqueta final de archivado.

## Estado final buscado

al archivar correctamente, `labels` queda como:

```
['received', 'unread', 'trash']
```

## Error 404 en mensajes antiguos

Al intentar actualizar mensajes muy antiguos, la API responde:

```
NotFoundError: Message not found
```

Esto no significa que el mensaje no exista, sino que no es actualizable por este endpoint. Registrar en el reporte y continuar con el siguiente lote.

## Lo que NO anda (ya probado)

- `PATCH` directo con body JSON `{"labels": ["trash"]}` -> 400
- cambiar `trash` por `read`, `seen`, `status`, `folder`, `op` -> 400
- usar `client.messages.update(...)` (ruta incorrecta) -> AttributeError
- usar thread.update en lugar de messages.update -> cambio de entidad incorrecto

## Verificacion rapida

```python
messages = client.inboxes.messages.list(inbox_id=inbox_id, limit=10)
for m in messages:
    labels = getattr(m, 'labels', [])
    msg_id = getattr(m, 'message_id', None)
    print(msg_id, labels)
```

Buscar explicitamente `'trash' in labels` para confirmar archivado.
