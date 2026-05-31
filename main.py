#!/usr/bin/env python3
"""DevUtils API - Launch script.

Run locally:  python main.py
Deploy via:   uvicorn app.main:app  (if using Railway with Uvicorn)
Run via:      python main.py        (zero-dependency stdlib server)
"""

import os
import sys

# Add the app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.server import start

if __name__ == "__main__":
    start()
