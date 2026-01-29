import customtkinter as ctk
from typing import Dict, Optional

class AIGuide:
    """AI Guide that provides contextual help and tooltips"""
    
    def __init__(self):
        self.tips: Dict[str, str] = {
            "dashboard_start": """Welcome to the Ransomware Simulator Dashboard!
            
1. First, select an encryption algorithm from the dropdown
2. Choose a target folder using the 'Choose' button
3. Optionally customize the ransom note
4. Click 'Start' to begin the simulation
5. Monitor progress in the Statistics panel
6. Use 'Stop' to cancel at any time""",

            "encryption_types": """Available Encryption Methods:
            
• AES 256 - Industry standard symmetric encryption
• RSA - Public key cryptography, good for small files
• ChaCha20 - Modern stream cipher, fast on mobile devices""",

            "sandbox_warning": """⚠️ Sandbox Mode:
            
The simulator runs in a sandbox environment to prevent 
accidental encryption of important files. Always test in 
a safe folder with sample data.""",

            "stats_help": """Statistics Panel Guide:
            
• Progress wheel shows % completion
• Files Found - Total files detected
• Files Encrypted - Number processed so far
• Elapsed Time - Duration of current run"""
        }
        
        self.popup: Optional[ctk.CTkToplevel] = None

    def show_tip(self, key: str, parent: ctk.CTkBaseClass):
        """Display a tooltip with guide information"""
        if key not in self.tips:
            return
            
        if self.popup:
            self.popup.destroy()
            
        self.popup = ctk.CTkToplevel(parent)
        self.popup.title("Guide")
        self.popup.geometry("400x300")
        
        # Add icon/image for AI assistant
        icon = ctk.CTkLabel(self.popup, text="🤖", font=("Segoe UI Emoji", 32))
        icon.pack(pady=10)
        
        # Tip content
        content = ctk.CTkTextbox(self.popup, width=360, height=200)
        content.pack(padx=20, pady=10)
        content.insert("1.0", self.tips[key])
        content.configure(state="disabled")
        
        # Close button
        ctk.CTkButton(
            self.popup, 
            text="Got it!",
            width=100,
            command=self.popup.destroy
        ).pack(pady=10)
        
        # Position popup near parent
        self.popup.transient(parent)
        x = parent.winfo_rootx() + 50
        y = parent.winfo_rooty() + 50
        self.popup.geometry(f"+{x}+{y}")