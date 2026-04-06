import json
import os
from PyQt6 import QtWidgets, QtGui, QtCore

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRINTERS_JSON = os.path.join(BASE_DIR, "printers.json")
NEON_GREEN = "#00ff99"
BG_COLOR = "#000000"
FONT_FAMILY = "Segoe UI"

def load_printers():
    if not os.path.exists(PRINTERS_JSON):
        with open(PRINTERS_JSON, "w") as f:
            json.dump([], f)
    with open(PRINTERS_JSON, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_printers(printers):
    with open(PRINTERS_JSON, "w") as f:
        json.dump(printers, f, indent=4)

class AddPrinterPopup(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Printer")
        self.setFixedSize(400, 400)
        self.setStyleSheet(f"background-color: {BG_COLOR}; color: {NEON_GREEN};")

        layout = QtWidgets.QFormLayout(self)

        self.name_input = QtWidgets.QLineEdit()
        self.type_input = QtWidgets.QComboBox()
        self.type_input.addItems(["Bambu Lab", "PrusaLink", "OctoPrint", "Moonraker/Clinker"])
        self.ip_input = QtWidgets.QLineEdit()
        self.port_input = QtWidgets.QLineEdit()
        self.api_input = QtWidgets.QLineEdit()

        layout.addRow("Printer Name:", self.name_input)
        layout.addRow("Type:", self.type_input)
        layout.addRow("IP Address:", self.ip_input)
        layout.addRow("Port:", self.port_input)
        layout.addRow("API Key / Password:", self.api_input)

        btn = QtWidgets.QPushButton("Add Printer")
        btn.setFont(QtGui.QFont(FONT_FAMILY, 12, QtGui.QFont.Weight.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                color: {NEON_GREEN};
                background-color: {BG_COLOR};
                border: 2px solid {NEON_GREEN};
                border-radius: 10px;
                height: 40px;
            }}
            QPushButton:hover {{
                background-color: {NEON_GREEN};
                color: {BG_COLOR};
            }}
        """)
        btn.clicked.connect(self.add_printer)
        layout.addWidget(btn)

    def add_printer(self):
        printers = load_printers()
        printers.append({
            "name": self.name_input.text(),
            "type": self.type_input.currentText(),
            "ip": self.ip_input.text(),
            "port": self.port_input.text(),
            "api": self.api_input.text()
        })
        save_printers(printers)
        self.accept()