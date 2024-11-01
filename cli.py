#!/usr/bin/env python3
"""
Command Line Interface for Mobile Price Predictor administration.
"""

import argparse
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from database import prediction_cache
from monitoring import metrics_collector
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def show_status():
    """Show application status and health."""
    print("🔍 Checking application status...")
    
    try:
        # Check database
        db_stats = prediction_cache.get_cache_stats()
        print(f"✅ Database: Connected (Size: {db_stats.get('cache_size_mb', 0)} MB)")
        
        # Check metrics
        current_metrics = metrics_collector.get_current_metrics()
        if current_metrics:
            print(f"✅ Metrics: Collecting (System: {current_metrics['system']['current']['cpu_percent']:.1f}% CPU)")
        else:
            print("⚠️  Metrics: Not available")
        
        # Check configuration
        print(f"✅ Configuration: Loaded (Region: {Config.AWS_REGION})")
        
        print("\n📊 Current Statistics:")
        print(f"   Total Predictions: {db_stats.get('total_predictions', 0)}")
        print(f"   Recent (24h): {db_stats.get('recent_predictions_24h', 0)}")
        print(f"   Average Confidence: {db_stats.get('average_confidence', 0):.1f}%")
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False
    
    return True

def show_cache_stats():
    """Show detailed cache statistics."""
    print("📊 Cache Statistics:")
    print("=" * 40)
    
    try:
        stats = prediction_cache.get_cache_stats()
        
        print(f"Total Predictions: {stats.get('total_predictions', 0)}")
        print(f"Total Accesses: {stats.get('total_accesses', 0)}")
        print(f"Recent (24h): {stats.get('recent_predictions_24h', 0)}")
        print(f"Average Confidence: {stats.get('average_confidence', 0):.1f}%")
        print(f"Cache Size: {stats.get('cache_size_mb', 0):.2f} MB")
        
        # Calculate hit rate
        if stats.get('total_accesses', 0) > 0:
            hit_rate = (stats.get('total_predictions', 0) / stats.get('total_accesses', 0)) * 100
            print(f"Cache Hit Rate: {hit_rate:.1f}%")
        
    except Exception as e:
        print(f"❌ Failed to get cache stats: {e}")

def cleanup_cache(days: int):
    """Clean up old cache entries."""
    print(f"🧹 Cleaning up cache entries older than {days} days...")
    
    try:
        deleted_count = prediction_cache.cleanup_old_predictions(days)
        print(f"✅ Cleaned up {deleted_count} old predictions")
        
        # Show updated stats
        show_cache_stats()
        
    except Exception as e:
        print(f"❌ Cache cleanup failed: {e}")

def show_metrics(hours: int = 24):
    """Show application metrics."""
    print(f"📈 Application Metrics (Last {hours} hours):")
    print("=" * 50)
    
    try:
        current = metrics_collector.get_current_metrics()
        history = metrics_collector.get_metrics_history(hours)
        
        if current:
            print("\n🔄 Current Status:")
            print(f"   CPU Usage: {current['system']['current']['cpu_percent']:.1f}%")
            print(f"   Memory Usage: {current['system']['current']['memory_percent']:.1f}%")
            print(f"   Total Requests: {current['application']['current']['total_requests']}")
            print(f"   Success Rate: {(current['application']['current']['successful_requests'] / max(current['application']['current']['total_requests'], 1)) * 100:.1f}%")
            print(f"   Avg Response Time: {current['application']['current']['average_response_time']:.2f}ms")
        
        if history['system']:
            print(f"\n📊 System Metrics ({len(history['system'])} data points):")
            cpu_values = [m['cpu_percent'] for m in history['system']]
            memory_values = [m['memory_percent'] for m in history['system']]
            
            if cpu_values:
                print(f"   CPU: Min {min(cpu_values):.1f}%, Max {max(cpu_values):.1f}%, Avg {sum(cpu_values)/len(cpu_values):.1f}%")
            if memory_values:
                print(f"   Memory: Min {min(memory_values):.1f}%, Max {max(memory_values):.1f}%, Avg {sum(memory_values)/len(memory_values):.1f}%")
        
        if history['application']:
            print(f"\n📱 Application Metrics ({len(history['application'])} data points):")
            request_values = [m['total_requests'] for m in history['application']]
            response_values = [m['average_response_time'] for m in history['application']]
            
            if request_values:
                print(f"   Requests: Min {min(request_values)}, Max {max(request_values)}, Avg {sum(request_values)/len(request_values):.1f}")
            if response_values:
                print(f"   Response Time: Min {min(response_values):.2f}ms, Max {max(response_values):.2f}ms, Avg {sum(response_values)/len(response_values):.2f}ms")
        
    except Exception as e:
        print(f"❌ Failed to get metrics: {e}")

