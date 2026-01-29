import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os
import threading
import subprocess
import sys
import time
import AI.shared_data as shared_data
import re
from Backend.safe_zone import populate_safe_zone, SAFE_ZONE_PATH


# Constants
FONT = ("Roboto", 12)
TITLE_FONT = ("Roboto", 20, "bold")
SIDEBAR_FONT = ("Roboto", 14, "bold")
BADGE_FONT = ("Roboto", 10, "bold")
MONO_FONT = ("Consolas", 11)

# Color Palette
COLOR_BG = "#212121"
COLOR_CARD = "#2b2b2b"
COLOR_ACCENT = "#00cec9"  # Cyan/Teal
COLOR_BUTTON_START = "#07be11"  # Orange
COLOR_BUTTON_ABORT = "#d63031"  # Red/Pink
COLOR_TEXT = "#ffffff"
COLOR_TEXT_SECONDARY = "#b0b0b0"
COLOR_INACTIVE = "#666666"


class TimelineStep(ctk.CTkFrame):
    """Represents a single step in the mini timeline."""
    
    def __init__(self, master, label: str, is_active: bool = False, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.is_active = is_active
        
        # Create a horizontal layout: circle icon + text
        self.grid_columnconfigure(1, weight=1)
        
        # Circular icon (using a small frame with border)
        circle_color = COLOR_ACCENT if is_active else COLOR_INACTIVE
        self.circle = ctk.CTkFrame(
            self,
            width=40,
            height=40,
            fg_color="transparent",
            border_color=circle_color,
            border_width=2,
            corner_radius=20
        )
        self.circle.grid(row=0, column=0, padx=(0, 15), pady=10)
        
        # Icon symbol or text in center (using label)
        icon_map = {
            "Scanning": "🔍",
            "Encryption": "🔒",
            "Ransom Note": "📄",
            "Complete": "✓"
        }
        icon_text = icon_map.get(label, "•")
        
        icon_label = ctk.CTkLabel(
            self.circle,
            text=icon_text,
            font=("Roboto", 16, "bold"),
            text_color=circle_color
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Text label
        text_color = COLOR_TEXT if is_active else COLOR_TEXT_SECONDARY
        self.label = ctk.CTkLabel(
            self,
            text=label,
            font=("Roboto", 12, "bold" if is_active else "normal"),
            text_color=text_color
        )
        self.label.grid(row=0, column=1, sticky="w", pady=10)


class MiniTimeline(ctk.CTkFrame):
    """Mini timeline showing the progress steps."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=15, **kwargs)
        
        # Header
        header = ctk.CTkLabel(
            self,
            text="Mini Timeline",
            font=TITLE_FONT,
            text_color=COLOR_ACCENT
        )
        header.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Timeline container
        timeline_container = ctk.CTkFrame(self, fg_color="transparent")
        timeline_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Steps
        steps_data = [
            ("Scanning", True),
            ("Encryption", False),
            ("Ransom Note", False),
            ("Complete", False)
        ]
        
        # Draw vertical line connecting steps
        for i, (label, is_active) in enumerate(steps_data):
            step = TimelineStep(timeline_container, label, is_active=is_active)
            step.pack(fill="x", pady=(5 if i > 0 else 0, 0))
            
            # Draw a vertical line between steps (except after the last one)
            if i < len(steps_data) - 1:
                line_color = COLOR_ACCENT if is_active else COLOR_INACTIVE
                line = ctk.CTkFrame(
                    timeline_container,
                    fg_color=line_color,
                    height=20,
                    width=2
                )
                line.pack(pady=(0, 0))


class SimulationSettings(ctk.CTkFrame):
    """Main simulation settings card."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=15, **kwargs)
        self.grid_columnconfigure(1, weight=1)
        self.simulation_thread = None
        self.stop_event = threading.Event()
        
        # Header
        header = ctk.CTkLabel(
            self,
            text="Simulation Settings",
            font=TITLE_FONT,
            text_color=COLOR_ACCENT
        )
        header.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(15, 20))
        
        # Row 1: Algorithm and Encryption Speed
        ctk.CTkLabel(self, text="Algorithm", font=FONT, text_color=COLOR_TEXT).grid(
            row=1, column=0, sticky="w", padx=20, pady=(0, 5)
        )
        ctk.CTkLabel(self, text="Encryption Speed", font=FONT, text_color=COLOR_TEXT).grid(
            row=1, column=1, sticky="w", padx=20, pady=(0, 5)
        )
        
        self.algorithm_menu = ctk.CTkOptionMenu(
            self,
            values=["AES 256", "RSA", "ChaCha20"],
            fg_color="#3b3b3b",
            button_color=COLOR_ACCENT,
            text_color=COLOR_TEXT,
            font=FONT
        )
        self.algorithm_menu.set("AES 256")
        self.algorithm_menu.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        self.speed_menu = ctk.CTkOptionMenu(
            self,
            values=["Normal", "Fast", "Slow"],
            fg_color="#3b3b3b",
            button_color=COLOR_ACCENT,
            text_color=COLOR_TEXT,
            font=FONT
        )
        self.speed_menu.set("Normal")
        self.speed_menu.grid(row=2, column=1, sticky="ew", padx=20, pady=(0, 15))
        
        # Row 2: Folder Picker
        ctk.CTkLabel(self, text="Folder Picker", font=FONT, text_color=COLOR_TEXT).grid(
            row=3, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 5)
        )
        
        folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        folder_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 15))
        folder_frame.grid_columnconfigure(0, weight=1)
        
        self.folder_entry = ctk.CTkEntry(
            folder_frame,
            placeholder_text="Select a folder...",
            fg_color="#3b3b3b",
            border_color=COLOR_ACCENT,
            text_color=COLOR_TEXT,
            font=FONT
        )
        self.folder_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            folder_frame,
            text="Browse",
            fg_color=COLOR_ACCENT,
            text_color=COLOR_BG,
            hover_color="#00b8a9",
            font=FONT,
            width=80,
            command=self.browse_folder
        )
        browse_btn.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        auto_populate_btn = ctk.CTkButton(
            folder_frame,
            text="Auto Populate",
            fg_color=COLOR_ACCENT,
            text_color=COLOR_BG,
            hover_color="#00b8a9",
            font=FONT,
            width=120,
            command=self.auto_populate_folder
        )
        auto_populate_btn.grid(row=0, column=2, sticky="ew")
        
        # Row 3: Checkboxes
        self.all_files_check = ctk.CTkCheckBox(
            self,
            text="All files (incl. dll, csv)",
            font=FONT,
            text_color=COLOR_TEXT,
            fg_color=COLOR_ACCENT,
            hover_color="#00b8a9",
            checkmark_color=COLOR_BG
        )
        self.all_files_check.grid(row=5, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 15))
        
        self.ransom_note_check = ctk.CTkCheckBox(
            self,
            text="Drop Ransom Note",
            font=FONT,
            text_color=COLOR_TEXT,
            fg_color=COLOR_ACCENT,
            hover_color="#00b8a9",
            checkmark_color=COLOR_BG
        )
        self.ransom_note_check.grid(row=6, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 15))
        
        # Row 4: Custom Ransom Note Text Area
        ctk.CTkLabel(self, text="Custom Ransom Note", font=FONT, text_color=COLOR_TEXT).grid(
            row=7, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 5)
        )
        
        self.ransom_note_text = ctk.CTkTextbox(
            self,
            fg_color="#3b3b3b",
            text_color=COLOR_TEXT,
            border_color=COLOR_ACCENT,
            border_width=1,
            font=FONT,
            height=100
        )
        self.ransom_note_text.grid(row=8, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 25))
        self.ransom_note_text.insert("1.0", "Your files have been encrypted.\nPay ransom to recover.")
        
        # Action Buttons
        start_btn = ctk.CTkButton(
            self,
            text="Start Simulation",
            fg_color=COLOR_BUTTON_START,
            hover_color="#078b1b",
            text_color=COLOR_TEXT,
            font=("Roboto", 14, "bold"),
            height=45,
            corner_radius=10,
            command=self.start_simulation_clicked
        )
        start_btn.grid(row=9, column=0, columnspan=1, sticky="ew", padx=20, pady=(0, 10))
        
        abort_btn = ctk.CTkButton(
            self,
            text="Abort Simulation",
            fg_color=COLOR_BUTTON_ABORT,
            hover_color="#b71c1c",
            text_color=COLOR_TEXT,
            font=("Roboto", 12, "bold"),
            height=35,
            corner_radius=8,
            command=self.abort_simulation_clicked
        )
        abort_btn.grid(row=10, column=0, columnspan=1, sticky="", padx=20, pady=(0, 20))
    
    def browse_folder(self):
        """Handle folder selection."""
        folder_path = tk.filedialog.askdirectory(
            title="Select Folder for Simulation",
            initialdir=os.path.expanduser("~")
        )
        if folder_path:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_path)

    def auto_populate_folder(self):
        """Populate the safe zone and set the folder entry."""
        try:
            # Run the population in a separate thread to avoid blocking the UI
            threading.Thread(target=populate_safe_zone, daemon=True).start()
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, str(SAFE_ZONE_PATH.resolve()))
        except Exception as e:
            print(f"Failed to populate safe zone: {e}")
    
    def start_simulation_clicked(self):
        """Callback for Start button. Bind to backend method."""
        settings = self.master.master.get_settings()
        self.stop_event.clear()
        self.simulation_thread = threading.Thread(
            target=self.run_simulation,
            args=(settings, self.stop_event)
        )
        self.simulation_thread.start()
        
        # Navigate to dashboard page
        # Find the root app and call change_page
        root = self.winfo_toplevel()
        if hasattr(root, 'change_page'):
            root.change_page('dashboard_page')

    def abort_simulation_clicked(self):
        """Callback for Abort button. Bind to backend method."""
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.stop_event.set()
            print("[UI] Abort signal sent.")

    def run_simulation(self, settings, stop_event):
        """Run the backend encryption script (try in-process simulate_encrypt_folder first)."""
        folder = settings.get("folder")
        alg_raw = settings.get("algorithm", "AES")
        all_files = settings.get("all_files", False)
        drop_ransom_note = settings.get("drop_ransom_note", False)
        ransom_note_content = settings.get("ransom_note", "")

        if not folder:
            print("[Error] No folder selected for simulation.")
            return

        # Normalize algorithm
        alg_l = (alg_raw or "").lower()
        if "aes" in alg_l:
            algorithm = "AES"
        elif "rsa" in alg_l:
            algorithm = "RSA"
        elif "chacha" in alg_l:
            algorithm = "ChaCha20"
        else:
            algorithm = alg_raw

        # If all_files is True, allowed_ext will be None (scan everything)
        allowed_ext = None if all_files else None  # keep None here so encrypt.py default is used                                           # but when calling in-process we can pass None to mean all
        # Try to run in-process (preferred) so we can receive structured progress callbacks
        
        try:
            # Import the simulate function directly
            from Backend.encrypt import simulate_encrypt_folder
            print("[UI] Running simulation in-process (direct call to simulate_encrypt_folder).")

            last_data = {'files': 0, 'time': 0}

            def progress_callback(done, total, elapsed):
                nonlocal last_data
                last_data['files'] = total
                last_data['time'] = elapsed
                # Update Dashboard cards safely on the UI thread
                root = self.winfo_toplevel()
                try:
                    dashboard = root.pages.get("dashboard_page") if hasattr(root, "pages") else None
                except Exception:
                    dashboard = None

                if dashboard:
                    def ui_update():
                        # Files Encrypted
                        dashboard.card_files_encrypted.set_value(str(done))
                        # Files Found (total)
                        dashboard.card_files_found.set_value(str(total))
                        # Time elapsed
                        mins, secs = divmod(int(elapsed), 60)
                        dashboard.card_time_elapsed.set_value(f"{mins:02d}:{secs:02d}")
                        # Percent/progress
                        pct = int(done / (total or 1) * 100)
                        dashboard.card_files_pct.set_value(f"{pct}%")
                        dashboard.card_progress.set_progress(pct)
                    dashboard.after(0, ui_update)

            # Call the simulation (this will print to stdout as well)
            simulate_encrypt_folder(folder, test_mode=True, algorithm=algorithm, stop_event=stop_event, progress_callback=progress_callback, allowed_ext=(None if all_files else None), drop_ransom_note=drop_ransom_note, ransom_note_content=ransom_note_content)
            print("[UI] simulate_encrypt_folder returned (in-process).")
            # Store simulation data
            speed = last_data['files'] / last_data['time'] if last_data['time'] > 0 else 0
            shared_data.last_simulation_data = {'speed': speed, 'files': last_data['files'], 'time': last_data['time'], 'algorithm': algorithm}
            return
        except Exception as e:
            print(f"[UI] In-process simulate failed (falling back to subprocess): {e}")

        # Fallback: run as subprocess (unbuffered) and stream output
        backend_script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "Backend",
            "encrypt.py"
        )

        try:
            # Use unbuffered Python so printed lines are available immediately
            command = [sys.executable, "-u", backend_script_path, folder, f"--algorithm={algorithm}"]
            if all_files:
                command.append("--all-files")

            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"

            output_lines = []

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            print(f"Starting simulation with command: {' '.join(command)}")

            def _reader(pipe, prefix, output_lines):
                try:
                    for line in iter(pipe.readline, ""):
                        if not line:
                            break
                        print(f"{prefix}{line.rstrip()}")
                        output_lines.append(line)
                except Exception as e:
                    print(f"[Reader Error] {e}")
                finally:
                    try:
                        pipe.close()
                    except Exception:
                        pass

            t_out = threading.Thread(target=_reader, args=(process.stdout, "[Backend STDOUT]: ", output_lines), daemon=True)
            t_err = threading.Thread(target=_reader, args=(process.stderr, "[Backend STDERR]: ", output_lines), daemon=True)
            t_out.start()
            t_err.start()

            while process.poll() is None:
                if stop_event is not None and stop_event.is_set():
                    try:
                        process.terminate()
                        print("Simulation process terminated by user.")
                    except Exception:
                        pass
                    break
                time.sleep(0.1)

            try:
                process.wait(timeout=5)
            except Exception:
                pass

            t_out.join(timeout=1)
            t_err.join(timeout=1)
            print("Simulation subprocess finished.")

            # Parse simulation data
            files = sum(1 for line in output_lines if "->" in line)
            time_taken = 0
            for line in reversed(output_lines):
                if "Total time taken:" in line:
                    match = re.search(r"Total time taken: ([\d.]+) seconds", line)
                    if match:
                        time_taken = float(match.group(1))
                    break
            speed = files / time_taken if time_taken > 0 else 0
            shared_data.last_simulation_data = {'speed': speed, 'files': files, 'time': time_taken, 'algorithm': algorithm}
        except Exception as e:
            print(f"Failed to run simulation (subprocess fallback): {e}")
    
    def get_ransom_note(self):
        """Retrieve custom ransom note text."""
        return self.ransom_note_text.get("1.0", tk.END).strip()
        
