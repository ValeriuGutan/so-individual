import sys
import os

# Determinăm calea către directorul rădăcină al aplicației
if getattr(sys, 'frozen', False):
    # Suntem într-un build PyInstaller
    application_path = sys._MEIPASS
else:
    # Suntem în development
    application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Adăugăm calea la PYTHONPATH
sys.path.append(application_path)

from frontend.src.main import main

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1) 