import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os
import threading
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define common fonts and colors to match existing pages
FONT = ("Roboto", 12)
TITLE_FONT = ("Roboto", 20, "bold")
SUBTITLE_FONT = ("Roboto", 14, "bold")
LABEL_FONT = ("Roboto", 11)
SMALL_FONT = ("Roboto", 9)

# Color Palette (matching Dashboard/Simulation dark theme)
COLOR_BG = "#111111"
COLOR_CARD = "#1A1A1A"
COLOR_ACCENT_TEAL = "#00A8A8"
COLOR_BUTTON_ORANGE = "#F57C00"
COLOR_WARNING_RED = "#E53935"
COLOR_TEXT = "#FFFFFF"
COLOR_TEXT_SECONDARY = "#B0B0B0"
COLOR_DISABLED = "#666666"
COLOR_BADGE_ARMED = "#00A8A8"
COLOR_BADGE_TRIGGERED = "#E53935"


class CanaryFileSystemEventHandler(FileSystemEventHandler):
    """Watches for file system events and triggers on encrypted canaries."""
    
    def __init__(self, sentinel_page):
        """
        Args:
            sentinel_page: Reference to SentinelPage to access live canary list and callback.
        """
        super().__init__()
        self.sentinel_page = sentinel_page
    
    def on_created(self, event):
        """Called when a file is created."""
        if event.is_directory:
            return
        self._check_trigger(event.src_path)
    
    def on_modified(self, event):
        """Called when a file is modified."""
        if event.is_directory:
            return
        self._check_trigger(event.src_path)
    
    def _check_trigger(self, file_path):
        """Check if the file event matches any deployed canary."""
        try:
            file_path = Path(file_path).resolve()
            file_name = file_path.name
            
            print(f"[Sentinel] File event detected: {file_name} at {file_path}")
            
            # Access the live canary list from the monitoring panel
            canaries_list = self.sentinel_page.canary_monitor.canaries
            
            # Check each deployed canary
            for canary_entry in canaries_list:
                canary = canary_entry['data']
                canary_name = canary.get('name', '')
                canary_path = canary.get('path', '')
                
                if not canary_name or not canary_path:
                    continue
                
                # If canary is already triggered, skip
                if canary.get('status') == 'triggered':
                    continue
                
                # The simulator transforms "CONFIDENTIAL_REPORT.txt" -> "CONFIDENTIAL_REPORT.txt.enc"
                expected_enc_name = f"{canary_name}.encrypted"
                
                print(f"[Sentinel] Checking: file={file_name} vs expected={expected_enc_name}")
                
                # Check if created file matches the encrypted canary name
                if file_name == expected_enc_name:
                    # Verify it's in or near the canary's deployment location
                    if self._is_in_encrypted_folder(file_path, canary_path):
                        print(f"[Sentinel] MATCH FOUND: Canary '{canary_name}' triggered!")
                        # Mark canary as triggered with timestamp
                        canary['status'] = 'triggered'
                        canary['triggered_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        # Call the callback on the main thread
                        self.sentinel_page.after(0, lambda: self.sentinel_page.on_canary_triggered(canary))
                        return
        except Exception as e:
            print(f"[Sentinel] Error in _check_trigger: {e}")
    
    def _is_in_encrypted_folder(self, file_path, canary_base_path):
        """Check if file_path is within an 'encrypted' subfolder of canary_base_path."""
        try:
            file_path = Path(file_path).resolve()
            base_path = Path(canary_base_path).resolve()
            
            # Check if file is anywhere under base_path (including encrypted/ subdirectory)
            encrypted_dir = base_path / "encrypted"
            
            print(f"[Sentinel] Path check: file_parent={file_path.parent}, encrypted_dir={encrypted_dir}, base={base_path}")
            
            # Check multiple conditions:
            # 1. File is directly in encrypted/
            # 2. File is in a subfolder of encrypted/
            # 3. File path starts with encrypted_dir path
            is_match = (
                file_path.parent == encrypted_dir or
                encrypted_dir in file_path.parents or
                str(file_path).startswith(str(encrypted_dir))
            )
            
            print(f"[Sentinel] Path match result: {is_match}")
            return is_match
        except Exception as e:
            print(f"[Sentinel] Error in _is_in_encrypted_folder: {e}")
            return False


class CanaryFileRow(ctk.CTkFrame):
    """Individual canary file entry with status and remove button."""
    
    def __init__(self, master, canary_data, remove_callback, **kwargs):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=8, **kwargs)
        self.canary_data = canary_data
        self.remove_callback = remove_callback
        
        self.grid_columnconfigure(1, weight=1)
        
        # Left side: canary info
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="w", padx=12, pady=10)
        info_frame.grid_columnconfigure(0, weight=1)
        
        # File name (bold)
        file_name_label = ctk.CTkLabel(
            info_frame,
            text=canary_data.get('name', 'Unknown'),
            font=("Roboto", 11, "bold"),
            text_color=COLOR_TEXT
        )
        file_name_label.grid(row=0, column=0, sticky="w")
        
        # File path (smaller, secondary text)
        file_path_label = ctk.CTkLabel(
            info_frame,
            text=canary_data.get('path', 'N/A'),
            font=SMALL_FONT,
            text_color=COLOR_TEXT_SECONDARY
        )
        file_path_label.grid(row=1, column=0, sticky="w", pady=(2, 0))
        
        # Right side: status badge + remove button
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=0, column=1, sticky="e", padx=12, pady=10)
        
        # Status badge
        status = canary_data.get('status', 'armed').lower()
        badge_color = COLOR_BADGE_TRIGGERED if status == 'triggered' else COLOR_BADGE_ARMED
        badge_text = status.upper()
        
        status_badge = ctk.CTkLabel(
            action_frame,
            text=badge_text,
            font=("Roboto", 9, "bold"),
            text_color="#000000",
            fg_color=badge_color,
            corner_radius=4,
            padx=8,
            pady=4
        )
        status_badge.pack(side="left", padx=(0, 10))
        
        # Remove button
        remove_btn = ctk.CTkButton(
            action_frame,
            text="Remove",
            fg_color=COLOR_WARNING_RED,
            hover_color="#c23830",
            text_color=COLOR_TEXT,
            font=SMALL_FONT,
            height=24,
            width=70,
            command=lambda: remove_callback(canary_data)
        )
        remove_btn.pack(side="left")


