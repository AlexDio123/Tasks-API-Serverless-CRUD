# Evaluation criteria – how this project meets them

## 1. Correctness

- **Create (POST /tasks):** Accepts `title`, `description`, `status`; generates `taskId` (UUID); writes to DynamoDB; returns 201 and the created task.
- **Read (GET /tasks/{taskId}):** Fetches item by `taskId`; returns 200 with task or 404 if not found.
- **Update (PUT /tasks/{taskId}):** Updates only provided fields (title, description, status); returns 200 with updated task or 404.
- **Delete (DELETE /tasks/{taskId}):** Removes item; returns 204 No Content or 404 if not found.

All operations use the same DynamoDB table and schema (`taskId`, `title`, `description`, `status`).

---

## 2. AWS CDK usage

- **`cdk/tasks_api_stack.py`** defines all infrastructure in code:
  - **DynamoDB:** `TasksTable` with partition key `taskId` (string), on-demand billing.
  - **Lambda:** Four functions (Create, Get, Update, Delete), Python 3.12, env var `TABLE_NAME`, granted least-privilege table access.
  - **API Gateway:** REST API with `POST /tasks`, `GET/PUT/DELETE /tasks/{taskId}`, Lambda integrations, prod stage with throttling.
- **`cdk/app.py`** instantiates the stack; **`cdk.json`** configures the app. Deploy with `cdk deploy`.

---

## 3. Lambda and API Gateway integration

- **HTTP methods:** POST (create), GET (read), PUT (update), DELETE (delete) on the paths specified in the assignment.
- **Status codes:** 201 (create), 200 (get/update), 204 (delete), 400 (validation), 404 (not found), 500 (server error).
- **Request/response:** JSON body for POST/PUT; path parameter `{taskId}` for GET/PUT/DELETE. Responses are JSON (except 204 with no body).
- **Integration:** Each route uses `LambdaIntegration` in the CDK stack; Lambda receives API Gateway event and returns the expected response shape.

---

## 4. DynamoDB access via AWS SDK

- All four Lambdas use **boto3** (AWS SDK for Python):
  - **create_task:** `table.put_item(Item=...)`
  - **get_task:** `table.get_item(Key={"taskId": ...})`
  - **update_task:** `table.get_item` (existence check) and `table.update_item` with `UpdateExpression`, `ExpressionAttributeNames`, `ExpressionAttributeValues`
  - **delete_task:** `table.delete_item(Key=..., ReturnValues="ALL_OLD")` and 404 if no `Attributes` returned
- Table name is provided via environment variable `TABLE_NAME` from the CDK stack.

---

## 5. Code structure

- **Infrastructure:** Single stack file; clear separation of table, Lambdas, and API; shared Lambda config; CDK outputs for API URL and table name.
- **Lambdas:** One module per operation under `lambdas/<operation>/handler.py`; shared pattern (parse input → DynamoDB → response); minimal dependencies (stdlib + boto3).
- **Conventions:** Docstrings, consistent response helper, validation in one place per handler. No framework lock-in; easy to extend.

---

## 6. Error handling

- **Missing/invalid input:** Missing `title` (create) → 400 with `{"error": "title is required"}`. Invalid `status` → 400 with allowed values. Missing `taskId` in path → 400.
- **Not found:** Get/Update/Delete return 404 with `{"error": "Task not found"}` when the item does not exist.
- **Bad JSON:** Invalid request body → 400 with message (e.g. `Invalid JSON body`).
- **Server errors:** Unhandled exceptions → 500 with `{"error": "<message>"}`. All error responses are JSON with a consistent `error` field.

---

## 7. Testing (optional / bonus)

- **Unit tests** in `tests/test_handlers.py`:
  - Create: missing title → 400; invalid status → 400.
  - Get: missing `taskId` → 400.
- **Approach:** Tests import handlers and call them with mock events; no AWS calls (validation paths only). `TABLE_NAME` set in env for import.
- **Possible extensions for bonus:** Use **Pydantic** in Lambdas for request/response validation and shared models; add **AWS Powertools** (logger, tracer) for observability; add tests that mock `boto3` for 404 and successful create/update/delete flows.
