# AWS CLI and credentials – step-by-step guide

The CDK and Lambda SDK (boto3) use the same credential chain as the AWS CLI. Configure once and everything works.

## 1. Install AWS CLI

**macOS (Homebrew):**
```bash
brew install awscli
```

**macOS / Linux (official installer):**
```bash
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

**Windows:** Download and run the [AWS CLI MSI](https://awscli.amazonaws.com/AWSCLIV2.msi).

Verify:
```bash
aws --version
```

## 2. Install AWS CDK CLI

The `cdk` command is a separate Node.js tool. Install it globally (requires Node.js 18+):

```bash
npm install -g aws-cdk
```

Verify:
```bash
cdk --version
```

If you get "command not found", ensure Node.js is installed (`node --version`) and that npm’s global bin directory is on your `PATH` (often `~/.nvm/versions/node/<version>/bin` if using nvm).

## 3. Get credentials

You need an **Access Key ID** and **Secret Access Key** for an IAM user that can create/update resources (Lambda, API Gateway, DynamoDB, IAM roles, etc.).

- **Option A – AWS Console:** IAM → Users → your user → Security credentials → Create access key (use "Command Line Interface" and confirm).
- **Option B – Already have keys:** Use the same key pair for this project.

## 4. Configure the CLI

Run and follow the prompts (use the region where you want to deploy, e.g. `us-east-1`):

```bash
aws configure
```

You'll be asked for:

| Prompt                | What to enter            |
|-----------------------|--------------------------|
| AWS Access Key ID     | Your access key          |
| AWS Secret Access Key | Your secret key          |
| Default region name   | e.g. `us-east-1`         |
| Default output format | `json` (optional)        |

This writes to `~/.aws/credentials` and `~/.aws/config`. The CDK and boto3 will use these by default.

## 5. Optional: named profiles

To use a different account or role:

```bash
aws configure --profile my-project
```

Use it for CDK:

```bash
cdk deploy --profile my-project
```

Or set for the shell:

```bash
export AWS_PROFILE=my-project
cdk deploy
```

## 6. Verify

```bash
aws sts get-caller-identity
```

You should see your account ID, user ARN, and user ID. If this works, CDK and the Lambdas (via the roles CDK creates) will be able to use the same credentials for deployment and runtime.

## 7. SDK (boto3)

No extra config: **boto3** uses the same credentials as the AWS CLI. Once `aws configure` (or `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_PROFILE`) is set, your local Python and the CDK app use it. Lambdas get permissions from the IAM roles defined in the CDK stack, not from your CLI credentials.