class CanaryGeneratorPanel(ctk.CTkFrame):
    """Left column: Canary file creation and deployment."""
    
    def __init__(self, master, deploy_callback, **kwargs):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=12, **kwargs)
        self.deploy_callback = deploy_callback
        self.selected_folder = None
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Canary File Generator",
            font=SUBTITLE_FONT,
            text_color=COLOR_TEXT
        )
        title_label.pack(anchor="w", padx=16, pady=(16, 12))
        
        # File type selection
        ctk.CTkLabel(
            self,
            text="Select Canary File Type",
            font=LABEL_FONT,
            text_color=COLOR_TEXT
        ).pack(anchor="w", padx=16, pady=(0, 6))
        
        self.file_type_var = ctk.StringVar(value=".txt")
        file_type_dropdown = ctk.CTkOptionMenu(
            self,
            values=[".txt", ".exe", ".pdf", ".jpg", ".docx"],
            variable=self.file_type_var,
            fg_color="#2D2D2D",
            button_color=COLOR_ACCENT_TEAL,
            button_hover_color="#008F8F",
            text_color=COLOR_TEXT,
            font=LABEL_FONT
        )
        file_type_dropdown.pack(fill="x", padx=16, pady=(0, 12))
        
        # File name input
        ctk.CTkLabel(
            self,
            text="Canary File Name",
            font=LABEL_FONT,
            text_color=COLOR_TEXT
        ).pack(anchor="w", padx=16, pady=(0, 6))
        
        self.file_name_entry = ctk.CTkEntry(
            self,
            placeholder_text="e.g., CONFIDENTIAL_REPORT",
            fg_color="#2D2D2D",
            border_color=COLOR_ACCENT_TEAL,
            text_color=COLOR_TEXT,
            placeholder_text_color=COLOR_DISABLED,
            font=LABEL_FONT,
            height=32
        )
        self.file_name_entry.pack(fill="x", padx=16, pady=(0, 12))
        
        # Folder selection
        ctk.CTkLabel(
            self,
            text="Deployment Location",
            font=LABEL_FONT,
            text_color=COLOR_TEXT
        ).pack(anchor="w", padx=16, pady=(0, 6))
        
        folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        folder_frame.pack(fill="x", padx=16, pady=(0, 12))
        folder_frame.grid_columnconfigure(0, weight=1)
        
        self.folder_display_entry = ctk.CTkEntry(
            folder_frame,
            placeholder_text="No folder selected",
            fg_color="#2D2D2D",
            border_color=COLOR_DISABLED,
            text_color=COLOR_TEXT_SECONDARY,
            placeholder_text_color=COLOR_DISABLED,
            font=LABEL_FONT,
            height=32
        )
        self.folder_display_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.folder_display_entry.configure(state="disabled")
        
        browse_btn = ctk.CTkButton(
            folder_frame,
            text="Browse",
            fg_color=COLOR_ACCENT_TEAL,
            hover_color="#008F8F",
            text_color="#000000",
            font=("Roboto", 10, "bold"),
            height=32,
            width=80,
            command=self.browse_folder
        )
        browse_btn.grid(row=0, column=1)
        
        # Toggle: Enable trigger logging
        toggle_frame = ctk.CTkFrame(self, fg_color="transparent")
        toggle_frame.pack(fill="x", padx=16, pady=(12, 12))
        toggle_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            toggle_frame,
            text="Enable Canary Trigger Logging",
            font=LABEL_FONT,
            text_color=COLOR_TEXT
        ).grid(row=0, column=0, sticky="w")
        
        self.logging_toggle = ctk.CTkSwitch(
            toggle_frame,
            text="",
            onvalue=True,
            offvalue=False,
            fg_color=COLOR_ACCENT_TEAL,
            progress_color=COLOR_ACCENT_TEAL
        )
        self.logging_toggle.grid(row=0, column=1, sticky="e")
        self.logging_toggle.select()  # Default ON
        
        # Deploy button
        deploy_btn = ctk.CTkButton(
            self,
            text="Deploy Canary File",
            fg_color=COLOR_BUTTON_ORANGE,
            hover_color="#E07000",
            text_color="#FFFFFF",
            font=("Roboto", 12, "bold"),
            height=40,
            corner_radius=8,
            command=self.deploy_canary_file
        )
        deploy_btn.pack(fill="x", padx=16, pady=(12, 16))
        
        # Description text
        desc_label = ctk.CTkLabel(
            self,
            text="A canary file detects unauthorized access or encryption attempts during simulation.",
            font=SMALL_FONT,
            text_color=COLOR_TEXT_SECONDARY,
            wraplength=250,
            justify="left"
        )
        desc_label.pack(anchor="w", padx=16, pady=(0, 16))
    
    def browse_folder(self):
        """Open folder selection dialog."""
        folder = filedialog.askdirectory(title="Select Deployment Location")
        if folder:
            self.selected_folder = folder
            self.folder_display_entry.configure(state="normal")
            self.folder_display_entry.delete(0, tk.END)
            # Show truncated path if too long
            display_path = folder if len(folder) <= 40 else "..." + folder[-37:]
            self.folder_display_entry.insert(0, display_path)
            self.folder_display_entry.configure(state="disabled")
    
    def deploy_canary_file(self):
        """Deploy a canary file (create actual file on disk)."""
        file_name = self.file_name_entry.get()
        file_type = self.file_type_var.get()
        
        if not file_name:
            print("[Warning] Please enter a canary file name.")
            return
        
        if not self.selected_folder:
            print("[Warning] Please select a deployment location.")
            return
        
        logging_enabled = self.logging_toggle.get()
        
        # Create the actual canary file on disk
        full_file_name = f"{file_name}{file_type}"
        canary_file_path = Path(self.selected_folder) / full_file_name
        
        try:
            # Write canary file with identifying content
            canary_content = f"CANARY FILE\nName: {full_file_name}\nDeployed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nDo not modify or delete."
            canary_file_path.write_text(canary_content, encoding='utf-8')
            print(f"[Sentinel] Canary file created: {canary_file_path}")
        except Exception as e:
            print(f"[Error] Failed to create canary file: {e}")
            return
        
        canary_info = {
            'name': full_file_name,
            'path': self.selected_folder,
            'type': file_type,
            'logging': logging_enabled,
            'status': 'armed',
            'triggered_at': None,
            'file_path': str(canary_file_path)  # Store full path for later
        }
        
        print(f"[Sentinel] Deploying canary: {canary_info['name']} to {self.selected_folder}")
        self.deploy_callback(canary_info)
        
        # Clear inputs
        self.file_name_entry.delete(0, tk.END)
        self.selected_folder = None
        self.folder_display_entry.configure(state="normal")
        self.folder_display_entry.delete(0, tk.END)
        self.folder_display_entry.configure(state="disabled")


