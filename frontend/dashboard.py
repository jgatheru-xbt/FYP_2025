import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import threading
import tkinter as tk
import customtkinter as ctk

from Backend.redirector import LogRedirector
# from Backend.encrypt import simulate_encrypt_folder
import AI.shared_data as shared_data
import Backend.reports_storage as reports_storage


import sys


try:
    from Backend.risk_summary_generator import RiskSummaryGenerator
except ImportError:
    RiskSummaryGenerator = None

# Define common fonts
FONT = ("Roboto", 12)
TITLE_FONT = ("Roboto", 20, "bold")
SIDEBAR_FONT = ("Roboto", 14, "bold")
BADGE_FONT = ("Roboto", 10, "bold")
MONO_FONT = ("Consolas", 9)

# Color Palette
COLOR_BG = "#212121"
COLOR_CARD = "#2b2b2b"
COLOR_STATUS_SIMULATOR = "#e67e22"  # Orange
COLOR_STATUS_SANDBOX = "#00cec9"  # Cyan
COLOR_TERMINAL_BG = "#000000"
COLOR_TERMINAL_TEXT = "#2ecc71"  # Neon Green
COLOR_BTN_START = "#27ae60"  # Green
COLOR_BTN_PAUSE = "#7f8c8d"  # Grey
COLOR_BTN_STOP = "#c0392b"  # Red


class CircularProgress(tk.Canvas):
    """Canvas-based circular progress indicator."""
    
    def __init__(self, master, percent=70, size=90, **kwargs):
        super().__init__(
            master,
            width=size,
            height=size,
            bg=COLOR_CARD,
            highlightthickness=0,
            **kwargs
        )
        self.size = size
        self.percent = percent
        self.draw_progress(percent)

    def draw_progress(self, percent):
        """Draw circular progress bar."""
        self.delete("all")
        s = self.size
        center = s // 2
        
        # Background circle
        self.create_oval(8, 8, s - 8, s - 8, outline="#444444", width=4)
        
        # Progress arc
        extent = int(360 * (percent / 100.0))
        if extent > 0:
            self.create_arc(
                8, 8, s - 8, s - 8,
                start=90,
                extent=-extent,
                style="arc",
                outline=COLOR_STATUS_SANDBOX,
                width=4
            )
        
        # Percent text
        self.create_text(
            center, center,
            text=f"{int(percent)}%",
            fill="#ffffff",
            font=("Roboto", 14, "bold")
        )


class StatusBar(ctk.CTkFrame): #simulator or sandbox 
    
    def __init__(self, master, label: str, bg_color: str, **kwargs):
        super().__init__(master, fg_color=bg_color, corner_radius=8, **kwargs)
        
        self.status_label = ctk.CTkLabel(
            self,
            text=label,
            font=("Roboto", 12, "bold"),
            text_color="#ffffff"
        )
        self.status_label.pack(side="left", padx=15, pady=12, expand=True, fill="both")
    
    def set_text(self, text: str):
        """Update status text."""
        self.status_label.configure(text=text)


class TerminalPanel(ctk.CTkFrame):
    """Recent Logs / Terminal panel."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=12, **kwargs)
        
        # Header
        header = ctk.CTkLabel(
            self,
            text="Recent Logs",
            font=("Roboto", 12, "bold"),
            text_color="#ffffff"
        )
        header.pack(anchor="w", padx=12, pady=(10, 8))
        
        # Terminal textbox
        self.textbox = ctk.CTkTextbox(
            self,
            fg_color=COLOR_TERMINAL_BG,
            text_color=COLOR_TERMINAL_TEXT,
            font=MONO_FONT,
            scrollbar_button_color=COLOR_CARD,
            border_width=1,
            border_color="#444444"
        )
        self.textbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.textbox.configure(state="disabled")
    
    def add_log(self, message: str):
        """Add a log line."""
        if not self.winfo_exists():
            return
        self.textbox.configure(state="normal")
        self.textbox.insert("end", message + "\n")
        self.textbox.see("end")
        self.textbox.configure(state="disabled")


class StatsCard(ctk.CTkFrame):
    """Individual stats card."""
    
    def __init__(self, master, label: str, value: str = "0", **kwargs):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=8, **kwargs)
        
        self.label_widget = ctk.CTkLabel(
            self,
            text=label,
            font=("Roboto", 10),
            text_color="#888888"
        )
        self.label_widget.pack(padx=10, pady=(8, 4))
        
        self.value_widget = ctk.CTkLabel(
            self,
            text=value,
            font=("Roboto", 20, "bold"),
            text_color="#ffffff"
        )
        self.value_widget.pack(padx=10, pady=(0, 8))
    
    def set_value(self, value: str):
        """Update the value display."""
        self.value_widget.configure(text=value)


class ProgressCard(ctk.CTkFrame):
    """Progress indicator card."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=8, **kwargs)
        
        self.canvas = CircularProgress(self, percent=0, size=80)
        self.canvas.pack(pady=8)
    
    def set_progress(self, percent: int):
        """Update progress."""
        self.canvas.draw_progress(percent)


