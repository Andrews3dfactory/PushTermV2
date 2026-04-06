import sys
import subprocess
import random
from PyQt6 import QtWidgets, QtCore, QtGui
import os

NEON_GREEN = "#00ff99"
BG_COLOR = "#000000"
FONT_FAMILY = "Segoe UI"

# --- Paths to your organized folders ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLASSIC_PATH = os.path.join(BASE_DIR, "Classic_Mode", "launcher.py")       # Classic Mode entry
COMMAND_PATH = os.path.join(BASE_DIR, "Command_Mode", "Pushterm_Terminal_Ui.py")        # Command Mode entry

class Launcher(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PushTerm V2 Launcher")
        self.setFixedSize(600,500)

        # --- Starry Background ---
        self.background = StarCanvas()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.background)

        self.overlay = QtWidgets.QWidget(self)
        self.overlay.setGeometry(self.rect())
        overlay_layout = QtWidgets.QVBoxLayout(self.overlay)
        overlay_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        header = QtWidgets.QLabel("PushTerm V2")
        header.setFont(QtGui.QFont(FONT_FAMILY,28,QtGui.QFont.Weight.Bold))
        header.setStyleSheet(f"color: {NEON_GREEN};")
        header.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(header)
        overlay_layout.addSpacing(30)

        # Buttons
        self.add_neon_button(overlay_layout,"Classic Mode",self.launch_classic)
        self.add_neon_button(overlay_layout,"Command Mode",self.launch_command)
        self.add_neon_button(overlay_layout,"Pro Mode (Coming Soon)",None,disabled=True)

    def add_neon_button(self,layout,text,callback=None,disabled=False):
        btn = QtWidgets.QPushButton(text)
        btn.setFont(QtGui.QFont(FONT_FAMILY,14,QtGui.QFont.Weight.Bold))
        btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(50)
        btn.setStyleSheet(f"""
            QPushButton {{
                color: {NEON_GREEN};
                background-color: {BG_COLOR};
                border: 2px solid {NEON_GREEN};
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: {NEON_GREEN};
                color: {BG_COLOR};
                border: 2px solid {NEON_GREEN};
            }}
            QPushButton:disabled {{
                color: #555555;
                border: 2px solid #555555;
                background-color: {BG_COLOR};
            }}
        """)
        if callback:
            btn.clicked.connect(callback)
        btn.setDisabled(disabled)
        layout.addWidget(btn)
        layout.addSpacing(15)

    # --- Launchers ---
    def launch_classic(self):
        if os.path.exists(CLASSIC_PATH):
            try:
                subprocess.Popen([sys.executable, CLASSIC_PATH])
                self.close()  # Close launcher
            except Exception as e:
                QtWidgets.QMessageBox.critical(None, "Launch Failed", str(e))
        else:
            QtWidgets.QMessageBox.warning(None, "File Missing", f"Classic Mode main file not found:\n{CLASSIC_PATH}")

    def launch_command(self):
        if os.path.exists(COMMAND_PATH):
            try:
                subprocess.Popen([sys.executable, COMMAND_PATH])
                self.close()  # Close launcher
            except Exception as e:
                QtWidgets.QMessageBox.critical(None, "Launch Failed", str(e))
        else:
            QtWidgets.QMessageBox.warning(None, "File Missing", f"Command Mode launcher file not found:\n{COMMAND_PATH}")

# --- Star Canvas ---
class StarCanvas(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.stars = [(random.randint(0,600), random.randint(0,500), random.randint(1,3)) for _ in range(120)]
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_stars)
        self.timer.start(50)
        self.setMinimumSize(600,500)

    def update_stars(self):
        new_stars = []
        for x,y,size in self.stars:
            y += 0.3 + random.random()*0.3
            if y > self.height():
                y = 0
                x = random.randint(0,self.width())
            new_stars.append((x,y,size))
        self.stars = new_stars
        self.update()

    def paintEvent(self,event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor(BG_COLOR))
        painter.setBrush(QtGui.QBrush(QtGui.QColor("white")))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        for x,y,size in self.stars:
            painter.drawEllipse(int(x),int(y),size,size)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    launcher = Launcher()
    launcher.show()
    sys.exit(app.exec())
