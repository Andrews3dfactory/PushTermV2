# Classic_Mode/pushterm_classic_app.py
import sys
import random
from PyQt6 import QtWidgets, QtCore, QtGui

NEON_GREEN = "#00ff99"
BG_COLOR = "#000000"
FONT_FAMILY = "Segoe UI"

# --- Starry Background ---
class StarCanvas(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.stars = [(random.randint(0,600), random.randint(0,500), random.randint(1,3)) for _ in range(120)]
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_stars)
        self.timer.start(50)

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

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor(BG_COLOR))
        painter.setBrush(QtGui.QBrush(QtGui.QColor("white")))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        for x,y,size in self.stars:
            painter.drawEllipse(int(x), int(y), size, size)

# --- Pages ---
class Page(QtWidgets.QWidget):
    def __init__(self, title):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        header = QtWidgets.QLabel(title)
        header.setFont(QtGui.QFont(FONT_FAMILY, 24, QtGui.QFont.Weight.Bold))
        header.setStyleSheet(f"color: {NEON_GREEN};")
        layout.addWidget(header)
        layout.addStretch()
        layout.addWidget(QtWidgets.QLabel(f"{title} content goes here."))

# --- Main App ---
class ClassicModeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PushTerm V2 - Classic Mode")
        self.setFixedSize(1000,700)

        # Central widget
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        main_layout = QtWidgets.QHBoxLayout(central)

        # --- Sidebar ---
        sidebar = QtWidgets.QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(f"background-color: {BG_COLOR}; border-right: 2px solid {NEON_GREEN};")
        sidebar_layout = QtWidgets.QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10,10,10,10)
        sidebar_layout.setSpacing(20)

        # Pages
        self.pages = {
            "Printers": Page("Printers"),
            "Queue": Page("Queue"),
            "Files": Page("G-Code Files"),
            "Print History": Page("Print History"),
            "Filaments": Page("Filaments"),
            "Read Me": Page("Read Me"),
            "Settings": Page("Settings"),
        }

        # Stack to show pages
        self.stack = QtWidgets.QStackedWidget()
        for page in self.pages.values():
            self.stack.addWidget(page)

        # --- Sidebar buttons ---
        for idx, (name, page) in enumerate(self.pages.items()):
            btn = QtWidgets.QPushButton(name)
            btn.setFont(QtGui.QFont(FONT_FAMILY, 14, QtGui.QFont.Weight.Bold))
            btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    color: {NEON_GREEN};
                    background-color: {BG_COLOR};
                    border: 2px solid {NEON_GREEN};
                    border-radius: 5px;
                    padding: 10px;
                }}
                QPushButton:hover {{
                    background-color: {NEON_GREEN};
                    color: {BG_COLOR};
                }}
            """)
            btn.clicked.connect(lambda checked, i=idx: self.stack.setCurrentIndex(i))
            sidebar_layout.addWidget(btn)
        sidebar_layout.addStretch()

        # --- Star background behind main area ---
        background_frame = QtWidgets.QFrame()
        background_layout = QtWidgets.QVBoxLayout(background_frame)
        self.background = StarCanvas()
        background_layout.addWidget(self.background)
        # Overlay stack of pages
        self.page_container = QtWidgets.QStackedLayout()
        for page in self.pages.values():
            self.page_container.addWidget(page)
        background_layout.addLayout(self.page_container)

        # Use stacked layout so clicking sidebar switches page
        main_layout.addWidget(sidebar)
        main_layout.addWidget(background_frame)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ClassicModeApp()
    window.show()
    sys.exit(app.exec())