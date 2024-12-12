from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QDialog, QLineEdit, 
                            QFormLayout, QMessageBox, QLabel, QHeaderView,
                            QDateEdit, QComboBox, QSpinBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QDate, QLocale
from ..api.client import APIClient
from decimal import Decimal

class InvoiceView(QWidget):
    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.init_ui()
        

        try:
            self.load_invoices()
        except Exception as e:
            QMessageBox.warning(
                self,
                "Connection Error",
                "Could not connect to server. Please ensure the backend is running.\n\n"
                f"Error: {str(e)}"
            )
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Invoices")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        
        btn_add = QPushButton("Create Invoice")
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Organization", "Invoice Number", 
            "Issue Date", "Due Date", "Total Amount", "Actions"
        ])

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  
        self.table.setColumnWidth(0, 50) 
        
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Organization
        
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Invoice Number
        self.table.setColumnWidth(2, 150)
        
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Issue Date
        self.table.setColumnWidth(3, 100)
        
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Due Date
        self.table.setColumnWidth(4, 100)
        
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # Total Amount
        self.table.setColumnWidth(5, 120)
        
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # Actions
        self.table.setColumnWidth(6, 200)

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
        
    def load_invoices(self):
        try:
            invoices = self.api_client.get_invoices()
            self.table.setRowCount(len(invoices))
            for i, inv in enumerate(invoices):
                try:
                    self.table.setItem(i, 0, QTableWidgetItem(str(inv['id'])))
                    self.table.setItem(i, 1, QTableWidgetItem(inv.get('organization_name', 'N/A')))
                    self.table.setItem(i, 2, QTableWidgetItem(inv['invoice_number']))
                    self.table.setItem(i, 3, QTableWidgetItem(str(inv['issue_date'])))
                    self.table.setItem(i, 4, QTableWidgetItem(str(inv['due_date'])))
                    self.table.setItem(i, 5, QTableWidgetItem(f"${float(inv['total_amount']):.2f}"))
                    
                    actions_widget = QWidget()
                    actions_layout = QHBoxLayout(actions_widget)
                    actions_layout.setContentsMargins(4, 4, 4, 4)
                    
                except KeyError:
                    self.table.setItem(i, 1, QTableWidgetItem("N/A"))
                
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 4, 4, 4)
                
                btn_edit = QPushButton("Edit")
                btn_delete = QPushButton("Delete")
                
                btn_edit.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        padding: 5px 15px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                """)
                
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #f44336;
                        color: white;
                        padding: 5px 15px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #d32f2f;
                    }
                """)
                
                btn_edit.clicked.connect(lambda checked, invoice=inv: self.show_edit_dialog(invoice))
                btn_delete.clicked.connect(lambda checked, invoice_id=inv['id']: self.delete_invoice(invoice_id))
                
                actions_layout.addWidget(btn_edit)
                actions_layout.addWidget(btn_delete)
                actions_layout.addStretch()
                
                self.table.setCellWidget(i, 6, actions_widget)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load invoices: {str(e)}")

    def show_add_dialog(self):
        dialog = InvoiceDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_invoices()
            
    def show_edit_dialog(self, invoice):
        dialog = InvoiceDialog(self, invoice)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_invoices()
            
    def show_view_dialog(self, invoice_id):
        try:
            invoice = self.api_client.get_invoice(invoice_id)
            dialog = InvoiceViewDialog(self, invoice)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load invoice: {str(e)}")
            
    def delete_invoice(self, invoice_id):
        # Creăm un dialog de confirmare personalizat
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Delete")
        msg_box.setText("Are you sure you want to delete this invoice?")
        msg_box.setIcon(QMessageBox.Icon.Question)
        
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 14px;
                padding: 20px;
            }
            QPushButton {
                width: 100px;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
                color: white;
                margin: 0 5px;
            }
            QPushButton[text="Yes"] {
                background-color: #f44336;
            }
            QPushButton[text="Yes"]:hover {
                background-color: #d32f2f;
            }
            QPushButton[text="No"] {
                background-color: #2196F3;
            }
            QPushButton[text="No"]:hover {
                background-color: #1976D2;
            }
        """)
        
        # Adăugăm butoanele Yes/No
        yes_button = msg_box.addButton("Yes", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("No", QMessageBox.ButtonRole.NoRole)
        
        msg_box.setDefaultButton(no_button)
        
        response = msg_box.exec()
        
        if msg_box.clickedButton() == yes_button:
            try:
                self.api_client.delete_invoice(invoice_id)
                self.load_invoices()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete invoice: {str(e)}")

class InvoiceDialog(QDialog):
    def __init__(self, parent=None, invoice=None):
        super().__init__(parent)
        self.api_client = APIClient()
        self.invoice = invoice
        self.items = []
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Create Invoice" if not self.invoice else "Edit Invoice")
        self.setMinimumWidth(800)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        form_layout = QFormLayout()
        
        self.org_combo = QComboBox()
        self.load_organizations()
        
        self.invoice_number = QLineEdit()
        
        self.issue_date = QDateEdit()
        self.issue_date.setCalendarPopup(True)
        self.issue_date.setDate(QDate.currentDate())
        
        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)
        self.due_date.setDate(QDate.currentDate().addDays(30))
        
        self.notes = QLineEdit()
        
        form_layout.addRow("Organization:", self.org_combo)
        form_layout.addRow("Invoice Number:", self.invoice_number)
        form_layout.addRow("Issue Date:", self.issue_date)
        form_layout.addRow("Due Date:", self.due_date)
        form_layout.addRow("Notes:", self.notes)
        
        layout.addLayout(form_layout)
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["Description", "Quantity", "Unit", "Total", "Actions"])
        
        self.items_table.setColumnWidth(0, 300)  # Description
        self.items_table.setColumnWidth(1, 100)  # Quantity
        self.items_table.setColumnWidth(2, 100)  # Unit
        self.items_table.setColumnWidth(3, 100)  # Total
        self.items_table.setColumnWidth(4, 80)   # Actions

        # Setăm înălțimea rândurilor
        self.items_table.verticalHeader().setDefaultSectionSize(60)

        # Setăm tabelul să ocupe toată lățimea disponibilă
        self.items_table.horizontalHeader().setStretchLastSection(True)

        self.items_table.setStyleSheet("""
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
        layout.addWidget(self.items_table)

        # Add item button
        btn_add_item = QPushButton("Add Item")
        btn_add_item.clicked.connect(self.add_item_row)
        layout.addWidget(btn_add_item)
        
        # Total amount
        self.total_label = QLabel("Total: $0.00")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.total_label)
        
        # Buttons
        buttons = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_cancel = QPushButton("Cancel")
        
        btn_save.clicked.connect(self.save_invoice)
        btn_cancel.clicked.connect(self.reject)
        
        buttons.addWidget(btn_save)
        buttons.addWidget(btn_cancel)
        layout.addLayout(buttons)
        
        # Stil general pentru dialog
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                min-width: 800px;
                padding: 20px;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 14px;
            }
            QLineEdit, QDateEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #333;
                border-radius: 4px;
                background-color: white;
                color: #333;
                font-size: 14px;
                min-width: 200px;
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus, 
            QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #2196F3;
                background-color: #f8f9fa;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton[text="Save"] {
                background-color: #4CAF50;
            }
            QPushButton[text="Save"]:hover {
                background-color: #45a049;
            }
            QPushButton[text="Cancel"] {
                background-color: #f44336;
            }
            QPushButton[text="Cancel"]:hover {
                background-color: #d32f2f;
            }
            QPushButton[text="Add Item"] {
                background-color: #2196F3;
            }
            QPushButton[text="Add Item"]:hover {
                background-color: #1976D2;
            }
            QPushButton[text="×"] {
                background-color: #f44336;
                min-width: 30px;
                padding: 4px;
            }
            QPushButton[text="×"]:hover {
                background-color: #d32f2f;
            }
        """)
        
        if self.invoice:
            self.load_invoice_data()
        else:
            self.add_item_row()
            
    def add_item_row(self, item_data=None):
        row_position = self.items_table.rowCount()
        self.items_table.insertRow(row_position)

        # Folosim QDoubleSpinBox pentru numere cu zecimale
        description = QLineEdit()
        quantity = QDoubleSpinBox()
        unit_price = QDoubleSpinBox()
        total = QLineEdit()
        
        # Configurăm spinbox-urile
        quantity.setRange(0, 999999.99)
        quantity.setDecimals(2)
        unit_price.setRange(0, 999999.99)
        unit_price.setDecimals(2)
        
        # Setăm configurația pentru numere
        for spinbox in [quantity, unit_price]:
            spinbox.setRange(0, 999999.99)
            spinbox.setDecimals(2)
            spinbox.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        
        # Setăm valorile dacă avem date
        if item_data:
            description.setText(item_data['description'])
            quantity.setValue(float(item_data['quantity']))
            unit_price.setValue(float(item_data['unit_price']))
            total.setText(f"{float(item_data['total_price']):.2f}")
            total.setReadOnly(True)

        # Actualizăm totalul când se schimbă cantitatea sau prețul unitar
        def update_total():
            try:
                item_total = quantity.value() * unit_price.value()
                total.setText(f"{item_total:.2f}")
                self.update_grand_total()
            except:
                total.setText("0.00")

        quantity.valueChanged.connect(update_total)
        unit_price.valueChanged.connect(update_total)

        btn_delete = QPushButton("×")
        btn_delete.clicked.connect(lambda: self.delete_item_row(row_position))

        self.items_table.setCellWidget(row_position, 0, description)
        self.items_table.setCellWidget(row_position, 1, quantity)
        self.items_table.setCellWidget(row_position, 2, unit_price)
        self.items_table.setCellWidget(row_position, 3, total)
        self.items_table.setCellWidget(row_position, 4, btn_delete)

    def delete_item_row(self, row):
        self.items_table.removeRow(row)
        self.update_grand_total()

    def update_grand_total(self):
        total = 0
        for row in range(self.items_table.rowCount()):
            total_widget = self.items_table.cellWidget(row, 3)
            if total_widget:
                try:
                    total += float(total_widget.text())
                except ValueError:
                    pass
        self.total_label.setText(f"Total: ${total:.2f}")
        
    def save_invoice(self):
        try:
            items = []
            for row in range(self.items_table.rowCount()):
                description = self.items_table.cellWidget(row, 0).text()
                quantity = self.items_table.cellWidget(row, 1).value()
                unit_price = self.items_table.cellWidget(row, 2).value()
                
                if not description or quantity <= 0 or unit_price <= 0:
                    raise ValueError("All items must have description and valid quantity/price")
                    
                items.append({
                    'description': description,
                    'quantity': quantity,
                    'unit_price': unit_price
                })
            
            if not items:
                raise ValueError("Invoice must have at least one item")
                
            # Construim datele facturii
            data = {
                'organization_id': self.org_combo.currentData(),
                'invoice_number': self.invoice_number.text(),
                'issue_date': self.issue_date.date().toString(Qt.DateFormat.ISODate),
                'due_date': self.due_date.date().toString(Qt.DateFormat.ISODate),
                'notes': self.notes.text(),
                'items': items
            }
            
            # Validăm datele
            if not data['organization_id']:
                raise ValueError("Please select an organization")
            if not data['invoice_number']:
                raise ValueError("Invoice number is required")
                
            # Trimitem request-ul
            if self.invoice:
                response = self.api_client.update_invoice(self.invoice['id'], data)
            else:
                response = self.api_client.create_invoice(data)
                
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save invoice: {str(e)}")
            
    def load_organizations(self):
        try:
            organizations = self.api_client.get_organizations()
            for org in organizations:
                self.org_combo.addItem(org['name'], org['id'])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load organizations: {str(e)}")
            
    def load_invoice_data(self):
        self.invoice_number.setText(self.invoice['invoice_number'])
        self.issue_date.setDate(QDate.fromString(self.invoice['issue_date'], Qt.DateFormat.ISODate))
        self.due_date.setDate(QDate.fromString(self.invoice['due_date'], Qt.DateFormat.ISODate))
        self.notes.setText(self.invoice.get('notes', ''))
        
        index = self.org_combo.findData(self.invoice['organization_id'])
        if index >= 0:
            self.org_combo.setCurrentIndex(index)
            
        for item in self.invoice['items']:
            self.add_item_row(item)
            