install:
	python3 -m venv .venv && . .venv/bin/activate && pip install --upgrade pip localstack awscli-local boto3

start-localstack:
	localstack start -d
	localstack status services

create-ec2:
	awslocal ec2 run-instances --image-id ami-df5de72bdb3b --count 1 --instance-type t3.nano --query 'Instances[0].InstanceId' --output text > instance_id.txt
	cat instance_id.txt

package-lambda:
	cd lambda && zip ../function.zip lambda_function.py

create-lambda:
	awslocal lambda create-function \
		--function-name control-ec2 \
		--runtime python3.11 \
		--handler lambda_function.lambda_handler \
		--zip-file fileb://function.zip \
		--role arn:aws:iam::000000000000:role/lambda-role \
		--environment "Variables={INSTANCE_ID=$$(cat instance_id.txt),AWS_ENDPOINT_URL=http://localhost.localstack.cloud:4566}"

status:
	curl -X POST "http://localhost:4566/restapis/$$(cat api_id.txt)/dev/_user_request_/ec2" \
		-H "Content-Type: application/json" \
		-d '{"action":"status"}'

start:
	curl -X POST "http://localhost:4566/restapis/$$(cat api_id.txt)/dev/_user_request_/ec2" \
		-H "Content-Type: application/json" \
		-d '{"action":"start"}'

stop:
	curl -X POST "http://localhost:4566/restapis/$$(cat api_id.txt)/dev/_user_request_/ec2" \
		-H "Content-Type: application/json" \
		-d '{"action":"stop"}'
