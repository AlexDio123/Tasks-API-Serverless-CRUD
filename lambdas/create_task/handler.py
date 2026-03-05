import json
import os
import uuid

import boto3

TABLE_NAME = os.environ["TABLE_NAME"]
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

VALID_STATUSES = {"pending", "in-progress", "completed"}


def handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        title = body.get("title", "").strip()
        description = (body.get("description") or "").strip()
        status = (body.get("status") or "pending").strip().lower()

        if not title:
            return response(400, {"error": "title is required"})

        if status not in VALID_STATUSES:
            return response(400, {"error": f"status must be one of: {sorted(VALID_STATUSES)}"})

        task_id = str(uuid.uuid4())
        item = {
            "taskId": task_id,
            "title": title,
            "description": description,
            "status": status,
        }
        table.put_item(Item=item)
        return response(201, item)
    except json.JSONDecodeError as e:
        return response(400, {"error": f"Invalid JSON body: {e!s}"})
    except Exception as e:
        return response(500, {"error": str(e)})


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }
