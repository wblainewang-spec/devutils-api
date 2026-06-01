"""DevUtils API - Zero-dependency launch script."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.server import start

if __name__ == "__main__":
    start()
