"""Command-line interface entry point for VN Tech Job Radar Pipeline."""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from rich.console import Console
from rich.table import Table

from src.pipeline import JobRadarPipeline

console = Console()


def setup_logging(verbose: bool = False) -> None:
    """Configures structured logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


async def main_async(args: argparse.Namespace) -> int:
    """Asynchronous entrypoint."""
    console.rule("[bold cyan]📡 VN Tech Job Radar - Ingestion Engine[/bold cyan]")

    pipeline = JobRadarPipeline(
        data_dir=args.data_dir,
        ttl_days=args.ttl,
    )

    console.print(f"[dim]Executing scrapers with TTL = {args.ttl} days, storage = {args.data_dir}[/dim]")
    
    with console.status("[bold green]Harvesting and processing tech jobs...", spinner="dots"):
        telemetry = await pipeline.run()

    # Telemetry Summary Table
    table = Table(title="📊 Pipeline Execution Report", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold green")

    table.add_row("Execution Duration", f"{telemetry.duration_seconds}s")
    table.add_row("Scrapers Executed", str(telemetry.scrapers_executed))
    table.add_row("Scrapers Failed", f"[red]{telemetry.scrapers_failed}[/red]" if telemetry.scrapers_failed > 0 else "0")
    table.add_row("Raw Postings Harvested", str(telemetry.total_harvested_raw))
    table.add_row("Valid Jobs Processed", str(telemetry.valid_jobs_processed))
    table.add_row("New Jobs Added", str(telemetry.new_jobs_added))
    table.add_row("Existing Jobs Refreshed", str(telemetry.existing_jobs_updated))
    table.add_row("Total Active Jobs in Radar", str(telemetry.total_active_jobs))

    console.print(table)

    if telemetry.scrapers_failed > 0:
        console.print(f"[yellow]Warning: Some sources encountered errors: {', '.join(telemetry.failed_sources)}[/yellow]")

    console.print("[bold green]✔ Ingestion Pipeline completed successfully![/bold green]")
    return 0


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="VN Tech Job Radar Ingestion Pipeline")
    parser.add_argument("--data-dir", default="data", help="Path to data directory (default: data)")
    parser.add_argument("--ttl", type=int, default=30, help="TTL in days for job expiration (default: 30)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")

    args = parser.parse_args()
    setup_logging(args.verbose)

    exit_code = asyncio.run(main_async(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
