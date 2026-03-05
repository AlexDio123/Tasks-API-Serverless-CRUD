import json
import os

import boto3

TABLE_NAME = os.environ["TABLE_NAME"]
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

VALID_STATUSES = {"pending", "in-progress", "completed"}


def handler(event, context):
    try:
        task_id = (event.get("pathParameters") or {}).get("taskId")
        if not task_id:
            return response(400, {"error": "taskId is required"})

        # Check task exists
        existing = table.get_item(Key={"taskId": task_id})
        if not existing.get("Item"):
            return response(404, {"error": "Task not found"})

        body = json.loads(event.get("body") or "{}")
        title = body.get("title")
        description = body.get("description")
        status = body.get("status")

        if status is not None and str(status).strip().lower() not in VALID_STATUSES:
            return response(400, {"error": f"status must be one of: {sorted(VALID_STATUSES)}"})

        # Build update expression: only update provided fields
        update_parts = []
        expr_names = {}
        expr_values = {}

        if title is not None:
            update_parts.append("#title = :title")
            expr_names["#title"] = "title"
            expr_values[":title"] = str(title).strip()
        if description is not None:
            update_parts.append("#desc = :desc")
            expr_names["#desc"] = "description"
            expr_values[":desc"] = str(description).strip()
        if status is not None:
            update_parts.append("#status = :status")
            expr_names["#status"] = "status"
            expr_values[":status"] = str(status).strip().lower()

        if not update_parts:
            # No updates; return current item
            result = table.get_item(Key={"taskId": task_id})
            return response(200, result["Item"])

        update_expr = "SET " + ", ".join(update_parts)
        table.update_item(
            Key={"taskId": task_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
            ReturnValues="ALL_NEW",
        )
        updated = table.get_item(Key={"taskId": task_id})
        return response(200, updated["Item"])
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