def export_data(output_file: str, data_type: str):
    """Export data to JSON file."""
    print(f"📤 Exporting {data_type} to {output_file}...")
    
    try:
        if data_type == 'metrics':
            metrics_collector.export_metrics(output_file)
        elif data_type == 'cache':
            # Export cache data
            stats = prediction_cache.get_cache_stats()
            with open(output_file, 'w') as f:
                json.dump(stats, f, indent=2)
        else:
            print(f"❌ Unknown data type: {data_type}")
            return
        
        print(f"✅ Data exported successfully to {output_file}")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")

def show_errors(limit: int = 10):
    """Show recent error logs."""
    print(f"🚨 Recent Errors (Last {limit}):")
    print("=" * 40)
    
    try:
        current_metrics = metrics_collector.get_current_metrics()
        if current_metrics and 'errors' in current_metrics:
            errors = current_metrics['errors']['recent_errors'][-limit:]
            
            if not errors:
                print("✅ No errors recorded")
                return
            
            for error in errors:
                print(f"\n⏰ {error['timestamp']}")
                print(f"   Type: {error['type']}")
                print(f"   Message: {error['message']}")
                if error.get('stack_trace'):
                    print(f"   Stack: {error['stack_trace'][:100]}...")
        else:
            print("⚠️  No error data available")
            
    except Exception as e:
        print(f"❌ Failed to get error logs: {e}")

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Mobile Price Predictor CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py status                    # Show application status
  python cli.py cache-stats              # Show cache statistics
  python cli.py cleanup-cache --days 7   # Clean up old cache entries
  python cli.py metrics --hours 48       # Show metrics for last 48 hours
  python cli.py export --type metrics --output metrics.json  # Export metrics
  python cli.py errors --limit 20        # Show last 20 errors
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show application status')
    
    # Cache stats command
    subparsers.add_parser('cache-stats', help='Show cache statistics')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup-cache', help='Clean up old cache entries')
    cleanup_parser.add_argument('--days', type=int, default=30, help='Days to keep (default: 30)')
    
    # Metrics command
    metrics_parser = subparsers.add_parser('metrics', help='Show application metrics')
    metrics_parser.add_argument('--hours', type=int, default=24, help='Hours to show (default: 24)')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export data to file')
    export_parser.add_argument('--type', choices=['metrics', 'cache'], required=True, help='Type of data to export')
    export_parser.add_argument('--output', required=True, help='Output file path')
    
    # Errors command
    errors_parser = subparsers.add_parser('errors', help='Show recent error logs')
    errors_parser.add_argument('--limit', type=int, default=10, help='Number of errors to show (default: 10)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'status':
            show_status()
        elif args.command == 'cache-stats':
            show_cache_stats()
        elif args.command == 'cleanup-cache':
            cleanup_cache(args.days)
        elif args.command == 'metrics':
            show_metrics(args.hours)
        elif args.command == 'export':
            export_data(args.output, args.type)
        elif args.command == 'errors':
            show_errors(args.limit)
        else:
            print(f"❌ Unknown command: {args.command}")
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.exception("CLI error")

if __name__ == '__main__':
    main() 