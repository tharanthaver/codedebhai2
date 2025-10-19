import os
import sys
import subprocess
import platform
from datetime import datetime
import psutil

# Global cache for user-to-terminal-path assignments
_user_path_cache = {}
_next_template_index = 0

# 50 predefined terminal path templates with {name} placeholder
TERMINAL_PATH_TEMPLATES = [
    "PS C:\\Users\\{name}\\Documents> ",
    "PS C:\\Users\\{name}\\Desktop> ",
    "PS C:\\Users\\{name}\\Projects> ",
    "PS C:\\Users\\{name}\\Downloads> ",
    "PS C:\\Users\\{name}\\Pictures> ",
    "PS C:\\Users\\{name}\\Music> ",
    "PS C:\\Users\\{name}\\Videos> ",
    "PS C:\\Users\\{name}\\AppData\\Local> ",
    "PS C:\\Users\\{name}\\OneDrive> ",
    "PS C:\\Users\\{name}\\Source\\Repos> ",
    "PS C:\\Program Files> ",
    "PS C:\\Program Files (x86)> ",
    "PS C:\\Windows\\System32> ",
    "PS C:\\temp> ",
    "PS C:\\data> ",
    "PS D:\\Projects\\{name}> ",
    "PS D:\\Backup> ",
    "PS E:\\Storage> ",
    "PS C:\\inetpub\\wwwroot> ",
    "PS C:\\logs> ",
    "PS C:\\Users\\{name}\\workspace> ",
    "PS C:\\dev\\{name}> ",
    "PS C:\\code\\projects> ",
    "PS C:\\scripts> ",
    "PS C:\\tools> ",
    "PS C:\\bin> ",
    "PS C:\\lib> ",
    "PS C:\\src> ",
    "PS C:\\build> ",
    "PS C:\\output> ",
    "PS C:\\Users\\{name}\\node_modules> ",
    "PS C:\\Users\\{name}\\venv> ",
    "PS C:\\Users\\{name}\\conda> ",
    "PS C:\\ProgramData> ",
    "PS C:\\Windows\\Temp> ",
    "PS C:\\Windows\\Logs> ",
    "PS C:\\Users\\{name}\\git> ",
    "PS C:\\repos\\{name}> ",
    "PS C:\\shared> ",
    "PS C:\\public> ",
    "PS C:\\upload> ",
    "PS C:\\media> ",
    "PS C:\\assets> ",
    "PS C:\\config> ",
    "PS C:\\database> ",
    "PS C:\\cache> ",
    "PS C:\\sessions> ",
    "PS C:\\backup\\{name}> ",
    "PS C:\\reports> ",
    "PS C:\\analytics> "
]

