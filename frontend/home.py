import customtkinter as ctk
import webbrowser

class HomePage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#111111", **kwargs)
        
        # Configure grid to center the content
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create a central container
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.grid(row=0, column=0, sticky="ns")
        
        # --- HEADER SECTION ---
        # Icon (Placeholder)
        self.icon_label = ctk.CTkLabel(
            self.center_frame,
            text="🛡️",  # Shield icon as placeholder
            font=("Roboto", 40),
            text_color="white"
        )
        self.icon_label.pack(pady=(0, 10))

        # "ABOUT" Title
        self.about_label = ctk.CTkLabel(
            self.center_frame, 
            text="ABOUT", 
            font=("Roboto", 16, "bold"), 
            text_color="white"
        )
        self.about_label.pack(pady=(40, 5))

        # Orange Separator Line
        self.separator = ctk.CTkFrame(
            self.center_frame, 
            height=2, 
            width=100, 
            fg_color="#F57C00"
        )
        self.separator.pack(pady=(0, 40))

        # --- DISCLAIMER SECTION ---
        # "DISCLAIMER :" Title
        self.disclaimer_title = ctk.CTkLabel(
            self.center_frame, 
            text="DISCLAIMER :", 
            font=("Roboto", 18, "bold"), 
            text_color="white",
            anchor="w"
        )
        # Pack with fill="x" so it aligns left relative to the text block if we use a frame, 
        # or just standard pack if we want it centered above. 
        # The prompt says "Align this slightly to the left of the text block below it."
        # A simple way is to put both in a frame that is centered, but their contents are left aligned?
        # Let's try packing it normally first, but maybe using a frame for the text block.
        
        self.content_container = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.content_container.pack(pady=(0, 30), padx=20)

        self.disclaimer_title.pack(in_=self.content_container, anchor="w", pady=(0, 10))

        disclaimer_text = (
            "SAFETY & LIABILITY : This Ransomware Simulator interacts with the file system to "
            "encrypt data. While it includes safety mechanisms (such as non-destructive defaults "
            "and specific targeting), it should strictly be run in a disposable environment. "
            "The creator of this project is not responsible for accidental encryption of sensitive "
            "files or any damage caused by modifying the source code to act maliciously. "
            "Usage of this tool for attacking targets without prior mutual consent is illegal. "
            "This project is provided 'as-is' without warranty of any kind."
        )

        self.disclaimer_body = ctk.CTkLabel(
            self.content_container,
            text=disclaimer_text,
            font=("Roboto", 20),
            text_color="#CCCCCC",
            wraplength=600,
            justify="left"
        )
        self.disclaimer_body.pack(anchor="w")

        # --- LINKS SECTION ---
        self.links_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.links_frame.pack(pady=(0, 50))

        # Github Link
        self.github_container = ctk.CTkFrame(self.links_frame, fg_color="transparent")
        self.github_container.pack(side="left", padx=20)
        
        self.github_label = ctk.CTkLabel(
            self.github_container, 
            text="Github", 
            font=("Roboto", 14), 
            text_color="white",
            cursor="hand2"
        )
        self.github_label.pack()
        # Bind click event (placeholder URL)
        self.github_label.bind("<Button-1>", lambda e: self.open_link("https://github.com"))
        
        # Github Underline
        self.github_line = ctk.CTkFrame(self.github_container, height=1, width=40, fg_color="white")
        self.github_line.pack(pady=(2, 0))

        # Documentation Link
        self.docs_container = ctk.CTkFrame(self.links_frame, fg_color="transparent")
        self.docs_container.pack(side="left", padx=20)

        self.docs_label = ctk.CTkLabel(
            self.docs_container, 
            text="Documentation", 
            font=("Roboto", 14), 
            text_color="white",
            cursor="hand2"
        )
        self.docs_label.pack()
        # Bind click event (placeholder URL)
        self.docs_label.bind("<Button-1>", lambda e: self.open_link("https://example.com/docs"))

        # Docs Underline
        self.docs_line = ctk.CTkFrame(self.docs_container, height=1, width=90, fg_color="white")
        self.docs_line.pack(pady=(2, 0))


        # --- PROCEED BUTTON ---
        self.proceed_btn = ctk.CTkButton(
            self.center_frame,
            text="Proceed",
            font=("Roboto", 14, "bold"),
            fg_color="#F57C00",
            hover_color="#E65100",
            corner_radius=20,
            width=200,
            height=40,
            command=self.go_to_dashboard
        )
        self.proceed_btn.pack(pady=(0, 40))

    def open_link(self, url):
        webbrowser.open_new(url)

    def go_to_dashboard(self):
        # Traverse up to find the MainApp instance that has 'change_page'
        app = self.master
        while app is not None and not hasattr(app, "change_page"):
            app = getattr(app, "master", None)
        
        if app:
            app.change_page("dashboard_page")
        else:
            print("Error: Could not find main application controller.")