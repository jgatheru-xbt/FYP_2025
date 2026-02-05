import customtkinter as ctk
import tkinter as tk
import os
import sys

# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import page classes
from frontend.home import HomePage
from frontend.dashboard import DashboardPage
from frontend.recovery import RecoveryPage
from frontend.simulations import SimulationPage
from frontend.sentinel import SentinelPage
from frontend.reports_page import ReportsPage
from Backend.safe_zone import SAFE_ZONE_PATH

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Define common fonts
FONT = ("Roboto", 12)
TITLE_FONT = ("Roboto", 20, "bold")
SIDEBAR_FONT = ("Roboto", 14, "bold")
BADGE_FONT = ("Roboto", 10, "bold")
MONO_FONT = ("Consolas", 11)
DOT_SIZE = 10


class NavigationSidebar(ctk.CTkFrame):
    def __init__(self, master, command, **kwargs):
        super().__init__(master, fg_color="#23272e", **kwargs)
        self.command = command
        self.configure(corner_radius=0)

        self.logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, pady=(20, 30), padx=20, sticky="ew")
        self.logo_frame.grid_columnconfigure(0, weight=1)

        self.logo = ctk.CTkLabel(
            self.logo_frame, text="", fg_color="#1500FA", width=30, height=30
        )
        self.logo.pack(side="left", padx=(0, 10))

        self.title_label = ctk.CTkLabel(
            self.logo_frame,
            text="Ransomware Simulator",
            font=("Roboto", 16, "bold"),
            text_color="white",
        )
        self.title_label.pack(side="left")

        self.nav_buttons = {}
        nav_items = [
            ("Home", "home_page"),
            ("Dashboard", "dashboard_page"),
            ("Simulation", "simulation_page"),
            ("Recover", "recovery_page"),
            ("Sentinel", "sentinel_page"),
            ("Reports", "reports_page"),
        ]

        for i, item_info in enumerate(nav_items):
            text = item_info[0]
            frame_name = item_info[1]
            has_badge = item_info[2] if len(item_info) > 2 else False

            button_frame = ctk.CTkFrame(self, fg_color="transparent")
            button_frame.grid(
                row=i + 1, column=0, sticky="ew", padx=10, pady=(10 if i == 0 else 0, 0)
            )
            button_frame.grid_columnconfigure(0, weight=1)

            button = ctk.CTkButton(
                button_frame,
                text=text,
                fg_color="transparent",
                text_color="white",
                anchor="w",
                hover_color="#1E2732",
                font=SIDEBAR_FONT,
                command=lambda name=frame_name: self.command(name),
            )
            button.grid(row=0, column=0, sticky="ew")
            self.nav_buttons[frame_name] = button

            if has_badge:
                badge_label = ctk.CTkLabel(
                    button_frame,
                    text="New",
                    font=BADGE_FONT,
                    text_color="#fff",
                    fg_color="#e53935",
                    corner_radius=8,
                    width=32,
                    height=18,
                )
                badge_label.grid(row=0, column=1, padx=(5, 0))

        # Place flexible spacer row right after the buttons so following widgets (Quit) are bottom-aligned
        spacer_row = len(nav_items) + 1
        self.grid_rowconfigure(spacer_row, weight=1)

        # Quit button at the bottom
        quit_button = ctk.CTkButton(
            self,
            text="Quit",
            fg_color="transparent",
            text_color="#d63031",
            anchor="w",
            hover_color="#1E2732",
            font=SIDEBAR_FONT,
            command=master.quit_app,
        )
        quit_button.grid(
            row=spacer_row + 1, column=0, sticky="ew", padx=10, pady=(0, 20)
        )

        self.active_button = None
        self.select_button("home_page")  # Default active page

    def select_button(self, name):
        if self.active_button:
            self.active_button.configure(text_color="white", fg_color="transparent")

        button = self.nav_buttons.get(name)
        if button:
            button.configure(text_color="#ff9800", fg_color="#2d333b")
            self.active_button = button


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ransomware Simulator")
        self.after(0, lambda: self.state("zoomed"))
        # self.minsize(900, 600)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = NavigationSidebar(self, command=self.change_page, width=180)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        # Main content frame
        self.main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(0, weight=1)

        # Dictionary to hold page instances
        self.pages = {}
        self.current_page = None

        # Initialize pages
        self._create_pages()

        # Ensure the safe zone directory exists
        self._create_safe_zone()

        self.change_page("home_page")  # Set initial page

    def _create_safe_zone(self):
        """Creates the Ransomware_Test directory if it doesn't exist."""
        try:
            SAFE_ZONE_PATH.mkdir(exist_ok=True)
            print(f"Safe zone directory ensured at: {SAFE_ZONE_PATH.resolve()}")
        except OSError as e:
            print(f"Error creating safe zone directory: {e}")

    def _create_pages(self):
        self.pages["home_page"] = HomePage(self.main_content_frame)
        self.pages["dashboard_page"] = DashboardPage(self.main_content_frame)
        self.pages["simulation_page"] = SimulationPage(self.main_content_frame)
        self.pages["recovery_page"] = RecoveryPage(self.main_content_frame)
        self.pages["sentinel_page"] = SentinelPage(self.main_content_frame)
        self.pages["reports_page"] = ReportsPage(self.main_content_frame)

    def change_page(self, page_name):
        if self.current_page:
            self.current_page.grid_forget()  # Hide current page

        page = self.pages.get(page_name)
        if page:
            page.grid(row=0, column=0, sticky="nsew")  # Show new page
            self.current_page = page
            self.sidebar.select_button(page_name)  # Update sidebar button state

            # Refresh reports page if applicable
            if page_name == "reports_page" and hasattr(page, "refresh_reports"):
                page.refresh_reports()

    def quit_app(self):
        """Gracefully quit the application."""
        # Stop Sentinel watchdog monitoring
        if "sentinel_page" in self.pages:
            sentinel_page = self.pages["sentinel_page"]
            if hasattr(sentinel_page, "stop_monitoring"):
                sentinel_page.stop_monitoring()

        self.destroy()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
