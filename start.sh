#!/bin/sh
echo "=== start.sh running ==="
echo "PORT=$PORT"
echo "PWD=$(pwd)"
echo "Python: $(python3 --version 2>&1)"
echo "=== Running minimal test server ==="
exec python3 test_minimal.py