class DashboardPage(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_BG, **kwargs)

        # Page state (kept from previous implementation)
        self._sim_thread = None
        self._stop_event = None
        self._start_time = None
        self._files_total = 0
        self._files_done = 0
        self._active = True
        try:
            self.generator = RiskSummaryGenerator() if RiskSummaryGenerator else None
        except Exception as e:
            print(f"Warning: Could not load AI model: {e}")
            self.generator = None

        # Initialize reports storage
        self.reports_storage = reports_storage.reports_storage

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # ===== ROW 0: Title =====
        title = ctk.CTkLabel(
            self,
            text="Simulator Dashboard",
            font=TITLE_FONT,
            text_color="#ffffff"
        )
        title.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))


        # ===== ROW 1: Main Content =====
        main_area = ctk.CTkFrame(self, fg_color="transparent")
        main_area.grid(row=1, column=0, sticky="nsew", padx=16, pady=(6, 12))
        main_area.grid_rowconfigure(0, weight=2)   # logs row (bigger)
        main_area.grid_rowconfigure(1, weight=3)   # lower split row (controls + stats)
        main_area.grid_columnconfigure(0, weight=1)

        # recent logs top
        self.logs_panel = TerminalPanel(main_area)
        self.logs_panel.grid(row=0, column=0, sticky="nsew", pady=(0, 12))

        # Lower area: two columns (left: sentinel monitor, right: stats) 
        lower_area = ctk.CTkFrame(main_area, fg_color="transparent")
        lower_area.grid(row=1, column=0, sticky="nsew")
        lower_area.grid_columnconfigure(0, weight=1)  
        lower_area.grid_columnconfigure(1, weight=2)  
        lower_area.grid_rowconfigure(0, weight=1)

        # Sentinel Monitor Card (left) - will be linked to Sentinel page
        self.sentinel_monitor_card = SentinelMonitorCard(lower_area, sentinel_page_ref=None)
        self.sentinel_monitor_card.grid(row=0, column=0, sticky="nsew", padx=(5, 7))

        # Stats column (right)
        stats_col = ctk.CTkFrame(lower_area, fg_color="transparent")
        stats_col.grid(row=0, column=1, sticky="nsew")
        stats_col.grid_rowconfigure(0, weight=1)
        stats_col.grid_rowconfigure(1, weight=1)
        stats_col.grid_rowconfigure(2, weight=1)
        stats_col.grid_columnconfigure(0, weight=1)

        # Top stats row (two cards)
        self.card_files_found = StatsCard(stats_col, "Files Found", "0")
        self.card_files_found.grid(row=0, column=0, sticky="nsew", padx=6, pady=(0, 8))

        self.card_files_pct = StatsCard(stats_col, "Progress", "0%")
        self.card_files_pct.grid(row=0, column=1, sticky="nsew", padx=6, pady=(0, 8))

        self.card_files_encrypted = StatsCard(stats_col, "Files Encrypted", "0")
        self.card_files_encrypted.grid(row=1, column=0, sticky="nsew", padx=6, pady=(8, 0))

        self.card_time_elapsed = StatsCard(stats_col, "Time Elapsed", "00:00")
        self.card_time_elapsed.grid(row=1, column=1, sticky="nsew", padx=6, pady=(8, 0))

        # Risk Assessment Card
        ai_card = ctk.CTkFrame(stats_col, fg_color=COLOR_CARD, corner_radius=12)
        ai_card.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=6, pady=(8, 0))
        ai_card.grid_columnconfigure(0, weight=1)
        ai_card.grid_rowconfigure(1, weight=1)

        ai_title = ctk.CTkLabel(
            ai_card,
            text="Generate Report",
            font=("fixedsys", 12, "bold"),
            text_color="#ffffff"
        )
        ai_title.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 5))

        self.ai_textbox = ctk.CTkTextbox(
            ai_card,
            wrap="word",
            font=MONO_FONT,
            text_color="#ffffff",
            fg_color="#000000",
            height=100
        )
        self.ai_textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 5))
        self.ai_textbox.insert("0.0", "Generate A Report after running a simulation...")
        self.ai_textbox.configure(state="disabled")

        # Generate Report Button
        self.generate_report_btn = ctk.CTkButton(
            ai_card,
            text="Generate Report",
            fg_color=COLOR_BTN_START,
            hover_color="#27ae60",
            corner_radius=8,
            height=30,
            font=("Roboto", 10, "bold"),
            command=self.generate_ai_report
        )
        self.generate_report_btn.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 10))

        progress_holder = ctk.CTkFrame(lower_area, fg_color="transparent")
        progress_holder.grid(row=0, column=2, rowspan=1, sticky="nsew", padx=(8,0))
        # Note: ensure lower_area has a 3rd column for the progress holder if needed
        lower_area.grid_columnconfigure(2, weight=0, minsize=120)

        self.card_progress = ProgressCard(progress_holder)
        self.card_progress.pack(anchor="n", pady=6, padx=6)


        # ROW 2: Footer - Stop Process button centered 
        footer_row = ctk.CTkFrame(self, fg_color="transparent")
        footer_row.grid(row=2, column=0, sticky="ew", padx=16, pady=(6, 14))
        footer_row.grid_columnconfigure(0, weight=1)

        self.stop_process_btn = ctk.CTkButton(
            footer_row,
            text="Stop Process",
            fg_color=COLOR_BTN_STOP,
            hover_color="#a93226",
            corner_radius=20,
            height=40,
            width=320,
            font=("Roboto", 14, "bold"),
            command=self.stop_simulation
        )
        self.stop_process_btn.grid(row=0, column=0, pady=0)


        # Redirect stdout -> logs panel
        sys.stdout = LogRedirector(self.logs_panel)

    def start_simulation(self):
        if self._sim_thread and self._sim_thread.is_alive():
            print("Simulation already running.")
            return

        folder = self.control_panel  # preserve behavior; backend will validate
        print("Starting simulation...")
        self.simulator_status.set_text("Simulator: Running")
        self._stop_event = threading.Event()
        self._files_done = 0
        self._files_total = 0
        self._start_time = time.time()

        def runner():
            try:
                for i in range(1, 101):
                    if self._stop_event.is_set():
                        break
                    time.sleep(0.05)
                    self._files_done = i
                    self._files_total = 100
                    elapsed = time.time() - self._start_time

                    def update_ui():
                        if not self.winfo_exists():
                            return
                        self.card_files_encrypted.set_value(str(i))
                        self.card_files_found.set_value(str(self._files_total))
                        mins, secs = divmod(int(elapsed), 60)
                        self.card_time_elapsed.set_value(f"{mins:02d}:{secs:02d}")
                        # progress percent
                        pct = int(i / (self._files_total or 1) * 100)
                        self.card_files_pct.set_value(f"{pct}%")
                        self.card_progress.set_progress(pct)

                    self.after(0, update_ui)
            except Exception as e:
                print(f"[Error] {e}")
            finally:
                if self.winfo_exists():
                    self.simulator_status.set_text("Simulator: Completed")
                    # Store simulation data for AI report
                    elapsed = time.time() - self._start_time
                    shared_data.last_simulation_data = {
                        'speed': self._files_done / elapsed if elapsed > 0 else 0,
                        'files': self._files_done,
                        'time': elapsed,
                        'algorithm': 'AES-256'  # Mock, replace with actual
                    }

        self._sim_thread = threading.Thread(target=runner, daemon=True)
        self._sim_thread.start()

    def stop_simulation(self):
        if self._stop_event and not self._stop_event.is_set():
            self._stop_event.set()
            print("aborting ....")
            self.simulator_status.set_text("Simulator: Idle")
        else:
            print("No active simulation to stop.")

    def generate_ai_report(self):
        """Generate AI risk assessment report based on last simulation data."""
        if not self.generator:
            self.ai_textbox.configure(state="normal")
            self.ai_textbox.delete("0.0", tk.END)
            self.ai_textbox.insert("0.0", "Model not available. Please configure the model first.")
            self.ai_textbox.configure(state="disabled")
            return
        
        if not shared_data.last_simulation_data:
            self.ai_textbox.configure(state="normal")
            self.ai_textbox.delete("0.0", tk.END)
            self.ai_textbox.insert("0.0", "No simulation data available. Run a simulation first.")
            self.ai_textbox.configure(state="disabled")
            return
        
        print(f"Shared data: {shared_data.last_simulation_data}")
        # Create input from last simulation data
        input_data = f"Encryption speed: {shared_data.last_simulation_data.get('speed', 'N/A')} files/sec, Files encrypted: {shared_data.last_simulation_data.get('files', 'N/A')}, Time: {shared_data.last_simulation_data.get('time', 'N/A')} seconds, Algorithm: {shared_data.last_simulation_data.get('algorithm', 'N/A')}"
        print(f"Input data: '{input_data}'")
        
        # Generate in thread
        def generate():
            try:
                summary = self.generator.generate_summary(input_data)
                print(f"Summary from generator: '{summary}'")
                
                # Save the report
                self.reports_storage.add_report(
                    input_data=input_data,
                    report_text=summary,
                    simulation_data=shared_data.last_simulation_data.copy()
                )
                print("Report saved successfully")
                
                self.after(0, lambda: self._update_ai_text(summary))
            except Exception as e:
                self.after(0, lambda: self._update_ai_text(f"Error generating report: {str(e)}"))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def _update_ai_text(self, text):
        """Update the AI textbox."""
        print(f"Setting AI text: '{text}'")
        self.ai_textbox.configure(state="normal")
        self.ai_textbox.delete("0.0", tk.END)
        self.ai_textbox.insert("0.0", text)
        self.ai_textbox.configure(state="disabled")


