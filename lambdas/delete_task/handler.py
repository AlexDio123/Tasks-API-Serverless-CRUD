
import json
import os

import boto3

TABLE_NAME = os.environ["TABLE_NAME"]
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def handler(event, context):
    try:
        task_id = (event.get("pathParameters") or {}).get("taskId")
        if not task_id:
            return response(400, {"error": "taskId is required"})

        result = table.delete_item(
            Key={"taskId": task_id},
            ReturnValues="ALL_OLD",
        )
        if not result.get("Attributes"):
            return response(404, {"error": "Task not found"})

        # 204 No Content: no body
        return {
            "statusCode": 204,
            "headers": {
                "Access-Control-Allow-Origin": "*",
            },
            "body": "",
        }
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
