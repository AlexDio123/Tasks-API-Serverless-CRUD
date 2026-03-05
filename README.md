# Tasks API – Serverless CRUD

A serverless CRUD API for **Tasks** built with **AWS CDK**, **Lambda**, **API Gateway**, and **DynamoDB**.

For how this project addresses the evaluation criteria, see [EVALUATION.md](EVALUATION.md).

---

## Deliverables

| Deliverable | Location |
|-------------|----------|
| **Lambda function code** | [`lambdas/create_task/handler.py`](lambdas/create_task/handler.py), [`lambdas/get_task/handler.py`](lambdas/get_task/handler.py), [`lambdas/update_task/handler.py`](lambdas/update_task/handler.py), [`lambdas/delete_task/handler.py`](lambdas/delete_task/handler.py) — one handler per CRUD operation |
| **README (setup + deploy)** | This file — see [Prerequisites](#prerequisites), [Setup and deploy](#setup-and-deploy), and [Run tests](#run-tests) |
| **Deploy instructions** | [Setup and deploy](#setup-and-deploy) below (venv, dependencies, `cdk bootstrap`, `cdk deploy`). AWS CLI/CDK install: [CONFIGUREME.md](CONFIGUREME.md) |
| **How to test the API** | [Try the API](#setup-and-deploy) (step 4) with `curl` examples; also [Run tests](#run-tests) for unit tests |

Submit this project as a **GitHub repository** (clone or download as zip). All of the above are included in the repo.

---

## Structure

```
tasks-api/
├── cdk/                    # CDK app and stack
│   ├── app.py
│   ├── cdk.json
│   ├── requirements.txt
│   └── tasks_api_stack.py
├── lambdas/                 # One Lambda per operation
│   ├── create_task/
│   ├── get_task/
│   ├── update_task/
│   └── delete_task/
├── tests/
├── requirements.txt         # Dev/test deps (boto3, pytest)
├── README.md
└── CONFIGUREME.md           # AWS CLI install and credentials
```

## Task model

| Attribute    | Type   | Description                                      |
|-------------|--------|--------------------------------------------------|
| `taskId`    | string | Unique identifier (auto-generated on create)     |
| `title`     | string | Title of the task                                |
| `description` | string | Brief description                              |
| `status`    | string | `"pending"`, `"in-progress"`, or `"completed"`   |

## API

| Method | Path              | Description        |
|--------|-------------------|--------------------|
| POST   | `/tasks`          | Create a task      |
| GET    | `/tasks/{taskId}` | Get a task         |
| PUT    | `/tasks/{taskId}` | Update a task      |
| DELETE | `/tasks/{taskId}` | Delete a task      |

### Create Task – `POST /tasks`

**Request body:**

```json
{
  "title": "Task 1",
  "description": "This is task 1",
  "status": "pending"
}
```

**Response (201):**

```json
{
  "taskId": "generated-unique-id",
  "title": "Task 1",
  "description": "This is task 1",
  "status": "pending"
}
```

### Get Task – `GET /tasks/{taskId}`

**Response (200):** Task object as above.

### Update Task – `PUT /tasks/{taskId}`

**Request body (all fields optional):**

```json
{
  "title": "Updated Task 1",
  "description": "This task has been updated",
  "status": "completed"
}
```

**Response (200):** Updated task object.

### Delete Task – `DELETE /tasks/{taskId}`

**Response:** `204 No Content`.

---

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for AWS CDK CLI)
- **AWS CLI** configured with credentials (see [CONFIGUREME.md](CONFIGUREME.md) for install and setup)
- **AWS CDK CLI:** `npm install -g aws-cdk`

## Setup and deploy

1. **Create a virtual environment and install CDK dependencies:**

   ```bash
   cd tasks-api/cdk
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Bootstrap CDK (once per account/region):**

   ```bash
   cdk bootstrap
   ```

3. **Deploy the stack:**

   ```bash
   cdk deploy
   ```

   Accept the IAM changes when prompted. After deployment, the CLI prints the **API base URL** (e.g. `https://xxxx.execute-api.region.amazonaws.com/prod/`).

4. **Try the API:**  
   Replace `YOUR_API_URL` with the URL from the deploy output (e.g. `https://abc123.execute-api.us-east-1.amazonaws.com`).

   ```bash
   # Create a task
   curl -X POST https://YOUR_API_URL/prod/tasks \
     -H "Content-Type: application/json" \
     -d '{"title":"My Task","description":"First task","status":"pending"}'

   # Get task (use taskId from create response)
   curl https://YOUR_API_URL/prod/tasks/TASK_ID

   # Update task
   curl -X PUT https://YOUR_API_URL/prod/tasks/TASK_ID \
     -H "Content-Type: application/json" \
     -d '{"title":"Updated","description":"Done","status":"completed"}'

   # Delete task
   curl -X DELETE https://YOUR_API_URL/prod/tasks/TASK_ID
   ```

## Run tests

From the project root:

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## Destroy

From `cdk/`:

```bash
cdk destroy
```

## Design notes

- **No framework in Lambdas:** Handlers are plain Python + `boto3`. This keeps cold starts low and dependencies minimal; `boto3` is provided by the Lambda runtime.
- **One Lambda per operation:** Clear separation of concerns and independent scaling; you can later split into a single Lambda with routing if you prefer.
- **DynamoDB:** Table `TasksTable` with partition key `taskId` (string), billing mode **on-demand** (pay per request).
- **API Gateway:** REST API with `POST/GET/PUT/DELETE` on `/tasks` and `/tasks/{taskId}`, integrated with the Lambdas.
