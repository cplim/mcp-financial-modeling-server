#!/usr/bin/env python3
"""Script to run integration tests for FMP API client.

This script checks for the FMP_API_KEY environment variable and runs
integration tests if available.
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Run integration tests."""
    # Check for .env file first
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv

            load_dotenv(env_file)
            print("✅ .env file found and loaded")
        except ImportError:
            print("⚠️  .env file found but python-dotenv not installed")
            print("Run: uv sync --dev")

    api_key = os.getenv("FMP_API_KEY")

    if not api_key:
        print("❌ FMP_API_KEY environment variable not set")
        print("Integration tests require a valid Financial Modeling Prep API key.")
        print("Get your free API key at: https://financialmodelingprep.com/developer/docs")
        print("Then either:")
        print("  1. Set environment variable: export FMP_API_KEY=your_api_key_here")
        print("  2. Copy .env.example to .env and add your API key")
        sys.exit(1)

    print("✅ FMP_API_KEY found - running integration tests...")
    print(f"Using API key: {api_key[:8]}{'*' * (len(api_key) - 8)}")

    # Run integration tests only
    try:
        subprocess.run(
            ["uv", "run", "pytest", "tests/test_fmp_integration.py", "-v", "-m", "integration"],
            check=True,
        )

        print("\n✅ All integration tests passed!")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Integration tests failed with exit code: {e.returncode}")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("❌ 'uv' command not found. Please install uv or run pytest directly.")
        sys.exit(1)


if __name__ == "__main__":
    main()
