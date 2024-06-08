#!/bin/bash
python3 -m grpc_tools.protoc -I./proto --python_out=./src --grpc_python_out=./src ./proto/posts_service.proto
python3 -m grpc_tools.protoc -I./proto --python_out=./src --grpc_python_out=./src ./proto/statistics_service.proto
cd src
uvicorn main:server --host=0.0.0.0 --port=8000 --reload
