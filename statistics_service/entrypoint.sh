#!/bin/bash
cd src
uvicorn main:server --host=0.0.0.0 --port=8002 --reload
