#!/bin/bash
python3 -m grpc_tools.protoc -I./proto --python_out=./src --grpc_python_out=./src ./proto/posts_service.proto
python3 ./src/main.py