class SentinelMonitorCard(ctk.CTkFrame):
    """Card that displays Sentinel canary monitoring data."""
    
    def __init__(self, master, sentinel_page_ref=None, **kwargs):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=12, **kwargs)
        self.sentinel_page_ref = sentinel_page_ref
        
        # Header
        header = ctk.CTkLabel(
            self,
            text="Sentinel Monitor",
            font=("Roboto", 12, "bold"),
            text_color="#ffffff"
        )
        header.pack(anchor="w", padx=12, pady=(10, 12))
        
        # Stats container
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        stats_frame.grid_columnconfigure(0, weight=1)
        
        # Active Canaries stat
        active_label = ctk.CTkLabel(
            stats_frame,
            text="Active Canaries",
            font=("Roboto", 10),
            text_color="#888888"
        )
        active_label.grid(row=0, column=0, sticky="w", pady=(0, 4))
        
        self.active_canaries_label = ctk.CTkLabel(
            stats_frame,
            text="0",
            font=("Roboto", 16, "bold"),
            text_color="#00A8A8"
        )
        self.active_canaries_label.grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        # Triggered Canaries stat
        triggered_label = ctk.CTkLabel(
            stats_frame,
            text="Triggered Canaries",
            font=("Roboto", 10),
            text_color="#888888"
        )
        triggered_label.grid(row=2, column=0, sticky="w", pady=(0, 4))
        
        self.triggered_canaries_label = ctk.CTkLabel(
            stats_frame,
            text="0",
            font=("Roboto", 16, "bold"),
            text_color="#E53935"
        )
        self.triggered_canaries_label.grid(row=3, column=0, sticky="w", pady=(0, 10))
        
        # Last Trigger Time stat
        last_trigger_label = ctk.CTkLabel(
            stats_frame,
            text="Last Trigger Event",
            font=("Roboto", 10),
            text_color="#888888"
        )
        last_trigger_label.grid(row=4, column=0, sticky="w", pady=(0, 4))
        
        self.last_trigger_time_label = ctk.CTkLabel(
            stats_frame,
            text="—",
            font=("Roboto", 11),
            text_color="#B0B0B0"
        )
        self.last_trigger_time_label.grid(row=5, column=0, sticky="w")
        
        # Start periodic update
        self.update_canary_data()
    
    def update_canary_data(self):
        """Fetch and update canary data from Sentinel page. Robustly finds sentinel if ref missing."""
        # If we don't have a reference to the sentinel page, try to locate it on the app root
        if not self.sentinel_page_ref:
            try:
                root = self.winfo_toplevel()
                if hasattr(root, "pages") and "sentinel_page" in root.pages:
                    self.sentinel_page_ref = root.pages["sentinel_page"]
            except Exception:
                # ignore lookup failures and try again next tick
                self.sentinel_page_ref = None

        if self.sentinel_page_ref and self.winfo_exists():
            try:
                raw_list = []
                # defensive: the sentinel monitor stores entries as {'data':..., 'widget':...}
                monitor = getattr(self.sentinel_page_ref, "canary_monitor", None)
                if monitor is not None:
                    raw_list = getattr(monitor, "canaries", [])  # list of {'data', 'widget'}
                else:
                    # fallback: sentinel page might expose a direct list
                    raw_list = getattr(self.sentinel_page_ref, "canaries", []) or []

                # normalize items to canary dicts
                canary_dicts = []
                for item in raw_list:
                    if isinstance(item, dict) and "data" in item:
                        canary_dicts.append(item["data"])
                    elif isinstance(item, dict):
                        canary_dicts.append(item)
                    else:
                        # unknown shape: ignore
                        pass

                # Count armed/triggered
                armed = sum(1 for c in canary_dicts if str(c.get("status", "")).lower() == "armed")
                triggered = sum(1 for c in canary_dicts if str(c.get("status", "")).lower() == "triggered")

                # Last trigger time (most recent triggered canary)
                triggered_events = [c for c in canary_dicts if str(c.get("status", "")).lower() == "triggered"]
                last_trigger = "—"
                if triggered_events:
                    # prefer 'triggered_at' then 'last_trigger' or None
                    # convert to string for display
                    last_trigger = triggered_events[0].get("triggered_at") or triggered_events[0].get("last_trigger") or "—"

                # Update UI (on UI thread)
                self.active_canaries_label.configure(text=str(armed))
                self.triggered_canaries_label.configure(text=str(triggered))
                self.last_trigger_time_label.configure(text=str(last_trigger))
            except Exception as e:
                # keep the card alive; print debug info to console
                print(f"[Dashboard] Error updating canary data: {e}")

        # Schedule next update (every 1 second)
        if self.winfo_exists():
            self.after(1000, self.update_canary_data)


