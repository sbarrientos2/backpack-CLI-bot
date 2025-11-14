#!/usr/bin/env python3
"""Main entry point for Backpack CLI Bot trading bot."""

import sys
from api.backpack import BackpackClient
from ui.cli import CLI
from config import config


def main():
    """Main function."""
    # Validate configuration
    if not config.validate():
        print("Error: Missing API credentials!")
        print("Please copy .env.example to .env and add your Backpack API credentials.")
        sys.exit(1)

    # Initialize Backpack client
    api_key, api_secret = config.get_api_credentials()
    client = BackpackClient(
        api_key=api_key,
        api_secret=api_secret,
        base_url=config.API_BASE_URL
    )

    # Initialize and run CLI
    cli = CLI(client)

    try:
        cli.run()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
