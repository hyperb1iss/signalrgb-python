#!/usr/bin/env python3

import sys
import os
from signalrgb.cli import cli

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)


if __name__ == '__main__':
    cli()