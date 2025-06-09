import subprocess
import signal
import os
from PyQt5.QtCore import QThread, pyqtSignal


class CommandWorker(QThread):
    finished = pyqtSignal(bool, str, str)

    def __init__(self, command):
        super().__init__()
        self.command = command
        self.placeholders = {}
        self.process = None
        self._should_terminate = False

    def get_placeholders(self):
        """Return a dictionary of placeholders. These are the variables
        enclosed in curly braces {} in the command string."""
        placeholders = {}
        parts = self.command.split()
        for part in parts:
            if part.startswith("{") and part.endswith("}"):
                key = part[1:-1]
                if key not in placeholders:
                    placeholders[key] = None
        return placeholders

    def expand_placeholders(self, placeholders):
        """Expand the placeholders in the command string using the provided dictionary."""
        expanded_command = self.command
        for key, value in placeholders.items():
            if value is not None:
                expanded_command = expanded_command.replace(f"{{{key}}}", str(value))
            else:
                expanded_command = expanded_command.replace(f"{{{key}}}", "")
        return expanded_command

    def run(self):
        try:
            expanded_command = self.expand_placeholders(self.placeholders)
            
            # Use Popen instead of run() to get process control
            self.process = subprocess.Popen(
                expanded_command, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid  # Create new process group for proper cleanup
            )
            
            # Wait for process to complete or be terminated
            stdout, stderr = self.process.communicate()
            
            if self._should_terminate:
                self.finished.emit(False, "", "Process was terminated by user")
            else:
                success = self.process.returncode == 0
                self.finished.emit(success, stdout, stderr)
                
        except Exception as e:
            self.finished.emit(False, "", str(e))
        finally:
            self.process = None

    def terminate_process(self):
        """Terminate the running subprocess"""
        self._should_terminate = True
        if self.process and self.process.poll() is None:  # Process is still running
            try:
                # Try graceful termination first
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                
                # Wait a bit for graceful shutdown
                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful termination didn't work
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                    self.process.wait()
                    
            except (ProcessLookupError, OSError):
                # Process already terminated
                pass

    def terminate(self):
        """Override Qt terminate to properly handle subprocess"""
        self.terminate_process()
        return super().terminate()