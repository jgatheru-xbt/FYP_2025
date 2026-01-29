import json
import os
from datetime import datetime
from pathlib import Path

class ReportsStorage:
    """Manages persistent storage of AI risk assessment reports."""

    def __init__(self, storage_file="reports_history.json"):
        self.storage_file = Path(__file__).parent.parent / storage_file
        self.reports = []
        self.load_reports()

    def load_reports(self):
        """Load reports from JSON file."""
        try:
            if self.storage_file.exists():
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Validate data structure
                    if isinstance(data, list):
                        self.reports = data
                    else:
                        print("Warning: Invalid reports data structure, starting fresh")
                        self.reports = []
            else:
                self.reports = []
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: Could not load reports: {e}, starting fresh")
            self.reports = []

    def save_reports(self):
        """Save reports to JSON file."""
        try:
            # Create backup if file exists
            if self.storage_file.exists():
                backup_file = self.storage_file.with_suffix('.json.backup')
                self.storage_file.replace(backup_file)

            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.reports, f, indent=2, ensure_ascii=False)

            # Remove backup on successful save
            if backup_file.exists():
                backup_file.unlink()

        except Exception as e:
            print(f"Error saving reports: {e}")
            # Restore backup if save failed
            if backup_file.exists():
                backup_file.replace(self.storage_file)

    def add_report(self, input_data, report_text, simulation_data):
        """Add a new report to storage."""
        report_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "input_data": input_data,
            "report": report_text,
            "simulation_data": simulation_data
        }

        self.reports.append(report_entry)
        self.save_reports()

    def get_reports(self, limit=None):
        """Get all reports sorted by timestamp (newest first)."""
        sorted_reports = sorted(self.reports, key=lambda x: x["timestamp"], reverse=True)
        return sorted_reports[:limit] if limit else sorted_reports

    def delete_report(self, timestamp):
        """Delete a report by timestamp."""
        self.reports = [r for r in self.reports if r["timestamp"] != timestamp]
        self.save_reports()

    def clear_old_reports(self, keep_last=100):
        """Keep only the most recent reports."""
        if len(self.reports) > keep_last:
            self.reports = sorted(self.reports, key=lambda x: x["timestamp"], reverse=True)[:keep_last]
            self.save_reports()

# Global instance
reports_storage = ReportsStorage()