import sys

class LogRedirector:
    def __init__(self, log_widget):
        self.log_widget = log_widget

    def write(self, message):
        if message.strip():  # avoid blank lines
            self.log_widget.add_log(message.strip())

    def flush(self):
        pass  # required for file-like compatibility
