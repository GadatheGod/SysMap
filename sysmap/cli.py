"""CLI entry point for sysmap."""

import argparse
import json
import sys
import os
import webbrowser
import threading
from pathlib import Path


def cmd_report(args):
    """Generate system report."""
    from sysmap.server.export_html import generate_html_report
    from sysmap.server.export_pdf import generate_pdf_report
    from sysmap.collector import collect_all

    output_path = args.output or "sysmap_report.html"

    print("Collecting system information...")
    snapshot = collect_all()

    print(f"Generating HTML report: {output_path}")
    generate_html_report(snapshot, output_path)
    print(f"HTML report saved to: {output_path}")

    if args.pdf:
        pdf_path = output_path.replace('.html', '.pdf')
        try:
            print("Generating PDF report...")
            generate_pdf_report(pdf_path, output_path)
            print(f"PDF report saved to: {pdf_path}")
        except ImportError as e:
            print(f"PDF generation skipped: {e}")
            print("Install with: pip install sysmap[pdf]")

    if args.json:
        json_path = output_path.replace('.html', '.json')
        with open(json_path, 'w') as f:
            json.dump(snapshot.model_dump(mode='json'), f, indent=2)
        print(f"JSON data saved to: {json_path}")

    print("\nReport generated successfully!")
    print(f"Open with: xdg-open '{output_path}'")


def cmd_info(args):
    """Print quick system summary."""
    from sysmap.collector import collect_summary

    summary = collect_summary()
    print("=" * 60)
    print("  SysMap - System Summary")
    print("=" * 60)
    print(f"  Platform:    {summary['platform']}")
    print(f"  Hostname:    {summary['hostname']}")
    print(f"  CPU:         {summary['cpu']}")
    print(f"  RAM:         {summary['ram_gb']} GB")
    print(f"  GPU:         {summary['gpu']}")
    print(f"  Storage:     {summary['storage_gb']:.0f} GB")
    print(f"  OS:          {summary['os']}")
    print(f"  Processes:   {summary['processes']}")
    print("=" * 60)


def cmd_server(args):
    """Launch the web dashboard."""
    from uvicorn import Config, Server

    port = args.port or 8000

    print(f"Starting SysMap server on http://localhost:{port}")
    print("Press Ctrl+C to stop")

    config = Config(
        app="server.app:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=False,
    )
    server = Server(config)

    # Open browser after a short delay
    def open_browser():
        import time
        time.sleep(1)
        webbrowser.open(f"http://localhost:{port}")

    threading.Thread(target=open_browser, daemon=True).start()
    server.run()


def cmd_export_json(args):
    """Export raw JSON data."""
    from sysmap.collector import collect_all

    output_path = args.output or "sysmap_data.json"
    snapshot = collect_all()

    with open(output_path, 'w') as f:
        json.dump(snapshot.model_dump(mode='json'), f, indent=2)

    print(f"JSON data exported to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        prog="sysmap",
        description="SysMap - Complete System Profiler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sysmap              Launch web dashboard
  sysmap info         Quick system summary
  sysmap report       Generate HTML report
  sysmap report --pdf Generate PDF report
  sysmap report --json Generate JSON export
  sysmap export-json  Export raw JSON data
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command')

    # info command
    info_parser = subparsers.add_parser('info', help='Quick system summary')
    info_parser.set_defaults(func=cmd_info)

    # report command
    report_parser = subparsers.add_parser('report', help='Generate system report')
    report_parser.add_argument('-o', '--output', help='Output file path')
    report_parser.add_argument('--pdf', action='store_true', help='Also generate PDF')
    report_parser.add_argument('--json', action='store_true', help='Also generate JSON export')
    report_parser.set_defaults(func=cmd_report)

    # server command
    server_parser = subparsers.add_parser('server', help='Launch web dashboard')
    server_parser.add_argument('-p', '--port', type=int, help='Port number (default: 8000)')
    server_parser.set_defaults(func=cmd_server)

    # export-json command
    export_parser = subparsers.add_parser('export-json', help='Export raw JSON data')
    export_parser.add_argument('-o', '--output', help='Output file path')
    export_parser.set_defaults(func=cmd_export_json)

    # Default: launch server
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(0)

    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