class CanaryMonitoringPanel(ctk.CTkFrame):
    """Right column: Active canary files monitoring."""
    
    def __init__(self, master, remove_callback, **kwargs):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=12, **kwargs)
        self.remove_callback = remove_callback
        self.canaries = []
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Active Canary Files",
            font=SUBTITLE_FONT,
            text_color=COLOR_TEXT
        )
        title_label.pack(anchor="w", padx=16, pady=(16, 12))
        
        # Scrollable canary list
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Placeholder label (shown when no canaries)
        self.placeholder_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="No canary files deployed.",
            font=LABEL_FONT,
            text_color=COLOR_TEXT_SECONDARY
        )
        self.placeholder_label.pack(pady=40)
        
        # Status Summary Card
        summary_card = ctk.CTkFrame(self, fg_color="#2D2D2D", corner_radius=8)
        summary_card.pack(fill="x", padx=16, pady=(0, 16))
        summary_card.grid_columnconfigure(0, weight=1)
        
        summary_title = ctk.CTkLabel(
            summary_card,
            text="System Detection Summary",
            font=("Roboto", 11, "bold"),
            text_color=COLOR_TEXT
        )
        summary_title.pack(anchor="w", padx=12, pady=(10, 8))
        
        # Stats grid
        stats_frame = ctk.CTkFrame(summary_card, fg_color="transparent")
        stats_frame.pack(fill="x", padx=12, pady=(0, 10))
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Armed count
        ctk.CTkLabel(
            stats_frame,
            text="Armed:",
            font=LABEL_FONT,
            text_color=COLOR_TEXT_SECONDARY
        ).grid(row=0, column=0, sticky="w")
        
        self.armed_count_label = ctk.CTkLabel(
            stats_frame,
            text="0",
            font=("Roboto", 12, "bold"),
            text_color=COLOR_ACCENT_TEAL
        )
        self.armed_count_label.grid(row=0, column=1, sticky="w", padx=(4, 0))
        
        # Triggered count
        ctk.CTkLabel(
            stats_frame,
            text="Triggered:",
            font=LABEL_FONT,
            text_color=COLOR_TEXT_SECONDARY
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))
        
        self.triggered_count_label = ctk.CTkLabel(
            stats_frame,
            text="0",
            font=("Roboto", 12, "bold"),
            text_color=COLOR_WARNING_RED
        )
        self.triggered_count_label.grid(row=1, column=1, sticky="w", padx=(4, 0), pady=(4, 0))
        
        # Last trigger event
        ctk.CTkLabel(
            stats_frame,
            text="Last Trigger:",
            font=LABEL_FONT,
            text_color=COLOR_TEXT_SECONDARY
        ).grid(row=2, column=0, sticky="w", pady=(4, 0))
        
        self.last_trigger_label = ctk.CTkLabel(
            stats_frame,
            text="—",
            font=LABEL_FONT,
            text_color=COLOR_ACCENT_TEAL
        )
        self.last_trigger_label.grid(row=2, column=1, sticky="w", padx=(4, 0), pady=(4, 0))
    
    def add_canary(self, canary_data):
        """Add a canary file to the monitoring list."""
        if self.placeholder_label.winfo_exists():
            self.placeholder_label.pack_forget()
        
        canary_row = CanaryFileRow(
            self.scrollable_frame,
            canary_data,
            self.remove_callback,
            height=60
        )
        canary_row.pack(fill="x", pady=6)
        
        self.canaries.append({'data': canary_data, 'widget': canary_row})
        self.update_summary()
    
    def update_canary_status(self, canary_data):
        """Update an existing canary's status (e.g., to Triggered)."""
        for canary_entry in self.canaries:
            if canary_entry['data'] == canary_data:
                # Rebuild the row to reflect status change
                canary_entry['widget'].destroy()
                canary_row = CanaryFileRow(
                    self.scrollable_frame,
                    canary_data,
                    self.remove_callback,
                    height=60
                )
                canary_row.pack(fill="x", pady=6)
                canary_entry['widget'] = canary_row
                self.update_summary()
                break
    
    def remove_canary(self, canary_data):
        """Remove a canary from the list."""
        self.canaries = [c for c in self.canaries if c['data'] != canary_data]
        
        # Refresh the display
        for widget in self.scrollable_frame.winfo_children():
            widget.pack_forget()
        
        if not self.canaries:
            self.placeholder_label.pack(pady=40)
        else:
            for canary_entry in self.canaries:
                canary_entry['widget'].pack(fill="x", pady=6)
        
        self.update_summary()
    
    def update_summary(self):
        """Update the summary statistics."""
        armed = sum(1 for c in self.canaries if c['data'].get('status') == 'armed')
        triggered = sum(1 for c in self.canaries if c['data'].get('status') == 'triggered')
        
        self.armed_count_label.configure(text=str(armed))
        self.triggered_count_label.configure(text=str(triggered))
        
        # Find most recent triggered event
        triggered_events = [c for c in self.canaries if c['data'].get('status') == 'triggered']
        if triggered_events:
            last_time = triggered_events[0]['data'].get('triggered_at', '—')
            self.last_trigger_label.configure(text=str(last_time))
        else:
            self.last_trigger_label.configure(text="—")