class HomePage(ctk.CTkFrame):
    """Home page of the application."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_BG, **kwargs)

        # Header
        header = ctk.CTkLabel(
            self,
            text="Welcome to the AILauncher",
            font=TITLE_FONT,
            text_color="#ffffff"
        )
        header.pack(anchor="n", padx=16, pady=(24, 12))

        # Description
        description = ctk.CTkLabel(
            self,
            text="Select a task from the sidebar to get started.",
            font=("Roboto", 14),
            text_color="#cccccc"
        )
        description.pack(anchor="n", padx=16, pady=(0, 16))

        # --- Page content will be defined in subclasses ---


class SimulationPage(ctk.CTkFrame):
    """Simulation page for running and monitoring simulations."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_BG, **kwargs)

        # Header
        header = ctk.CTkLabel(
            self,
            text="Simulation Control",
            font=TITLE_FONT,
            text_color="#ffffff"
        )
        header.pack(anchor="n", padx=16, pady=(24, 12))

        # Description
        description = ctk.CTkLabel(
            self,
            text="Manage and monitor your simulations here.",
            font=("Roboto", 14),
            text_color="#cccccc"
        )
        description.pack(anchor="n", padx=16, pady=(0, 16))

        # --- Simulation control and monitoring elements ---


class RecoveryPage(ctk.CTkFrame):
    """Recovery page for managing recovery options."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_BG, **kwargs)

        # Header
        header = ctk.CTkLabel(
            self,
            text="Recovery Options",
            font=TITLE_FONT,
            text_color="#ffffff"
        )
        header.pack(anchor="n", padx=16, pady=(24, 12))

        # Description
        description = ctk.CTkLabel(
            self,
            text="Configure recovery options for your simulations.",
            font=("Roboto", 14),
            text_color="#cccccc"
        )
        description.pack(anchor="n", padx=16, pady=(0, 16))

        # --- Recovery configuration elements ---


class SentinelPage(ctk.CTkFrame):
    """Sentinel page for managing canary tokens and monitoring."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_BG, **kwargs)

        # Header
        header = ctk.CTkLabel(
            self,
            text="Sentinel Monitoring",
            font=TITLE_FONT,
            text_color="#ffffff"
        )
        header.pack(anchor="n", padx=16, pady=(24, 12))

        # Description
        description = ctk.CTkLabel(
            self,
            text="Monitor and manage Sentinel canary tokens.",
            font=("Roboto", 14),
            text_color="#cccccc"
        )
        description.pack(anchor="n", padx=16, pady=(0, 16))

        # --- Sentinel management elements ---


