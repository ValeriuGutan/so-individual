from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QDialog, QLineEdit, 
                            QFormLayout, QMessageBox, QLabel, QHeaderView)
from PyQt6.QtCore import Qt
from ..api.client import APIClient

class OrganizationView(QWidget):
    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.init_ui()
        self.load_organizations()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Organizations")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        
        btn_add = QPushButton("Add Organization")
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_add.clicked.connect(self.show_add_dialog)
        header_layout.addStretch()
        header_layout.addWidget(btn_add)
        
        layout.addLayout(header_layout)
        
        # Tabel
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Fiscal Code", "Address", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                gridline-color: #f0f0f0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                font-weight: bold;
                color: #2c3e50;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
                color: #333333;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #2c3e50;
            }
        """)
        layout.addWidget(self.table)
        
    def load_organizations(self):
        try:
            organizations = self.api_client.get_organizations()
            self.table.setRowCount(len(organizations))
            for i, org in enumerate(organizations):
                self.table.setItem(i, 0, QTableWidgetItem(str(org['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(org['name']))
                self.table.setItem(i, 2, QTableWidgetItem(org['fiscal_code'] or ''))
                self.table.setItem(i, 3, QTableWidgetItem(org['address'] or ''))
                
                # Butoane pentru acțiuni
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 4, 4, 4)
                
                # Creăm funcții separate pentru fiecare buton
                def create_edit_handler(org_id):
                    return lambda: self.show_edit_dialog(org_id)
                
                def create_delete_handler(org_id):
                    return lambda: self.delete_organization(org_id)
                
                btn_edit = QPushButton("Edit")
                btn_delete = QPushButton("Delete")
                
                # Stil comun pentru butoane
                button_style = """
                    QPushButton {
                        color: white;
                        padding: 6px 12px;
                        border-radius: 4px;
                        font-weight: bold;
                        font-size: 12px;
                        min-width: 70px;
                        margin: 0 3px;
                    }
                """
                
                # Stil pentru butonul Edit
                btn_edit.setStyleSheet(button_style + """
                    QPushButton {
                        background-color: #2196F3;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                    QPushButton:pressed {
                        background-color: #1565C0;
                    }
                """)
                
                # Stil pentru butonul Delete
                btn_delete.setStyleSheet(button_style + """
                    QPushButton {
                        background-color: #f44336;
                    }
                    QPushButton:hover {
                        background-color: #d32f2f;
                    }
                    QPushButton:pressed {
                        background-color: #c62828;
                    }
                """)
                
                # Ajustăm layout-ul pentru butoane
                actions_layout.setSpacing(8)  # Spațiu între butoane
                actions_layout.setContentsMargins(8, 4, 8, 4)  # Margini pentru container
                
                actions_widget.setStyleSheet("""
                    QWidget {
                        background: transparent;
                    }
                """)
                
                # Conectăm butoanele folosind funcțiile create
                btn_edit.clicked.connect(create_edit_handler(org['id']))
                btn_delete.clicked.connect(create_delete_handler(org['id']))
                
                actions_layout.addWidget(btn_edit)
                actions_layout.addWidget(btn_delete)
                actions_layout.addStretch()
                
                self.table.setCellWidget(i, 4, actions_widget)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load organizations: {str(e)}")

    def show_add_dialog(self):
        dialog = OrganizationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_organizations()
            
    def show_edit_dialog(self, org_id):
        try:
            org = self.api_client.get_organization(org_id)
            dialog = OrganizationDialog(self, org)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_organizations()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load organization: {str(e)}")
            
    def delete_organization(self, org_id):
        try:
            self.api_client.delete_organization(org_id)
            self.load_organizations()  # Reîncărcăm lista după ștergere
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not delete organization: {str(e)}")

class OrganizationDialog(QDialog):
    def __init__(self, parent=None, organization=None):
        super().__init__(parent)
        self.api_client = APIClient()
        self.organization = organization
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Add Organization" if not self.organization else "Edit Organization")
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        
        # Câmpuri
        self.name_edit = QLineEdit()
        self.fiscal_code_edit = QLineEdit()
        self.address_edit = QLineEdit()
        
        if self.organization:
            self.name_edit.setText(self.organization['name'])
            self.fiscal_code_edit.setText(self.organization['fiscal_code'] or '')
            self.address_edit.setText(self.organization['address'] or '')
        
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Fiscal Code:", self.fiscal_code_edit)
        layout.addRow("Address:", self.address_edit)
        
        # Butoane
        buttons = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_cancel = QPushButton("Cancel")
        
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        btn_save.clicked.connect(self.save_organization)
        btn_cancel.clicked.connect(self.reject)
        
        buttons.addWidget(btn_save)
        buttons.addWidget(btn_cancel)
        layout.addRow(buttons)
        
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                color: #333333;
                font-size: 14px;
                min-width: 300px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
                background-color: #f8f9fa;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton[text="Save"] {
                background-color: #4CAF50;
                min-width: 100px;
            }
            QPushButton[text="Save"]:hover {
                background-color: #45a049;
            }
            QPushButton[text="Cancel"] {
                background-color: #f44336;
                min-width: 100px;
            }
            QPushButton[text="Cancel"]:hover {
                background-color: #da190b;
            }
            QFormLayout {
                spacing: 15px;
            }
        """)
        
    def save_organization(self):
        try:
            data = {
                'name': self.name_edit.text(),
                'fiscal_code': self.fiscal_code_edit.text(),
                'address': self.address_edit.text()
            }
            
            if self.organization:
                self.api_client.update_organization(self.organization['id'], data)
            else:
                self.api_client.create_organization(data)
                
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save organization: {str(e)}")