class SentinelStatusBanner(ctk.CTkFrame):
    """Footer status banner."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_ACCENT_TEAL, corner_radius=0, height=40, **kwargs)
        self.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self,
            text="Sentinel system idle — waiting for simulation events.",
            font=LABEL_FONT,
            text_color="#000000"
        )
        self.status_label.pack(pady=10)
    
    def set_status(self, status_text):
        """Update the banner status text."""
        self.status_label.configure(text=status_text)


class SentinelPage(ctk.CTkFrame):
    """Main Sentinel page: Mitigation & Detection Tools with watchdog monitoring."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_BG, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Watchdog observer for file system events
        self.observer = None
        self.event_handler = None
        self.monitoring_paths = set()
        
        # Page title (centered at top)
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 16))
        title_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Sentinel — Mitigation & Detection Tools",
            font=TITLE_FONT,
            text_color=COLOR_TEXT
        )
        title_label.grid(row=0, column=0)
        
        # Main content frame (two-column layout)
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 16))
        content_frame.grid_columnconfigure((0, 1), weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Left column: Canary Generator
        self.canary_generator = CanaryGeneratorPanel(
            content_frame,
            deploy_callback=self.deploy_canary_file
        )
        self.canary_generator.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Right column: Canary Monitoring
        self.canary_monitor = CanaryMonitoringPanel(
            content_frame,
            remove_callback=self.remove_canary_item
        )
        self.canary_monitor.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Footer: Status banner
        self.status_banner = SentinelStatusBanner(self)
        self.status_banner.grid(row=2, column=0, sticky="ew")
        
        # Start watching for canary triggers
        self.start_watchdog()
    
    def start_watchdog(self):
        """Start the watchdog observer for file system monitoring."""
        if self.observer is None:
            self.observer = Observer()
            self.observer.daemon = True  # Daemon thread so it doesn't block app shutdown
            self.observer.start()
            print("[Sentinel] Watchdog observer started.")
    
    def add_watch_path(self, path):
        """Add a path to be monitored by watchdog."""
        path = Path(path).resolve()
        if path not in self.monitoring_paths:
            if self.observer and not self.observer.is_alive():
                self.observer = Observer()
                self.observer.daemon = True
                self.observer.start()
            
            # Watch the parent directory recursively
            if self.observer:
                self.observer.schedule(
                    self.event_handler,
                    str(path),
                    recursive=True
                )
                self.monitoring_paths.add(path)
                print(f"[Sentinel] Now monitoring: {path}")
    
    def deploy_canary_file(self, canary_info):
        """Handle canary file deployment and start monitoring."""
        print(f"[Sentinel] Deploying canary: {canary_info['name']}")
        self.canary_monitor.add_canary(canary_info)
        
        # Create event handler if not exists (reference to self for live access)
        if self.event_handler is None:
            self.event_handler = CanaryFileSystemEventHandler(self)
        
        # Add the deployment path to monitoring
        self.add_watch_path(canary_info['path'])
        
        self.status_banner.set_status(f"Sentinel: Canary '{canary_info['name']}' deployed and armed. Monitoring active.")
    
    def on_canary_triggered(self, canary_data):
        """Callback when a canary file is triggered (detected as encrypted)."""
        print(f"[Sentinel] 🚨 CANARY TRIGGERED: {canary_data['name']} at {canary_data.get('triggered_at', 'unknown')}")
        
        # Update the UI to show triggered status
        self.canary_monitor.update_canary_status(canary_data)
        
        # Update status banner
        self.status_banner.set_status(
            f"🚨 ALERT: Canary '{canary_data['name']}' was accessed/encrypted at {canary_data.get('triggered_at', 'now')}!"
        )
    
    def remove_canary_item(self, canary_data):
        """Handle removal of a canary file."""
        canary_path = canary_data.get('file_path', '')
        
        # Try to delete the actual file
        if canary_path:
            try:
                Path(canary_path).unlink()
                print(f"[Sentinel] Canary file deleted: {canary_path}")
            except Exception as e:
                print(f"[Warning] Could not delete canary file: {e}")
        
        print(f"[Sentinel] Removing canary: {canary_data['name']}")
        self.canary_monitor.remove_canary(canary_data)
        self.status_banner.set_status("Sentinel: Canary file removed from monitoring.")
    
    def refresh_canary_status(self):
        """Placeholder for manual refresh of canary status."""
        print("[Sentinel] Refreshing canary status...")
        # Watchdog handles this automatically; this can be used for manual checks
        pass
    
    def stop_monitoring(self):
        """Stop the watchdog observer (call on app shutdown)."""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            print("[Sentinel] Watchdog observer stopped.")