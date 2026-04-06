import sys, os, random
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QFileDialog

# --- Theme ---
NEON_GREEN = "#00ff99"
BG_COLOR = "#000000"
FONT_FAMILY = "Segoe UI"

# --- Directory for G-code files ---
MYPRINTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gcode_files")
os.makedirs(MYPRINTS_DIR, exist_ok=True)

# --- Sample G-code modifier function ---
def modify_gcode(file_path, copies, height):
    with open(file_path, "r") as f:
        lines = f.readlines()
    # Dummy modification: append height info
    new_lines = lines + [f";Modified Height: {height}\n"] * copies
    out_path = file_path.replace(".gcode", "_modified.gcode")
    with open(out_path, "w") as f:
        f.writelines(new_lines)
    return out_path

# --- Starry background widget ---
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
            if y>self.height():
                y=0
                x=random.randint(0,self.width())
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

# --- Classic Mode App ---
class ClassicLauncher(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PushTerm Classic Mode")
        self.setFixedSize(900,600)

        # Background
        self.background = StarCanvas()
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.background)

        # Overlay main widget
        self.main_widget = QtWidgets.QWidget(self)
        self.main_widget.setGeometry(self.rect())
        main_layout = QtWidgets.QHBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0,0,0,0)

        # Sidebar
        self.sidebar = QtWidgets.QVBoxLayout()
        self.sidebar.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(self.sidebar, 1)

        self.pages = QtWidgets.QStackedWidget()
        main_layout.addWidget(self.pages, 5)

        self.create_sidebar_buttons()
        self.create_pages()

    # --- Sidebar Buttons ---
    def create_sidebar_buttons(self):
        pages = [
            ("Overview", 0),
            ("Printers", 1),
            ("Queue", 2),
            ("Files", 3),
            ("Print History", 4),
            ("Filament", 5),
            ("Settings", 6)
        ]
        for name, index in pages:
            btn = QtWidgets.QPushButton(name)
            btn.setFixedHeight(50)
            btn.setFont(QtGui.QFont(FONT_FAMILY,14,QtGui.QFont.Weight.Bold))
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
                }}
            """)
            btn.clicked.connect(lambda checked, i=index: self.pages.setCurrentIndex(i))
            self.sidebar.addWidget(btn)
            self.sidebar.addSpacing(10)

    # --- Pages ---
    def create_pages(self):
        # 0 Overview
        overview = QtWidgets.QWidget()
        ov_layout = QtWidgets.QVBoxLayout(overview)
        ov_label = QtWidgets.QLabel("Welcome to PushTerm Classic Mode!")
        ov_label.setFont(QtGui.QFont(FONT_FAMILY,16))
        ov_label.setStyleSheet(f"color:{NEON_GREEN}")
        ov_layout.addWidget(ov_label)
        ov_layout.addStretch()
        self.pages.addWidget(overview)

        # 1 Printers (dummy)
        printers = QtWidgets.QWidget()
        pr_layout = QtWidgets.QVBoxLayout(printers)
        pr_layout.addWidget(QtWidgets.QLabel("No printers configured yet."))
        add_printer_btn = QtWidgets.QPushButton("+ Add Printer (will open popup later)")
        add_printer_btn.setFont(QtGui.QFont(FONT_FAMILY,12))
        pr_layout.addWidget(add_printer_btn)
        pr_layout.addStretch()
        self.pages.addWidget(printers)

        # 2 Queue (dummy)
        queue = QtWidgets.QWidget()
        q_layout = QtWidgets.QVBoxLayout(queue)
        q_layout.addWidget(QtWidgets.QLabel("Queue is empty."))
        self.pages.addWidget(queue)

        # 3 Files
        files = QtWidgets.QWidget()
        f_layout = QtWidgets.QVBoxLayout(files)
        self.file_list = QtWidgets.QListWidget()
        self.file_list.setStyleSheet(f"background-color: {BG_COLOR}; color:{NEON_GREEN}")
        f_layout.addWidget(self.file_list)

        # Drag & drop setup
        self.file_list.setAcceptDrops(True)
        self.file_list.dragEnterEvent = self.dragEnterEvent
        self.file_list.dropEvent = self.dropEvent

        # Copies & Height inputs
        self.copies_input = QtWidgets.QLineEdit("1")
        self.copies_input.setPlaceholderText("Copies")
        self.height_input = QtWidgets.QLineEdit("0")
        self.height_input.setPlaceholderText("Height")
        f_layout.addWidget(self.copies_input)
        f_layout.addWidget(self.height_input)

        # Buttons
        add_queue_btn = QtWidgets.QPushButton("Add to Queue (dummy)")
        add_queue_btn.setFont(QtGui.QFont(FONT_FAMILY,12))
        f_layout.addWidget(add_queue_btn)

        download_btn = QtWidgets.QPushButton("Download Modified G-code")
        download_btn.setFont(QtGui.QFont(FONT_FAMILY,12))
        download_btn.clicked.connect(self.download_modified)
        f_layout.addWidget(download_btn)

        self.pages.addWidget(files)

        # 4 Print History
        history = QtWidgets.QWidget()
        h_layout = QtWidgets.QVBoxLayout(history)
        h_layout.addWidget(QtWidgets.QLabel("No print history yet."))
        self.pages.addWidget(history)

        # 5 Filament
        filament = QtWidgets.QWidget()
        fl_layout = QtWidgets.QVBoxLayout(filament)
        fl_layout.addWidget(QtWidgets.QLabel("Filament tracking not set up yet."))
        self.pages.addWidget(filament)

        # 6 Settings
        settings = QtWidgets.QWidget()
        s_layout = QtWidgets.QVBoxLayout(settings)
        s_layout.addWidget(QtWidgets.QLabel("Settings page placeholder."))
        self.pages.addWidget(settings)

    # --- Drag & Drop ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith(".gcode"):
                fname = os.path.basename(path)
                dest = os.path.join(MYPRINTS_DIR, fname)
                try:
                    with open(path, "rb") as src, open(dest, "wb") as dst:
                        dst.write(src.read())
                    self.file_list.addItem(fname)
                except Exception as e:
                    print("Error copying file:", e)
        event.acceptProposedAction()

    # --- Download Modified G-code ---
    def download_modified(self):
        item = self.file_list.currentItem()
        if not item:
            return
        filename = item.text()
        filepath = os.path.join(MYPRINTS_DIR, filename)
        try:
            copies = int(self.copies_input.text())
            height = float(self.height_input.text())
        except:
            copies = 1
            height = 0
        # modify
        temp_output = modify_gcode(filepath, copies, height)
        # save dialog
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Modified G-code",
                                                   filename.replace(".gcode", "_modified.gcode"),
                                                   "G-code Files (*.gcode)")
        if save_path:
            try:
                with open(temp_output, "rb") as src, open(save_path, "wb") as dst:
                    dst.write(src.read())
            except:
                pass

# --- Run ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    launcher = ClassicLauncher()
    launcher.show()
    sys.exit(app.exec())