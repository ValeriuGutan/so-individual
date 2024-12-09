import sys
import os
from PyQt6.QtWidgets import QApplication
from frontend.src.views.main_window import MainWindow

def main():
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        window = MainWindow()
        window.show()
        
        return app.exec()
    except Exception as e:
        print(f"Error in main: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())