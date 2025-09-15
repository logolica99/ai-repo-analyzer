"""
Health report formatter for displaying repository health analysis results.
"""

from typing import List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.text import Text
from rich.columns import Columns
from rich.align import Align

from .types import OutputFormat
from .health_analyzer import HealthReport, HealthCategory, HealthMetric


class HealthFormatter:
    """Formats health reports for different output formats."""
    
    def __init__(self, output_format: OutputFormat):
        self.output_format = output_format
        self.console = Console()
    
    def format_health_report(self, health_report: HealthReport) -> str:
        """Format health report based on output format."""
        if self.output_format == OutputFormat.JSON:
            return self._format_json(health_report)
        elif self.output_format == OutputFormat.MARKDOWN:
            return self._format_markdown(health_report)
        else:
            return self._format_text(health_report)
    
    def _format_text(self, health_report: HealthReport) -> str:
        """Format health report as text."""
        output = []
        
        # Header
        output.append("🏥 Repository Health Report")
        output.append("=" * 50)
        output.append(f"Repository: {health_report.repository.full_name}")
        output.append(f"Analysis Date: {health_report.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"Overall Score: {health_report.overall_score:.1%}")
        output.append(f"Overall Status: {health_report.overall_status.upper()}")
        output.append("")
        
        # Summary
        output.append("📋 Summary")
        output.append("-" * 20)
        output.append(health_report.summary)
        output.append("")
        
        # Overall Health Bar
        status_emoji = self._get_status_emoji(health_report.overall_status)
        bar_length = 20
        filled_length = int(health_report.overall_score * bar_length)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        output.append(f"Overall Health: {status_emoji} [{bar}] {health_report.overall_score:.1%}")
        output.append("")
        
        # Categories
        output.append("📊 Health Categories")
        output.append("-" * 30)
        
        for category in health_report.categories:
            status_emoji = self._get_status_emoji(category.status)
            output.append(f"\n{status_emoji} {category.name}")
            output.append(f"   Score: {category.overall_score:.1%} ({category.status})")
            output.append(f"   Description: {category.description}")
            
            # Metrics
            for metric in category.metrics:
                metric_emoji = self._get_status_emoji(metric.status)
                output.append(f"   {metric_emoji} {metric.name}: {metric.score:.1%}")
                output.append(f"      {metric.details}")
                
                if metric.recommendations:
                    output.append("      Recommendations:")
                    for rec in metric.recommendations[:3]:  # Show top 3
                        output.append(f"        • {rec}")
        
        # Critical Issues
        if health_report.critical_issues:
            output.append("\n🚨 Critical Issues")
            output.append("-" * 30)
            for issue in health_report.critical_issues:
                output.append(f"• {issue}")
        
        # Recommendations
        if health_report.recommendations:
            output.append("\n💡 Top Recommendations")
            output.append("-" * 30)
            for i, rec in enumerate(health_report.recommendations[:5], 1):
                output.append(f"{i}. {rec}")
        
        return "\n".join(output)
    
    def _format_markdown(self, health_report: HealthReport) -> str:
        """Format health report as markdown."""
        output = []
        
        # Header
        output.append("# 🏥 Repository Health Report")
        output.append("")
        output.append(f"**Repository:** {health_report.repository.full_name}")
        output.append(f"**Analysis Date:** {health_report.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"**Overall Score:** {health_report.overall_score:.1%}")
        output.append(f"**Overall Status:** {health_report.overall_status.upper()}")
        output.append("")
        
        # Summary
        output.append("## 📋 Summary")
        output.append("")
        output.append(health_report.summary)
        output.append("")
        
        # Overall Health Bar
        status_emoji = self._get_status_emoji(health_report.overall_status)
        bar_length = 20
        filled_length = int(health_report.overall_score * bar_length)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        output.append(f"**Overall Health:** {status_emoji} `[{bar}] {health_report.overall_score:.1%}`")
        output.append("")
        
        # Categories
        output.append("## 📊 Health Categories")
        output.append("")
        
        for category in health_report.categories:
            status_emoji = self._get_status_emoji(category.status)
            output.append(f"### {status_emoji} {category.name}")
            output.append("")
            output.append(f"**Score:** {category.overall_score:.1%} ({category.status})")
            output.append(f"**Description:** {category.description}")
            output.append("")
            
            # Metrics table
            output.append("| Metric | Score | Status | Details |")
            output.append("|--------|-------|--------|---------|")
            
            for metric in category.metrics:
                metric_emoji = self._get_status_emoji(metric.status)
                output.append(f"| {metric_emoji} {metric.name} | {metric.score:.1%} | {metric.status} | {metric.details} |")
            
            output.append("")
            
            # Recommendations for this category
            category_recs = []
            for metric in category.metrics:
                category_recs.extend(metric.recommendations)
            
            if category_recs:
                output.append("**Recommendations:**")
                output.append("")
                for rec in category_recs[:3]:  # Show top 3
                    output.append(f"- {rec}")
                output.append("")
        
        # Critical Issues
        if health_report.critical_issues:
            output.append("## 🚨 Critical Issues")
            output.append("")
            for issue in health_report.critical_issues:
                output.append(f"- {issue}")
            output.append("")
        
        # Recommendations
        if health_report.recommendations:
            output.append("## 💡 Top Recommendations")
            output.append("")
            for i, rec in enumerate(health_report.recommendations[:10], 1):
                output.append(f"{i}. {rec}")
            output.append("")
        
        return "\n".join(output)
    
    def _format_json(self, health_report: HealthReport) -> str:
        """Format health report as JSON."""
        import json
        from dataclasses import asdict
        
        # Convert dataclasses to dictionaries
        def convert_to_dict(obj):
            if hasattr(obj, '__dataclass_fields__'):
                # It's a dataclass
                result = {}
                for field_name, field_value in obj.__dict__.items():
                    if isinstance(field_value, list):
                        result[field_name] = [convert_to_dict(item) for item in field_value]
                    elif hasattr(field_value, '__dataclass_fields__'):
                        result[field_name] = convert_to_dict(field_value)
                    else:
                        result[field_name] = field_value
                return result
            elif isinstance(obj, list):
                return [convert_to_dict(item) for item in obj]
            else:
                return obj
        
        data = {
            "repository": {
                "full_name": health_report.repository.full_name,
                "owner": health_report.repository.owner,
                "name": health_report.repository.name,
                "description": health_report.repository.description,
                "language": health_report.repository.language,
                "stars": health_report.repository.stars,
                "forks": health_report.repository.forks
            },
            "analysis_date": health_report.analysis_date.isoformat(),
            "overall_score": health_report.overall_score,
            "overall_status": health_report.overall_status,
            "summary": health_report.summary,
            "categories": convert_to_dict(health_report.categories),
            "critical_issues": health_report.critical_issues,
            "recommendations": health_report.recommendations
        }
        
        return json.dumps(data, indent=2, default=str)
    
    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for status."""
        status_emojis = {
            "excellent": "🟢",
            "good": "🟡",
            "fair": "🟠",
            "poor": "🔴",
            "critical": "💀"
        }
        return status_emojis.get(status, "❓")
    
    def display_health_report(self, health_report: HealthReport) -> None:
        """Display health report in the console with rich formatting."""
        
        # Header Panel
        header_text = Text()
        header_text.append("🏥 Repository Health Report\n", style="bold blue")
        header_text.append(f"Repository: {health_report.repository.full_name}\n", style="white")
        header_text.append(f"Analysis Date: {health_report.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}\n", style="dim")
        
        status_emoji = self._get_status_emoji(health_report.overall_status)
        header_text.append(f"Overall Status: {status_emoji} {health_report.overall_status.upper()}", style="bold")
        
        header_panel = Panel(header_text, title="Health Analysis", border_style="blue")
        self.console.print(header_panel)
        
        # Overall Score Progress Bar
        progress = Progress(
            TextColumn("[bold blue]Overall Health"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )
        
        with progress:
            task = progress.add_task("Health Score", total=100, completed=health_report.overall_score * 100)
        
        self.console.print()
        
        # Summary
        summary_panel = Panel(
            health_report.summary,
            title="📋 Summary",
            border_style="green"
        )
        self.console.print(summary_panel)
        
        # Categories Table
        categories_table = Table(title="📊 Health Categories", show_header=True, header_style="bold magenta")
        categories_table.add_column("Category", style="cyan", no_wrap=True)
        categories_table.add_column("Score", justify="right", style="green")
        categories_table.add_column("Status", justify="center")
        categories_table.add_column("Description", style="white")
        
        for category in health_report.categories:
            status_emoji = self._get_status_emoji(category.status)
            categories_table.add_row(
                category.name,
                f"{category.overall_score:.1%}",
                f"{status_emoji} {category.status}",
                category.description
            )
        
        self.console.print(categories_table)
        
        # Detailed Metrics for each category
        for category in health_report.categories:
            if category.metrics:
                metrics_table = Table(title=f"📈 {category.name} - Detailed Metrics", show_header=True)
                metrics_table.add_column("Metric", style="cyan")
                metrics_table.add_column("Score", justify="right", style="green")
                metrics_table.add_column("Status", justify="center")
                metrics_table.add_column("Details", style="white")
                
                for metric in category.metrics:
                    metric_emoji = self._get_status_emoji(metric.status)
                    metrics_table.add_row(
                        metric.name,
                        f"{metric.score:.1%}",
                        f"{metric_emoji} {metric.status}",
                        metric.details
                    )
                
                self.console.print(metrics_table)
        
        # Critical Issues
        if health_report.critical_issues:
            critical_panel = Panel(
                "\n".join(f"• {issue}" for issue in health_report.critical_issues),
                title="🚨 Critical Issues",
                border_style="red"
            )
            self.console.print(critical_panel)
        
        # Recommendations
        if health_report.recommendations:
            rec_text = Text()
            for i, rec in enumerate(health_report.recommendations[:10], 1):
                rec_text.append(f"{i}. {rec}\n", style="white")
            
            rec_panel = Panel(
                rec_text,
                title="💡 Top Recommendations",
                border_style="yellow"
            )
            self.console.print(rec_panel)
    
    def save_to_file(self, health_report: HealthReport, file_path: str) -> None:
        """Save health report to file."""
        content = self.format_health_report(health_report)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
