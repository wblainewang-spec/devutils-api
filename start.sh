#!/bin/sh
echo "=== start.sh running ==="
echo "PORT=$PORT"
echo "PWD=$(pwd)"
echo "Files: $(ls)"
echo "Python: $(python3 --version 2>&1)"
# Flush all output before starting Python
exec python3 main.py
