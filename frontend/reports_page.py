import customtkinter as ctk
import tkinter as tk
import os
from tkinter import messagebox
from datetime import datetime
import Backend.reports_storage as reports_storage

# Define common fonts and colors
FONT = ("Roboto", 12)
TITLE_FONT = ("Roboto", 20, "bold")
SUBTITLE_FONT = ("Roboto", 14, "bold")
LABEL_FONT = ("Roboto", 11)
SMALL_FONT = ("Roboto", 9)

# Color Palette
COLOR_BG = "#212121"
COLOR_CARD = "#2b2b2b"
COLOR_ACCENT = "#00cec9"
COLOR_BUTTON = "#27ae60"
COLOR_WARNING = "#e67e22"
COLOR_DANGER = "#e74c3c"
COLOR_TEXT = "#ffffff"
COLOR_TEXT_SECONDARY = "#b0b0b0"


class ReportCard(ctk.CTkFrame):
    """Card displaying a single report entry."""

    def __init__(self, master, report_data, delete_callback, **kwargs):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=12, **kwargs)

        self.report_data = report_data
        self.delete_callback = delete_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header with timestamp and severity
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)

        timestamp = ctk.CTkLabel(
            header_frame,
            text=report_data["timestamp"],
            font=LABEL_FONT,
            text_color=COLOR_TEXT_SECONDARY
        )
        timestamp.grid(row=0, column=0, sticky="w")

        # Extract severity from report
        severity = self._extract_severity(report_data["report"])
        severity_color = self._get_severity_color(severity)

        severity_label = ctk.CTkLabel(
            header_frame,
            text=severity,
            font=("Roboto", 10, "bold"),
            text_color=severity_color
        )
        severity_label.grid(row=0, column=1, sticky="e")

        # Report preview (first few lines)
        preview_text = self._get_preview(report_data["report"])

        preview_label = ctk.CTkLabel(
            self,
            text=preview_text,
            font=SMALL_FONT,
            text_color=COLOR_TEXT,
            justify="left",
            wraplength=400
        )
        preview_label.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

        # Action buttons
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 10))

        view_btn = ctk.CTkButton(
            buttons_frame,
            text="View Full Report",
            fg_color=COLOR_ACCENT,
            hover_color="#00a8a8",
            height=28,
            font=SMALL_FONT,
            command=self._view_full_report
        )
        view_btn.pack(side="left", padx=(0, 8))

        delete_btn = ctk.CTkButton(
            buttons_frame,
            text="Delete",
            fg_color=COLOR_DANGER,
            hover_color="#c0392b",
            height=28,
            font=SMALL_FONT,
            command=self._delete_report
        )
        delete_btn.pack(side="left")

    def _extract_severity(self, report_text):
        """Extract severity level from report text."""
        if "CRITICAL" in report_text:
            return "CRITICAL"
        elif "HIGH" in report_text:
            return "HIGH"
        elif "MEDIUM" in report_text:
            return "MEDIUM"
        elif "LOW" in report_text:
            return "LOW"
        return "UNKNOWN"

    def _get_severity_color(self, severity):
        """Get color for severity level."""
        colors = {
            "CRITICAL": "#e74c3c",
            "HIGH": "#e67e22",
            "MEDIUM": "#f39c12",
            "LOW": "#27ae60",
            "UNKNOWN": COLOR_TEXT_SECONDARY
        }
        return colors.get(severity, COLOR_TEXT_SECONDARY)

    def _get_preview(self, report_text):
        """Get preview text (first 2-3 lines)."""
        lines = report_text.split('\n')[:3]
        return '\n'.join(lines) + ('...' if len(report_text.split('\n')) > 3 else '')

    def _view_full_report(self):
        """Show full report in a popup window."""
        popup = ctk.CTkToplevel(self)
        popup.transient(self)  # Keep window on top
        popup.grab_set()  # Make window modal
        popup.title("AI Risk Assessment Report")
        popup.geometry("700x750")
        popup.configure(fg_color=COLOR_BG)

        # Title
        title_label = ctk.CTkLabel(
            popup,
            text=f"Report - {self.report_data['timestamp']}",
            font=TITLE_FONT,
            text_color=COLOR_TEXT
        )
        title_label.pack(pady=(20, 10))

        # Main content frame
        main_frame = ctk.CTkScrollableFrame(popup, fg_color=COLOR_BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=0)

        # Original Report Section
        report_title_label = ctk.CTkLabel(
            main_frame,
            text="Full Report",
            font=SUBTITLE_FONT,
            text_color=COLOR_TEXT
        )
        report_title_label.pack(anchor="w", pady=(10, 5))

        report_textbox = ctk.CTkTextbox(
            main_frame,
            wrap="word",
            font=FONT,
            text_color=COLOR_TEXT,
            fg_color=COLOR_CARD,
            height=200,
            border_spacing=5
        )
        report_textbox.pack(fill="x", expand=True)
        report_textbox.insert("0.0", self.report_data["report"])
        report_textbox.configure(state="disabled")

        # AI-Generated Summary Section
        summary_title_label = ctk.CTkLabel(
            main_frame,
            text="AI-Generated Summary",
            font=SUBTITLE_FONT,
            text_color=COLOR_TEXT
        )
        summary_title_label.pack(anchor="w", pady=(20, 5))

        summary_textbox = ctk.CTkTextbox(
            main_frame,
            wrap="word",
            font=FONT,
            text_color=COLOR_TEXT,
            fg_color=COLOR_CARD,
            height=200,
            border_spacing=5
        )
        summary_textbox.pack(fill="x", expand=True)
        summary_textbox.insert("0.0", "Generating summary...")

        # Generate summary in a separate thread to avoid UI freeze
        def generate_and_display_summary():
            try:
                from Backend.risk_summary_generator import RiskSummaryGenerator
                generator = RiskSummaryGenerator()
                summary = generator.generate_summary(self.report_data["input_data"])
                summary_textbox.configure(state="normal")
                summary_textbox.delete("0.0", "end")
                summary_textbox.insert("0.0", summary)
                summary_textbox.configure(state="disabled")
            except Exception as e:
                summary_textbox.configure(state="normal")
                summary_textbox.delete("0.0", "end")
                summary_textbox.insert("0.0", f"Error generating summary: {e}")
                summary_textbox.configure(state="disabled")

        import threading
        threading.Thread(target=generate_and_display_summary, daemon=True).start()

        # Action buttons frame
        action_frame = ctk.CTkFrame(popup, fg_color="transparent")
        action_frame.pack(pady=(15, 20))

        copy_btn = ctk.CTkButton(
            action_frame,
            text="Copy Report",
            fg_color=COLOR_ACCENT,
            hover_color="#00a8a8",
            width=120,
            command=lambda: self._copy_to_clipboard(popup, self.report_data["report"], "Report")
        )
        copy_btn.pack(side="left", padx=10)
        
        copy_summary_btn = ctk.CTkButton(
            action_frame,
            text="Copy Summary",
            fg_color=COLOR_ACCENT,
            hover_color="#00a8a8",
            width=120,
            command=lambda: self._copy_to_clipboard(popup, summary_textbox.get("0.0", "end"), "Summary")
        )
        copy_summary_btn.pack(side="left", padx=10)

        save_btn = ctk.CTkButton(
            action_frame,
            text="Save",
            fg_color=COLOR_BUTTON,
            hover_color="#219150",
            width=100,
            command=self._save_to_file
        )
        save_btn.pack(side="left", padx=10)

        # Close button
        close_btn = ctk.CTkButton(
            action_frame,
            text="Close",
            fg_color="transparent",
            border_width=1,
            border_color="#555555",
            hover_color="#333333",
            width=80,
            command=popup.destroy
        )
        close_btn.pack(side="left", padx=10)

    def _copy_to_clipboard(self, popup, content, content_type="Report"):
        """Copy specified content to clipboard."""
        popup.clipboard_clear()
        popup.clipboard_append(content)
        messagebox.showinfo("Copied", f"{content_type} text copied to clipboard!", parent=popup)

    def _save_to_file(self):
        """Save report to a text file."""
        filename = f"report_{self.report_data['timestamp'].replace(':', '-').replace(' ', '_')}.txt"
        
        # Use filedialog to ask where to save
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=filename,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Report"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Timestamp: {self.report_data['timestamp']}\n")
                    f.write(f"Input Data: {self.report_data['input_data']}\n")
                    f.write("-" * 50 + "\n\n")
                    f.write(self.report_data["report"])
                messagebox.showinfo("Saved", f"Report saved to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def _delete_report(self):
        """Delete this report."""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this report?"):
            self.delete_callback(self.report_data["timestamp"])
            self.destroy()


class ReportsPage(ctk.CTkFrame):
    """Main Reports page displaying historical AI risk assessments."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_BG, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Historical Reports",
            font=TITLE_FONT,
            text_color=COLOR_TEXT
        )
        title_label.grid(row=0, column=0, pady=(20, 10), padx=20, sticky="w")

        # Scrollable frame for reports
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Load and display reports
        self.load_reports()

    def load_reports(self):
        """Load and display all reports."""
        # Clear existing
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        reports = reports_storage.reports_storage.get_reports()

        if not reports:
            # No reports message
            empty_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No reports available.\nRun a simulation and generate a report to see it here.",
                font=SUBTITLE_FONT,
                text_color=COLOR_TEXT_SECONDARY,
                justify="center"
            )
            empty_label.pack(pady=50)
            return

        # Display reports
        for report in reports:
            report_card = ReportCard(
                self.scrollable_frame,
                report,
                self.delete_report
            )
            report_card.pack(fill="x", pady=8, padx=10)

    def delete_report(self, timestamp):
        """Delete a report and refresh display."""
        reports_storage.reports_storage.delete_report(timestamp)
        self.load_reports()

    def refresh_reports(self):
        """Refresh the reports display."""
        self.load_reports()