class TerminalUtils:
    """Utility class for terminal operations and screenshot functionality"""
    
    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
    
    @staticmethod
    def get_user_terminal_path(name: str) -> str:
        """
        Retrieve or assign a terminal path for a given user, replacing {name} with the actual user name.

        Args:
            name (str): The user's name

        Returns:
            str: The personalized terminal path
        """
        global _next_template_index

        if name in _user_path_cache:
            template_index = _user_path_cache[name]
        else:
            template_index = _next_template_index
            _next_template_index = (_next_template_index + 1) % len(TERMINAL_PATH_TEMPLATES)
            _user_path_cache[name] = template_index        

        # Replace the {name} placeholder with the actual user's name
        cleaned_name = name.strip().replace(' ', '').lower()
        return TERMINAL_PATH_TEMPLATES[template_index].replace('{name}', cleaned_name)

    def generate_clean_terminal_path(self, suppress_extra_prompt=True):
        """
        Generate a clean terminal path without extra prompts
        
        Args:
            suppress_extra_prompt (bool): Whether to suppress extra terminal prompts
        """
        try:
            current_dir = os.getcwd()
            
            if self.is_windows:
                # For Windows PowerShell, create a clean prompt
                user = os.environ.get('USERNAME', 'User')
                
                # Shorten long paths
                if len(current_dir) > 50:
                    parts = current_dir.split('\\')
                    if len(parts) > 3:
                        current_dir = f"{parts[0]}\\...\\{parts[-2]}\\{parts[-1]}"
                
                # Clean terminal prompt format
                prompt = f"PS {current_dir}> "
                
                if suppress_extra_prompt:
                    # Clear any lingering prompts
                    self._clear_terminal_buffer()
                    
                return prompt
            else:
                # For Unix-like systems
                user = os.environ.get('USER', 'user')
                hostname = os.environ.get('HOSTNAME', 'localhost')
                
                # Shorten path for better display
                home = os.path.expanduser('~')
                if current_dir.startswith(home):
                    current_dir = current_dir.replace(home, '~', 1)
                
                prompt = f"{user}@{hostname}:{current_dir}$ "
                
                if suppress_extra_prompt:
                    self._clear_terminal_buffer()
                    
                return prompt
                
        except Exception as e:
            print(f"Error generating terminal path: {e}")
            return "$ "
    
    def _clear_terminal_buffer(self):
        """Clear terminal buffer to prevent extra prompts"""
        try:
            if self.is_windows:
                # For Windows, clear the screen and reset cursor
                os.system('cls')
                # Reset PowerShell prompt if needed
                subprocess.run(['powershell', '-Command', 'Clear-Host'], 
                             capture_output=True, text=True, timeout=2)
            else:
                # For Unix-like systems
                os.system('clear')
                
        except Exception as e:
            # Silently handle errors to avoid disrupting terminal flow
            pass
    
    def suppress_extra_terminal_output(self):
        """
        Suppress extra terminal output that appears after script execution
        """
        try:
            if self.is_windows:
                # Kill any hanging PowerShell processes
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if 'powershell' in proc.info['name'].lower():
                            # Only kill child processes, not the main shell
                            if proc.pid != os.getpid() and proc.pid != os.getppid():
                                proc.terminate()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                        
                # Reset terminal state
                sys.stdout.flush()
                sys.stderr.flush()
                
        except Exception as e:
            # Silently handle errors
            pass
    
    def create_screenshot_function(self, output_path="screenshot.png"):
        """
        Create a screenshot of the terminal window
        
        Args:
            output_path (str): Path where the screenshot should be saved
        """
        try:
            if self.is_windows:
                # Use Windows built-in screenshot capability
                import win32gui
                import win32ui
                import win32con
                from PIL import Image
                
                # Get the terminal window
                hwnd = win32gui.GetForegroundWindow()
                
                # Get window dimensions
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                width = right - left
                height = bottom - top
                
                # Create device context
                hwndDC = win32gui.GetWindowDC(hwnd)
                mfcDC = win32ui.CreateDCFromHandle(hwndDC)
                saveDC = mfcDC.CreateCompatibleDC()
                
                # Create bitmap
                saveBitMap = win32ui.CreateBitmap()
                saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
                saveDC.SelectObject(saveBitMap)
                
                # Copy window content to bitmap
                saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
                
                # Convert to PIL Image and save
                bmpinfo = saveBitMap.GetInfo()
                bmpstr = saveBitMap.GetBitmapBits(True)
                
                img = Image.frombuffer(
                    'RGB',
                    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                    bmpstr, 'raw', 'BGRX', 0, 1
                )
                
                img.save(output_path)
                
                # Clean up
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)
                
                return f"Screenshot saved to {output_path}"
                
            else:
                # For Linux/macOS, use system screenshot tools
                try:
                    # Try different screenshot tools
                    screenshot_tools = [
                        ['gnome-screenshot', '-f', output_path],
                        ['scrot', output_path],
                        ['import', '-window', 'root', output_path],  # ImageMagick
                        ['screencapture', output_path]  # macOS
                    ]
                    
                    for tool in screenshot_tools:
                        try:
                            subprocess.run(tool, check=True, timeout=10)
                            return f"Screenshot saved to {output_path}"
                        except (subprocess.CalledProcessError, FileNotFoundError):
                            continue
                    
                    return "No screenshot tool available on this system"
                    
                except Exception as e:
                    return f"Error taking screenshot: {e}"
                    
        except ImportError:
            return "Required libraries not installed for screenshot functionality"
        except Exception as e:
            return f"Error creating screenshot: {e}"
    
    def fix_terminal_prompt_display(self):
        """
        Fix terminal prompt display issues by resetting terminal state
        """
        try:
            if self.is_windows:
                # Reset PowerShell prompt
                reset_commands = [
                    'powershell -Command "Clear-Host"',
                    'powershell -Command "$Host.UI.RawUI.CursorPosition = @{X=0; Y=0}"'
                ]
                
                for cmd in reset_commands:
                    try:
                        subprocess.run(cmd, shell=True, capture_output=True, timeout=2)
                    except:
                        continue
            else:
                # Reset Unix terminal
                reset_commands = [
                    'reset',
                    'clear',
                    'tput clear'
                ]
                
                for cmd in reset_commands:
                    try:
                        subprocess.run(cmd.split(), capture_output=True, timeout=2)
                    except:
                        continue
                        
            # Force flush output streams
            sys.stdout.flush()
            sys.stderr.flush()
            
            return "Terminal prompt reset successfully"
            
        except Exception as e:
            return f"Error resetting terminal: {e}"


# Convenience functions for easy use
def clean_terminal_path():
    """Generate a clean terminal path"""
    utils = TerminalUtils()
    return utils.generate_clean_terminal_path()

def take_screenshot(output_path="terminal_screenshot.png"):
    """Take a screenshot of the terminal"""
    utils = TerminalUtils()
    return utils.create_screenshot_function(output_path)

def fix_terminal():
    """Fix terminal display issues"""
    utils = TerminalUtils()
    return utils.fix_terminal_prompt_display()

def suppress_extra_output():
    """Suppress extra terminal output"""
    utils = TerminalUtils()
    utils.suppress_extra_terminal_output()


# Example usage and test function
if __name__ == "__main__":
    utils = TerminalUtils()
    
    print("Testing terminal utilities...")
    print(f"Clean path: {utils.generate_clean_terminal_path()}")
    print(f"Screenshot result: {utils.create_screenshot_function()}")
    print(f"Terminal fix result: {utils.fix_terminal_prompt_display()}")
    
    # Suppress any extra output at the end
    utils.suppress_extra_terminal_output()
