import json
import os
import uuid
from datetime import datetime, timezone

def _table():
    import boto3

    return boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])


def _response(status, body=None):
    response = {
        "statusCode": status,
        "headers": {
            "content-type": "application/json",
            "cache-control": "no-store",
        },
    }
    if body is not None:
        response["body"] = json.dumps(body)
    return response


def handler(event, _context):
    route = event.get("routeKey", "")

    if route == "GET /api/items":
        items = _table().scan().get("Items", [])
        items.sort(key=lambda item: item.get("createdAt", ""), reverse=True)
        return _response(200, {"items": items})

    if route == "POST /api/items":
        try:
            payload = json.loads(event.get("body") or "{}")
        except json.JSONDecodeError:
            return _response(400, {"error": "Request body must be valid JSON."})

        title = str(payload.get("title", "")).strip()
        if not title:
            return _response(400, {"error": "Title is required."})
        if len(title) > 120:
            return _response(400, {"error": "Title must be 120 characters or fewer."})

        item = {
            "id": str(uuid.uuid4()),
            "title": title,
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }
        _table().put_item(Item=item)
        return _response(201, item)

    if route == "DELETE /api/items/{id}":
        item_id = event.get("pathParameters", {}).get("id")
        if not item_id:
            return _response(400, {"error": "Item id is required."})
        _table().delete_item(Key={"id": item_id})
        return _response(204)

    return _response(404, {"error": "Not found."})