class SimulationPage(ctk.CTkFrame):
    """Main simulation page with settings and timeline."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_BG, **kwargs)
        
        # Configure grid for responsive layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)
        
        # Center wrapper
        center_wrapper = ctk.CTkFrame(self, fg_color="transparent")
        center_wrapper.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        center_wrapper.grid_columnconfigure(0, weight=1)
        center_wrapper.grid_rowconfigure(0, weight=1)
        
        # Left: Settings Card
        self.settings_card = SimulationSettings(center_wrapper)
        self.settings_card.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        # Right: Timeline Card
        self.timeline_card = MiniTimeline(center_wrapper, width=220)
        self.timeline_card.grid(row=0, column=1, sticky="nsew")
    
    def set_start_callback(self, callback):
        """Attach backend start callback."""
        self.settings_card.start_simulation_clicked = callback
    
    def set_abort_callback(self, callback):
        """Attach backend abort callback."""
        self.settings_card.abort_simulation_clicked = callback
    
    def get_settings(self):
        """Retrieve current settings from UI."""
        return {
            "algorithm": self.settings_card.algorithm_menu.get(),
            "speed": self.settings_card.speed_menu.get(),
            "folder": self.settings_card.folder_entry.get(),
            "all_files": self.settings_card.all_files_check.get(),
            "drop_ransom_note": self.settings_card.ransom_note_check.get(),
            "ransom_note": self.settings_card.get_ransom_note()
        }



