import json
import os
import boto3

INSTANCE_ID = os.environ.get("INSTANCE_ID")
AWS_ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL", "http://localhost.localstack.cloud:4566")
REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

ec2 = boto3.client(
    "ec2",
    region_name=REGION,
    endpoint_url=AWS_ENDPOINT_URL,
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

def get_body(event):
    body = event.get("body", event)

    if isinstance(body, str):
        try:
            return json.loads(body)
        except Exception:
            return {}

    if isinstance(body, dict):
        return body

    return {}

def lambda_handler(event, context):
    body = get_body(event)
    action = body.get("action", "status")

    if not INSTANCE_ID:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "INSTANCE_ID manquant dans la Lambda"})
        }

    try:
        if action == "start":
            ec2.start_instances(InstanceIds=[INSTANCE_ID])
            message = "Instance EC2 démarrée"

        elif action == "stop":
            ec2.stop_instances(InstanceIds=[INSTANCE_ID])
            message = "Instance EC2 arrêtée"

        elif action == "status":
            message = "Statut récupéré"

        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Action invalide. Utilise start, stop ou status"})
            }

        response = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
        state = response["Reservations"][0]["Instances"][0]["State"]["Name"]

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": message,
                "instance_id": INSTANCE_ID,
                "state": state
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
