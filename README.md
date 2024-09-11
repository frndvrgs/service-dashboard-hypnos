# service-dashboard-hypnos

# Audit Microservice

This microservice handles the auditing process for repositories.

## Setup

1. Ensure you have Python 3.9+ installed.
2. Create a virtual environment:

python -m venv venv
venv\Scripts\activate

3. Install dependencies:

pip install -r requirements.txt

4. Generate gRPC code:

python -m grpc_tools.protoc -I./proto --python_out=./src/core --grpc_python_out=./src/core ./proto/audit.proto

## Running the service

1. Activate the virtual environment:

venv\Scripts\activate

2. Define environment variables:

linux
export CMS_WEBSOCKET_ENDPOINT="ws://127.0.0.1:20110/audit"

windows
set CMS_WEBSOCKET_ENDPOINT=ws://127.0.0.1:20110/audit

2. Run the main script:

python src/main.py

The gRPC server will start on port 50051.

## Formatting

1. Run the black command:

black src