import aws_cdk as cdk
from tasks_api_stack import TasksApiStack

app = cdk.App()
TasksApiStack(app, "TasksApiStack", env=cdk.Environment(
    account=app.node.try_get_context("account") or None,
    region=app.node.try_get_context("region") or None,
))

app.synth()
