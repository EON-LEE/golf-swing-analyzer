#!/usr/bin/env python3
"""Command line interface for Golf Swing Analyzer."""

import argparse
import json
import sys
from pathlib import Path

from health import HealthChecker
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


def health_command(args):
    """Run health check."""
    try:
        if args.quick:
            is_healthy = HealthChecker.is_healthy()
            print("✅ Healthy" if is_healthy else "❌ Unhealthy")
            sys.exit(0 if is_healthy else 1)
        else:
            health_data = HealthChecker.get_system_health()
            if args.json:
                print(json.dumps(health_data, indent=2))
            else:
                print("🏥 System Health Report")
                print(f"Status: {'✅ Healthy' if health_data['status'] == 'healthy' else '❌ Unhealthy'}")
                print(f"CPU: {health_data['system']['cpu_percent']:.1f}%")
                print(f"Memory: {health_data['system']['memory_percent']:.1f}%")
                print(f"Disk: {health_data['system']['disk_percent']:.1f}%")
                print("\nDependencies:")
                for dep, status in health_data['dependencies'].items():
                    print(f"  {dep}: {'✅' if status else '❌'}")
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        sys.exit(1)


def config_command(args):
    """Show configuration."""
    try:
        Config.validate_config()
        config_data = Config.get_config_dict()
        
        if args.json:
            print(json.dumps(config_data, indent=2))
        else:
            print("⚙️  Configuration")
            for key, value in config_data.items():
                print(f"  {key}: {value}")
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Golf Swing Analyzer CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Check system health')
    health_parser.add_argument('--quick', action='store_true', help='Quick health check')
    health_parser.add_argument('--json', action='store_true', help='Output as JSON')
    health_parser.set_defaults(func=health_command)
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Show configuration')
    config_parser.add_argument('--json', action='store_true', help='Output as JSON')
    config_parser.set_defaults(func=config_command)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
