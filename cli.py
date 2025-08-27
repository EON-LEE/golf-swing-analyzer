"""Command Line Interface for Golf Swing Analyzer."""

import asyncio
import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.table import Table

from config import Config
from health import HealthChecker
from video_processor import VideoProcessor
from services import GolfSwingAnalysisService
from utils.logger import setup_logger

console = Console()
logger = setup_logger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--config-file', type=click.Path(exists=True), help='Custom config file')
def cli(verbose: bool, config_file: Optional[str]):
    """Golf Swing 3D Analyzer CLI."""
    if verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    if config_file:
        # Load custom config if provided
        pass


@cli.command()
def health():
    """Run system health checks."""
    async def _health():
        console.print("🏥 Running health checks...", style="blue")
        
        checker = HealthChecker()
        await checker.run_all_checks()
        
        summary = checker.get_health_summary()
        
        # Create results table
        table = Table(title="Health Check Results")
        table.add_column("Check", style="cyan")
        table.add_column("Status", style="green")
        
        for check, result in summary['details'].items():
            status = "✅ PASS" if result else "❌ FAIL"
            table.add_row(check.replace('_', ' ').title(), status)
        
        console.print(table)
        
        overall_status = "🟢 HEALTHY" if summary['overall_health'] else "🔴 UNHEALTHY"
        console.print(f"\nOverall Status: {overall_status}")
        
        return summary['overall_health']
    
    return asyncio.run(_health())


@cli.command()
@click.argument('video_path', type=click.Path(exists=True))
@click.option('--confidence', '-c', default=0.5, type=float, help='Pose detection confidence')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
def analyze(video_path: str, confidence: float, output: Optional[str]):
    """Analyze golf swing video."""
    async def _analyze():
        console.print(f"🏌️ Analyzing video: {video_path}", style="blue")
        
        try:
            # Validate inputs
            video_file = Path(video_path)
            if not video_file.exists():
                console.print(f"❌ Video file not found: {video_path}", style="red")
                return False
            
            # Create service and analyze
            service = GolfSwingAnalysisService(confidence)
            
            # Mock uploaded file object for CLI
            class MockUploadedFile:
                def __init__(self, path):
                    self.name = path.name
                    self._path = path
                
                def read(self):
                    return self._path.read_bytes()
            
            mock_file = MockUploadedFile(video_file)
            result = await service.analyze_swing(mock_file)
            
            # Display results
            console.print("✅ Analysis complete!", style="green")
            
            metrics_table = Table(title="Swing Metrics")
            metrics_table.add_column("Metric", style="cyan")
            metrics_table.add_column("Value", style="yellow")
            
            for key, value in result['metrics'].items():
                if value is not None:
                    metrics_table.add_row(
                        key.replace('_', ' ').title(),
                        f"{value:.1f}" if isinstance(value, float) else str(value)
                    )
            
            console.print(metrics_table)
            
            # Save results if output specified
            if output:
                import json
                output_path = Path(output)
                output_path.write_text(json.dumps(result, indent=2))
                console.print(f"📁 Results saved to: {output}", style="green")
            
            return True
            
        except Exception as e:
            console.print(f"❌ Analysis failed: {e}", style="red")
            logger.error(f"CLI analysis failed: {e}", exc_info=True)
            return False
    
    return asyncio.run(_analyze())


@cli.command()
def config():
    """Show current configuration."""
    config_dict = Config.get_config_dict()
    
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="yellow")
    
    for key, value in config_dict.items():
        table.add_row(key.replace('_', ' ').title(), str(value))
    
    console.print(table)


@cli.command()
def setup():
    """Setup application directories and validate installation."""
    console.print("🔧 Setting up Golf Swing Analyzer...", style="blue")
    
    try:
        # Create directories
        Config.create_directories()
        console.print("✅ Directories created", style="green")
        
        # Validate config
        Config.validate_config()
        console.print("✅ Configuration validated", style="green")
        
        # Run health checks
        checker = HealthChecker()
        results = asyncio.run(checker.run_all_checks())
        
        summary = checker.get_health_summary()
        if summary['overall_health']:
            console.print("✅ Setup complete! All systems ready.", style="green")
        else:
            console.print("⚠️ Setup complete with warnings. Check health status.", style="yellow")
        
    except Exception as e:
        console.print(f"❌ Setup failed: {e}", style="red")
        return False
    
    return True


def main():
    """Main CLI entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!", style="blue")
        sys.exit(0)
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    main()
