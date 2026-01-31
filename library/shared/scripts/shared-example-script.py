#!/usr/bin/env python3
"""
Shared example script for DevKit library.
Demonstrates the scripts folder structure.
"""

import sys

def main():
    print("Shared example script executed")
    if len(sys.argv) > 1:
        print(f"Arguments: {sys.argv[1:]}")

if __name__ == "__main__":
    main()
