from pathlib import Path

import aws_cdk as cdk
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_lambda as _lambda
from aws_cdk import Stack
from constructs import Construct


class TasksApiStack(Stack):
    """Stack for Tasks CRUD API: DynamoDB table, Lambda handlers, REST API."""

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Base path for Lambda code (relative to this file)
        lambdas_dir = Path(__file__).resolve().parent.parent / "lambdas"

        # 1. DynamoDB table
        self.tasks_table = dynamodb.Table(
            self,
            "TasksTable",
            table_name="TasksTable",
            partition_key=dynamodb.Attribute(
                name="taskId",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # 2. Lambda functions (one per CRUD operation)
        common_env = {"TABLE_NAME": self.tasks_table.table_name}
        common_lambda_kwargs = {
            "runtime": _lambda.Runtime.PYTHON_3_12,
            "timeout": cdk.Duration.seconds(30),
            "environment": common_env,
        }

        create_task_lambda = _lambda.Function(
            self,
            "CreateTaskFunction",
            function_name="TasksApi-CreateTask",
            handler="handler.handler",
            code=_lambda.Code.from_asset(str(lambdas_dir / "create_task")),
            **common_lambda_kwargs,
        )
        self.tasks_table.grant_read_write_data(create_task_lambda)

        get_task_lambda = _lambda.Function(
            self,
            "GetTaskFunction",
            function_name="TasksApi-GetTask",
            handler="handler.handler",
            code=_lambda.Code.from_asset(str(lambdas_dir / "get_task")),
            **common_lambda_kwargs,
        )
        self.tasks_table.grant_read_data(get_task_lambda)

        update_task_lambda = _lambda.Function(
            self,
            "UpdateTaskFunction",
            function_name="TasksApi-UpdateTask",
            handler="handler.handler",
            code=_lambda.Code.from_asset(str(lambdas_dir / "update_task")),
            **common_lambda_kwargs,
        )
        self.tasks_table.grant_read_write_data(update_task_lambda)

        delete_task_lambda = _lambda.Function(
            self,
            "DeleteTaskFunction",
            function_name="TasksApi-DeleteTask",
            handler="handler.handler",
            code=_lambda.Code.from_asset(str(lambdas_dir / "delete_task")),
            **common_lambda_kwargs,
        )
        self.tasks_table.grant_read_write_data(delete_task_lambda)

        # 3. API Gateway REST API
        api = apigateway.RestApi(
            self,
            "TasksApi",
            rest_api_name="Tasks API",
            description="Serverless CRUD API for Tasks",
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,
                throttling_burst_limit=200,
            ),
        )

        tasks_resource = api.root.add_resource("tasks")

        # POST /tasks -> Create Task
        tasks_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(create_task_lambda),
        )

        # GET /tasks/{taskId} -> Get Task
        task_id_resource = tasks_resource.add_resource("{taskId}")
        task_id_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(get_task_lambda),
        )

        # PUT /tasks/{taskId} -> Update Task
        task_id_resource.add_method(
            "PUT",
            apigateway.LambdaIntegration(update_task_lambda),
        )

        # DELETE /tasks/{taskId} -> Delete Task
        task_id_resource.add_method(
            "DELETE",
            apigateway.LambdaIntegration(delete_task_lambda),
        )

        # Outputs
        cdk.CfnOutput(
            self,
            "ApiEndpoint",
            value=api.url,
            description="Tasks API base URL",
            export_name="TasksApiEndpoint",
        )
        cdk.CfnOutput(
            self,
            "TasksTableName",
            value=self.tasks_table.table_name,
            description="DynamoDB Tasks table name",
            export_name="TasksTableName",
        )
