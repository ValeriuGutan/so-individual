import sys
import os

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(application_path)

from frontend.src.main import main

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1) 