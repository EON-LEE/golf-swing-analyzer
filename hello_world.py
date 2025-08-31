#!/usr/bin/env python3
"""
SMP-4: Hello World Implementation
Simple Python script to print Hello World in Korean and English
"""

import sys


def print_hello_world() -> None:
    """Print Hello World message in Korean and English."""
    try:
        print("Hello World! 안녕하세요!")
    except UnicodeEncodeError:
        # Fallback for systems with encoding issues
        print("Hello World!")
    except Exception as e:
        print(f"Error printing message: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main function to execute the Hello World program."""
    try:
        print_hello_world()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
