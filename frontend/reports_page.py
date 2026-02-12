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


import customtkinter as ctk
import tkinter as tk
import os
from tkinter import messagebox
from datetime import datetime
import Backend.reports_storage as reports_storage
from fpdf import FPDF
import matplotlib.pyplot as plt
import io

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
            font=FONT,
            command=self._view_full_report
        )
        view_btn.pack(side="left", padx=(0, 8))

        delete_btn = ctk.CTkButton(
            buttons_frame,
            text="Delete",
            fg_color=COLOR_DANGER,
            hover_color="#c0392b",
            height=28,
            font=FONT,
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
        popup.transient(self)
        popup.grab_set()
        popup.title("Risk Assessment Report")
        popup.geometry("700x850")
        popup.configure(fg_color=COLOR_BG)

        title_label = ctk.CTkLabel(popup, text=f"Report - {self.report_data['timestamp']}", font=TITLE_FONT, text_color=COLOR_TEXT)
        title_label.pack(pady=(20, 10))

        main_frame = ctk.CTkScrollableFrame(popup, fg_color=COLOR_BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=0)

        # Simulation Metrics Section
        sim_data = self.report_data.get("simulation_data")
        if sim_data:
            metrics_title_label = ctk.CTkLabel(main_frame, text="Simulation Metrics", font=SUBTITLE_FONT, text_color=COLOR_TEXT)
            metrics_title_label.pack(anchor="w", pady=(10, 5))

            metrics_text_content = ""
            for key, value in sim_data.items():
                formatted_key = key.replace('_', ' ').title()
                if key != "file_type_distribution_pct":
                    if isinstance(value, dict):
                        metrics_text_content += f"{formatted_key}:\n"
                        for sub_key, sub_value in value.items():
                            metrics_text_content += f"  - {sub_key}: {sub_value:.2f}%\n"
                    elif isinstance(value, float):
                        metrics_text_content += f"{formatted_key}: {value:.2f}\n"
                    else:
                        metrics_text_content += f"{formatted_key}: {value}\n"
            
            metrics_textbox = ctk.CTkTextbox(main_frame, wrap="word", font=FONT, text_color=COLOR_TEXT, fg_color=COLOR_CARD, height=200, border_spacing=5)
            metrics_textbox.pack(fill="x", expand=False, pady=(0, 10))
            metrics_textbox.insert("0.0", metrics_text_content)
            metrics_textbox.configure(state="disabled")

            # File Type Distribution Chart
            dist = sim_data.get("file_type_distribution_pct")
            if dist and isinstance(dist, dict) and sum(dist.values()) > 0:
                chart_title_label = ctk.CTkLabel(main_frame, text="File Type Distribution", font=SUBTITLE_FONT, text_color=COLOR_TEXT)
                chart_title_label.pack(anchor="w", pady=(10, 5))

                plt.style.use('default')
                fig, ax = plt.subplots(figsize=(6, 3))
                labels = list(dist.keys())
                sizes = list(dist.values())
                
                ax.barh(labels, sizes, color='#00cec9')
                ax.set_xlabel('Percentage (%)')
                ax.set_facecolor('#2b2b2b')
                fig.patch.set_facecolor('#212121')
                ax.tick_params(colors='#ffffff')
                ax.xaxis.label.set_color('#ffffff')

                buf = io.BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#212121')
                buf.seek(0)
                
                # Create image frame
                from PIL import Image, ImageTk
                img = Image.open(buf)
                img_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(600, 200))
                img_label = ctk.CTkLabel(main_frame, image=img_ctk, text="")
                img_label.image = img_ctk
                img_label.pack(pady=(0, 10))
                plt.close(fig)
                # AI Summary
                report_title_label = ctk.CTkLabel(main_frame, text="Summary", font=SUBTITLE_FONT, text_color=COLOR_TEXT)
                report_title_label.pack(anchor="w", pady=(20, 5))

                report_textbox = ctk.CTkTextbox(main_frame, wrap="word", font=FONT, text_color=COLOR_TEXT, fg_color=COLOR_CARD, height=100, border_spacing=5)
                report_textbox.pack(fill="x", expand=False)
                report_textbox.insert("0.0", self.report_data["report"])
                report_textbox.configure(state="disabled")


        # Action buttons frame
        action_frame = ctk.CTkFrame(popup, fg_color="transparent")
        action_frame.pack(pady=(15, 20))

        copy_btn = ctk.CTkButton(action_frame, text="Copy Report", fg_color=COLOR_ACCENT, hover_color="#00a8a8", width=120, command=lambda: self._copy_to_clipboard(popup, self.report_data["report"], "Report"))
        copy_btn.pack(side="left", padx=10)
        
        save_btn = ctk.CTkButton(action_frame, text="Save as PDF", fg_color=COLOR_BUTTON, hover_color="#219150", width=120, command=self._save_report_dialog)
        save_btn.pack(side="left", padx=10)

        close_btn = ctk.CTkButton(action_frame, text="Close", fg_color="transparent", border_width=1, border_color="#555555", hover_color="#333333", width=80, command=popup.destroy)
        close_btn.pack(side="left", padx=10)

    def _copy_to_clipboard(self, popup, content, content_type="Report"):
        """Copy specified content to clipboard."""
        popup.clipboard_clear()
        popup.clipboard_append(content)
        messagebox.showinfo("Copied", f"{content_type} text copied to clipboard!", parent=popup)

    def _save_report_dialog(self):
        """Open a dialog to save the report as a PDF."""
        filename = f"report_{self.report_data['timestamp'].replace(':', '-').replace(' ', '_')}.pdf"
        
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=filename,
            filetypes=[("PDF Documents", "*.pdf"), ("All files", "*.*")],
            title="Save Report as PDF"
        )
        
        if file_path:
            try:
                self._save_to_pdf(file_path)
                messagebox.showinfo("Saved", f"Report saved to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save PDF file: {e}")

    def _save_to_pdf(self, file_path: str):
        """Generate and save a PDF report."""
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 10, "Risk Assessment Report", 0, 1, "C")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, f"Timestamp: {self.report_data['timestamp']}", 0, 1, "C")
        pdf.ln(10)

        sim_data = self.report_data.get("simulation_data")
        if sim_data:
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "Simulation Metrics", 0, 1)
            pdf.set_font("Helvetica", "", 10)
            
            for key, value in sim_data.items():
                formatted_key = key.replace('_', ' ').title()
                if key != "file_type_distribution_pct":
                    if isinstance(value, float):
                        pdf.cell(0, 6, f"- {formatted_key}: {value:.2f}", 0, 1)
                    else:
                        pdf.cell(0, 6, f"- {formatted_key}: {value}", 0, 1)
            pdf.ln(5)

            # Chart
            dist = sim_data.get("file_type_distribution_pct")
            if dist and isinstance(dist, dict) and sum(dist.values()) > 0:
                plt.style.use('default')
                fig, ax = plt.subplots(figsize=(6, 4))
                labels = list(dist.keys())
                sizes = list(dist.values())
                
                ax.barh(labels, sizes, color='#00cec9')
                ax.set_xlabel('Percentage (%)')
                ax.set_title('File Type Distribution')
                ax.set_facecolor('#f5f5f5')
                fig.patch.set_facecolor('#ffffff')

                buf = io.BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight')
                buf.seek(0)
                pdf.image(buf, x=pdf.get_x() + 20, w=pdf.w - 100)
                plt.close(fig)
                pdf.ln(70)


        # AI Summary
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "AI-Generated Summary", 0, 1)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, self.report_data.get("report", "No summary available."))

        pdf.output(file_path)

    def _delete_report(self):
        """Delete this report."""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this report?"):
            self.delete_callback(self.report_data["timestamp"])
            self.destroy()


class ReportsPage(ctk.CTkFrame):
    """Main Reports page displaying historical Risk assessments."""

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