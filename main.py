"""DevUtils API - Zero-dependency launch script."""
import sys
import os

# Immediate stderr debug logging (visible in Railway logs even if app crashes)
sys.stderr.write("=== main.py starting ===\n")
sys.stderr.flush()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Log Python version and PORT
sys.stderr.write(f"Python: {sys.version}\n")
sys.stderr.write(f"PORT env: {os.environ.get('PORT', 'NOT SET')}\n")
sys.stderr.write(f"PWD: {os.getcwd()}\n")
sys.stderr.write(f"Files: {os.listdir('.')}\n")
sys.stderr.flush()

from app.server import start

sys.stderr.write("Calling start()...\n")
sys.stderr.flush()
start()