class App(ctk.CTk):
    """Main application class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Title and geometry
        self.title("AILauncher")
        self.geometry("1200x800")
        self.minsize(900, 600)

        # Configure grid layout (2 columns)
        self.grid_columnconfigure(0, weight=0, minsize=250)  # Sidebar
        self.grid_columnconfigure(1, weight=1)              # Main content

        # --- Sidebar: Navigation and control ---
        self.sidebar_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="ns", padx=0, pady=0)

        # Sidebar header
        sidebar_header = ctk.CTkLabel(
            self.sidebar_frame,
            text="AILauncher",
            font=TITLE_FONT,
            text_color="#ffffff"
        )
        sidebar_header.pack(padx=16, pady=(16, 8))

        # Navigation buttons (Home, Dashboard, Simulation, Recovery, Sentinel)
        nav_buttons = [
            ("Home", "home_page"),
            ("Dashboard", "dashboard_page"),
            ("Simulation", "simulation_page"),
            ("Recovery", "recovery_page"),
            ("Sentinel", "sentinel_page")
        ]

        for (text, page_id) in nav_buttons:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                fg_color=COLOR_BTN_START,
                hover_color="#229954",
                text_color="#ffffff",
                font=("Roboto", 12, "bold"),
                height=40,
                corner_radius=6,
                command=lambda pid=page_id: self.show_page(pid)
            )
            btn.pack(fill="x", padx=16, pady=(8 if text != "Home" else 0, 8))

        # --- Main content area (pages) ---
        self.main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        # Ensure the grid system is configured for the main content frame
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        # Dictionary to hold page references
        self.pages = {}

        # Create and pack the initial page (Home)
        self._create_pages()
        self.show_page("home_page")

        # Center the window on the screen
        self.center_window()

    def _create_pages(self):
        self.pages["home_page"] = HomePage(self.main_content_frame)
        self.pages["dashboard_page"] = DashboardPage(self.main_content_frame)
        self.pages["simulation_page"] = SimulationPage(self.main_content_frame)
        self.pages["recovery_page"] = RecoveryPage(self.main_content_frame)
        self.pages["sentinel_page"] = SentinelPage(self.main_content_frame)
        
        # Link Sentinel page to Dashboard monitor card
        if "dashboard_page" in self.pages and "sentinel_page" in self.pages:
            dashboard = self.pages["dashboard_page"]
            sentinel = self.pages["sentinel_page"]
            if hasattr(dashboard, 'sentinel_monitor_card'):
                dashboard.sentinel_monitor_card.sentinel_page_ref = sentinel

    def show_page(self, page_id):
        """Show the specified page by ID."""
        for page in self.pages.values():
            page.pack_forget()  # Hide all pages
        if page_id in self.pages:
            self.pages[page_id].pack(fill="both", expand=True)  # Show the requested page

    def center_window(self):
        """Center the window on the screen."""
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")





# del

    def pause_simulation(self):
        if self._sim_thread and self._sim_thread.is_alive():
            print("Simulation paused.")
            self.simulator_status.set_text("Simulator: Idle / Running / Completed")
        else:
            print("No active simulation to pause.")