import os
import sys

def get_base_path():
    # Get the base path for the application, works both in development and when compiled
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (compiled)
        return sys._MEIPASS
    else:
        # If the application is run from a Python interpreter
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def ensure_comprovantes_dir():
    # Get the base path
    base_path = get_base_path()
    
    # Define the comprovantes directory path
    if getattr(sys, 'frozen', False):
        # When compiled, create comprovantes in the same directory as the executable
        comprovantes_dir = os.path.join(os.path.dirname(sys.executable), 'comprovantes')
    else:
        # In development, use the views/comprovantes directory
        comprovantes_dir = os.path.join(base_path, 'views', 'comprovantes')
    
    # Create the directory if it doesn't exist
    if not os.path.exists(comprovantes_dir):
        os.makedirs(comprovantes_dir)
    
    return comprovantes_dir