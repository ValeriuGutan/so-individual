from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QStackedWidget, QLabel)
from PyQt6.QtCore import Qt
from .organization_view import OrganizationView
from .invoice_view import InvoiceView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice Manager")
        self.setGeometry(100, 100, 1200, 800)
        
        # Setăm stilul general al aplicației
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
                color: white;
                background-color: #2196F3;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QLabel {
                color: #333333;
            }
        """)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: white;
            }
            QPushButton {
                text-align: left;
                padding: 12px 24px;
                border-radius: 0;
                background-color: transparent;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #34495e;
                border-left: 4px solid #2196F3;
            }
            QLabel {
                color: white;
                padding: 20px;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Logo/Titlu
        title = QLabel("Invoice Manager")
        sidebar_layout.addWidget(title)
        
        # Butoane navigare
        self.btn_organizations = QPushButton("Organizations")
        self.btn_invoices = QPushButton("Invoices")
        
        self.btn_organizations.setCheckable(True)
        self.btn_invoices.setCheckable(True)
        
        sidebar_layout.addWidget(self.btn_organizations)
        sidebar_layout.addWidget(self.btn_invoices)
        sidebar_layout.addStretch()
        
        layout.addWidget(sidebar)
        
        # Container pentru conținut
        content_container = QWidget()
        content_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
            }
        """)
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Stack pentru views
        self.stack = QStackedWidget()
        self.organization_view = OrganizationView()
        self.invoice_view = InvoiceView()
        
        self.stack.addWidget(self.organization_view)
        self.stack.addWidget(self.invoice_view)
        content_layout.addWidget(self.stack)
        
        layout.addWidget(content_container)
        
        # Conectăm butoanele
        self.btn_organizations.clicked.connect(self.show_organizations)
        self.btn_invoices.clicked.connect(self.show_invoices)
        
        # Setăm view-ul inițial
        self.show_organizations()
        
    def show_organizations(self):
        self.stack.setCurrentWidget(self.organization_view)
        self.btn_organizations.setChecked(True)
        self.btn_invoices.setChecked(False)
        
    def show_invoices(self):
        self.stack.setCurrentWidget(self.invoice_view)
        self.btn_organizations.setChecked(False)
        self.btn_invoices.setChecked(True)