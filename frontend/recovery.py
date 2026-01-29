import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

# Fonts / colors (keep consistent with app theme)
TITLE_FONT = ("Roboto", 24, "bold")
SUBTITLE_FONT = ("Roboto", 12)
LABEL_FONT = ("Roboto", 11)
ENTRY_FONT = ("Roboto", 11)
BTN_FONT = ("Roboto", 13, "bold")

FG_ORANGE = "#D35400"
FG_ORANGE_HOVER = "#A04000"
FG_GREEN = "#27AE60"
FG_GREEN_HOVER = "#1E8449"
CARD_BG = "#2b2b2b"


class RecoveryPage(ctk.CTkFrame):
    """
    Recover Files UI frame.
    Place this frame into your main content area (sidebar is assumed to exist separately).
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        # center wrapper so page looks like reference
        self.grid_columnconfigure(0, weight=1)
        wrapper = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=12)
        wrapper.grid(row=0, column=0, padx=50, pady=30, sticky="nsew")
        wrapper.grid_columnconfigure(0, weight=1)

        # Title and subtitle
        title = ctk.CTkLabel(wrapper, text="Recover Files", font=TITLE_FONT, text_color="white")
        title.grid(row=0, column=0, pady=(20, 6), padx=24, sticky="n")

        subtitle = ctk.CTkLabel(
            wrapper,
            text="Decrypt files using the key generated during simulation.",
            font=SUBTITLE_FONT,
            text_color="#cccccc"
        )
        subtitle.grid(row=1, column=0, pady=(0, 18), padx=24, sticky="n")

        form = ctk.CTkFrame(wrapper, fg_color="transparent")
        form.grid(row=2, column=0, padx=36, pady=(0, 20), sticky="ew")
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=0)

        # Decryption Key Input
        key_label = ctk.CTkLabel(form, text="Decryption Key Input", font=LABEL_FONT, text_color="#dddddd")
        key_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        self.key_entry = ctk.CTkEntry(form, placeholder_text="Decryption Key Input", font=ENTRY_FONT, state="readonly")
        self.key_entry.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(0, 12))

        browse_key_btn = ctk.CTkButton(
            form,
            text="Browse Key",
            width=110,
            fg_color="#1976d2",
            hover_color="#145a9a",
            font=BTN_FONT,
            command=self.browse_key_file
        )
        browse_key_btn.grid(row=1, column=1, sticky="e", pady=(0, 12))

        # Folder selector
        folder_label = ctk.CTkLabel(form, text="Folder Selector", font=LABEL_FONT, text_color="#dddddd")
        folder_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 6))

        self.folder_entry = ctk.CTkEntry(form, placeholder_text="Folder Selector", font=ENTRY_FONT, state="readonly")
        self.folder_entry.grid(row=3, column=0, sticky="ew", padx=(0, 8), pady=(0, 12))

        folder_btn = ctk.CTkButton(
            form,
            text="Select",
            width=110,
            fg_color="#1976d2",
            hover_color="#145a9a",
            font=BTN_FONT,
            command=self.select_folder
        )
        folder_btn.grid(row=3, column=1, sticky="e", pady=(0, 12))

        # Algorithm selector
        algo_label = ctk.CTkLabel(form, text="Algorithm Selector", font=LABEL_FONT, text_color="#dddddd")
        algo_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, 6))

        # CTkComboBox may not be available in older CTk; OptionMenu is a compatible alternative.
        try:
            self.algorithm_selector = ctk.CTkComboBox(form, values=["RSA", "AES", "ChaCha20"], font=ENTRY_FONT)
            self.algorithm_selector.set("RSA")
        except Exception:
            self.algorithm_selector = ctk.CTkOptionMenu(form, values=["RSA", "AES", "ChaCha20"], font=ENTRY_FONT)
            self.algorithm_selector.set("RSA")

        self.algorithm_selector.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 18))

        # Action Buttons area
        actions = ctk.CTkFrame(wrapper, fg_color="transparent")
        actions.grid(row=3, column=0, padx=36, pady=(0, 28), sticky="ew")
        actions.grid_columnconfigure(0, weight=1)

        self.recover_btn = ctk.CTkButton(
            actions,
            text="Recover Files",
            fg_color=FG_ORANGE,
            hover_color=FG_ORANGE_HOVER,
            font=BTN_FONT,
            height=44,
            corner_radius=10,
            command=self._on_recover_clicked
        )
        self.recover_btn.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.success_btn = ctk.CTkButton(
            actions,
            text="Recovery Successful",
            fg_color=FG_GREEN,
            hover_color=FG_GREEN_HOVER,
            font=BTN_FONT,
            height=40,
            corner_radius=10,
            state="disabled",
            command=self._on_success_clicked
        )
        self.success_btn.grid(row=1, column=0, sticky="ew")

        # small spacer at bottom
        wrapper.grid_rowconfigure(4, weight=1)

    def browse_key_file(self):
        """Open file dialog to pick a key file and show its path in the entry."""
        path = filedialog.askopenfilename(
            title="Select Decryption Key",
            filetypes=[("Key files", "*.bin *.key *.pem"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        if path:
            # update readonly entry
            self.key_entry.configure(state="normal")
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, path)
            self.key_entry.configure(state="readonly")

    def select_folder(self):
        """Open folder dialog to pick a folder to recover."""
        folder = filedialog.askdirectory(title="Select folder to recover", initialdir=os.path.expanduser("~"))
        if folder:
            self.folder_entry.configure(state="normal")
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
            self.folder_entry.configure(state="readonly")

    def _on_recover_clicked(self):
        """Placeholder: start recovery in background then enable success button when done."""
        key = self.key_entry.get().strip()
        folder = self.folder_entry.get().strip()
        algo = self.algorithm_selector.get() if hasattr(self.algorithm_selector, "get") else self.algorithm_selector.get()
        if not key:
            messagebox.showwarning("Missing key", "Please select a decryption key file before recovering.")
            return
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("Missing folder", "Please select a folder to recover.")
            return

        # Disable recover button while running
        self.recover_btn.configure(state="disabled")
        self.success_btn.configure(state="disabled")

        def work():
            try:
                # Simulate recovery work (replace this with real call to your decrypt logic)
                time.sleep(1.2)  # short delay for UX
                # Example: create a small log file in the selected folder
                try:
                    note_path = os.path.join(folder, "recovery_log.txt")
                    with open(note_path, "a", encoding="utf-8") as f:
                        f.write(f"Recovery attempted with key: {os.path.basename(key)} algorithm: {algo}\n")
                except Exception:
                    pass
                # on success enable success button
                def on_done():
                    self.success_btn.configure(state="normal")
                    messagebox.showinfo("Recovery", "Recovery simulation completed successfully.")
                self.after(0, on_done)
            finally:
                # Re-enable recover button (allow re-run)
                def restore():
                    self.recover_btn.configure(state="normal")
                self.after(0, restore)

        threading.Thread(target=work, daemon=True).start()

    def _on_success_clicked(self):
        """Optional hook for success button (can show details)."""
        messagebox.showinfo("Recovery Status", "Recovery was successful.")