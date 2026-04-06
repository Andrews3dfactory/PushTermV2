import sys, os, random
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QFileDialog, QListWidgetItem

from gcode_utils import modify_gcode, parse_delay_input  # Fixed import

NEON_GREEN = "#00ff99"
BG_COLOR = "#000000"
FONT_FAMILY = "Segoe UI"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MYPRINTS_DIR = os.path.join(BASE_DIR, "gcode_files")
os.makedirs(MYPRINTS_DIR, exist_ok=True)


class StarCanvas(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.stars = [
            (random.randint(0, 600), random.randint(0, 500), random.randint(1, 3))
            for _ in range(120)
        ]
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_stars)
        self.timer.start(50)
        self.setMinimumSize(600, 500)

    def update_stars(self):
        new_stars = []
        for x, y, size in self.stars:
            y += 0.3 + random.random() * 0.3
            if y > self.height():
                y = 0
                x = random.randint(0, self.width())
            new_stars.append((x, y, size))
        self.stars = new_stars
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor(BG_COLOR))
        painter.setBrush(QtGui.QBrush(QtGui.QColor("white")))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        for x, y, size in self.stars:
            painter.drawEllipse(int(x), int(y), size, size)


class QueueItemWidget(QtWidgets.QWidget):
    def __init__(self, filename: str, launcher: "ClassicLauncher"):
        super().__init__()
        self.launcher = launcher
        self.filename = filename
        self.output_path = None

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)

        self.name_label = QtWidgets.QLabel(filename)
        self.name_label.setFont(QtGui.QFont(FONT_FAMILY, 11))
        self.name_label.setStyleSheet(f"color: {NEON_GREEN};")
        layout.addWidget(self.name_label, 3)

        self.status_label = QtWidgets.QLabel("Queued")
        self.status_label.setFont(QtGui.QFont(FONT_FAMILY, 10))
        self.status_label.setStyleSheet(f"color: {NEON_GREEN};")
        layout.addWidget(self.status_label, 2)

        def style_btn(btn):
            btn.setFixedHeight(28)
            btn.setFont(QtGui.QFont(FONT_FAMILY, 10, QtGui.QFont.Weight.Bold))
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    color: {NEON_GREEN};
                    background-color: {BG_COLOR};
                    border: 1px solid {NEON_GREEN};
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    background-color: {NEON_GREEN};
                    color: {BG_COLOR};
                }}
            """
            )

        self.start_btn = QtWidgets.QPushButton("Start")
        self.pause_btn = QtWidgets.QPushButton("Pause")
        self.remove_btn = QtWidgets.QPushButton("Remove")
        self.download_btn = QtWidgets.QPushButton("Download")

        for b in (self.start_btn, self.pause_btn, self.remove_btn, self.download_btn):
            style_btn(b)
            layout.addWidget(b)

        self.start_btn.clicked.connect(self.on_start)
        self.pause_btn.clicked.connect(self.on_pause)
        self.remove_btn.clicked.connect(self.on_remove)
        self.download_btn.clicked.connect(self.on_download)

    def on_start(self):
        self.launcher.start_job(self)

    def on_pause(self):
        self.launcher.pause_job(self)

    def on_remove(self):
        self.launcher.remove_job(self)

    def on_download(self):
        if not self.output_path or not os.path.exists(self.output_path):
            QtWidgets.QMessageBox.warning(
                self, "No G-code", "No modified G-code available yet. Start the job first."
            )
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Modified G-code",
            os.path.basename(self.output_path),
            "G-code Files (*.gcode)",
        )
        if save_path:
            try:
                with open(self.output_path, "rb") as src, open(save_path, "wb") as dst:
                    dst.write(src.read())
                QtWidgets.QMessageBox.information(self, "Saved", f"Saved to {save_path}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")


class ClassicLauncher(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PushTerm Classic Mode")
        self.setFixedSize(900, 600)

        self.background = StarCanvas()
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.background)

        self.main_widget = QtWidgets.QWidget(self)
        self.main_widget.setGeometry(self.rect())
        main_layout = QtWidgets.QHBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = QtWidgets.QVBoxLayout()
        self.sidebar.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(self.sidebar, 1)

        self.pages = QtWidgets.QStackedWidget()
        main_layout.addWidget(self.pages, 5)

        self.create_sidebar_buttons()
        self.create_pages()
        self.load_existing_files()

    def create_sidebar_buttons(self):
        pages = [
            ("Overview", 0),
            #("Printers", 1),
            ("Queue", 2),
            ("Files", 3),
            #("Print History", 4),
            #("Filament", 5),
            #("Settings", 6),
        ]
        for name, index in pages:
            btn = QtWidgets.QPushButton(name)
            btn.setFixedHeight(50)
            btn.setFont(QtGui.QFont(FONT_FAMILY, 14, QtGui.QFont.Weight.Bold))
            btn.setStyleSheet(
                f"""
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
            """
            )
            btn.clicked.connect(lambda checked, i=index: self.pages.setCurrentIndex(i))
            self.sidebar.addWidget(btn)
            self.sidebar.addSpacing(10)

    def create_pages(self):
        overview = QtWidgets.QWidget()
        ov_layout = QtWidgets.QVBoxLayout(overview)
        ov_label = QtWidgets.QLabel("Welcome to PushTerm Classic Mode!")
        ov_label.setFont(QtGui.QFont(FONT_FAMILY, 16))
        ov_label.setStyleSheet(f"color:{NEON_GREEN}")
        ov_layout.addWidget(ov_label)
        ov_layout.addStretch()
        self.pages.addWidget(overview)

        printers = QtWidgets.QWidget()
        pr_layout = QtWidgets.QVBoxLayout(printers)
        pr_label = QtWidgets.QLabel("No printers configured yet.")
        pr_label.setStyleSheet(f"color:{NEON_GREEN}")
        pr_layout.addWidget(pr_label)
        add_printer_btn = QtWidgets.QPushButton("+ Add Printer (coming soon)")
        add_printer_btn.setFont(QtGui.QFont(FONT_FAMILY, 12))
        pr_layout.addWidget(add_printer_btn)
        pr_layout.addStretch()
        self.pages.addWidget(printers)

        queue = QtWidgets.QWidget()
        q_layout = QtWidgets.QVBoxLayout(queue)
        q_layout.setContentsMargins(10, 10, 10, 10)
        q_layout.setSpacing(8)

        q_label = QtWidgets.QLabel("Print Queue")
        q_label.setFont(QtGui.QFont(FONT_FAMILY, 14, QtGui.QFont.Weight.Bold))
        q_label.setStyleSheet(f"color:{NEON_GREEN}")
        q_layout.addWidget(q_label)

        self.queue_list = QtWidgets.QListWidget()
        self.queue_list.setStyleSheet(
            f"""
            QListWidget {{
                background-color: {BG_COLOR};
                color: {NEON_GREEN};
                border: 1px solid {NEON_GREEN};
                border-radius: 8px;
            }}
        """
        )
        q_layout.addWidget(self.queue_list)
        self.pages.addWidget(queue)

        files = QtWidgets.QWidget()
        f_layout = QtWidgets.QVBoxLayout(files)
        f_layout.setContentsMargins(10, 10, 10, 10)
        f_layout.setSpacing(8)

        files_label = QtWidgets.QLabel("G-code Files")
        files_label.setFont(QtGui.QFont(FONT_FAMILY, 14, QtGui.QFont.Weight.Bold))
        files_label.setStyleSheet(f"color:{NEON_GREEN}")
        f_layout.addWidget(files_label)

        upload_btn = QtWidgets.QPushButton("Upload G-code File")
        upload_btn.setFont(QtGui.QFont(FONT_FAMILY, 12))
        upload_btn.setStyleSheet(
            f"""
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
        """
        )
        upload_btn.clicked.connect(self.upload_gcode_file)
        f_layout.addWidget(upload_btn)

        self.file_list = QtWidgets.QListWidget()
        self.file_list.setStyleSheet(
            f"background-color: {BG_COLOR}; color:{NEON_GREEN}; "
            f"border: 1px solid {NEON_GREEN}; border-radius: 8px;"
        )
        f_layout.addWidget(self.file_list)

        self.file_list.setAcceptDrops(True)
        self.file_list.dragEnterEvent = self.dragEnterEvent
        self.file_list.dropEvent = self.dropEvent

        delay_label = QtWidgets.QLabel("Delay (m5, s30, m1s15):")
        delay_label.setStyleSheet(f"color:{NEON_GREEN}")
        f_layout.addWidget(delay_label)

        self.delay_input = QtWidgets.QLineEdit("m0")
        self.delay_input.setStyleSheet(
            f"background-color:{BG_COLOR}; color:{NEON_GREEN}; "
            f"border:1px solid {NEON_GREEN}; border-radius:6px;"
        )
        f_layout.addWidget(self.delay_input)

        copies_label = QtWidgets.QLabel("Copies:")
        copies_label.setStyleSheet(f"color:{NEON_GREEN}")
        f_layout.addWidget(copies_label)

        self.copies_input = QtWidgets.QLineEdit("1")
        self.copies_input.setStyleSheet(
            f"background-color:{BG_COLOR}; color:{NEON_GREEN}; "
            f"border:1px solid {NEON_GREEN}; border-radius:6px;"
        )
        f_layout.addWidget(self.copies_input)

        height_label = QtWidgets.QLabel("Object Height (mm):")
        height_label.setStyleSheet(f"color:{NEON_GREEN}")
        f_layout.addWidget(height_label)

        self.height_input = QtWidgets.QLineEdit("0")
        self.height_input.setStyleSheet(
            f"background-color:{BG_COLOR}; color:{NEON_GREEN}; "
            f"border:1px solid {NEON_GREEN}; border-radius:6px;"
        )
        f_layout.addWidget(self.height_input)

        add_queue_btn = QtWidgets.QPushButton("Add to Queue")
        add_queue_btn.setFont(QtGui.QFont(FONT_FAMILY, 12))
        add_queue_btn.setStyleSheet(
            f"""
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
        """
        )
        add_queue_btn.clicked.connect(self.add_selected_to_queue)
        f_layout.addWidget(add_queue_btn)

        download_btn = QtWidgets.QPushButton("Download Modified G-code")
        download_btn.setFont(QtGui.QFont(FONT_FAMILY, 12))
        download_btn.setStyleSheet(
            f"""
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
        """
        )
        download_btn.clicked.connect(self.download_modified)
        f_layout.addWidget(download_btn)

        self.pages.addWidget(files)

        history = QtWidgets.QWidget()
        h_layout = QtWidgets.QVBoxLayout(history)
        h_label = QtWidgets.QLabel("No print history yet.")
        h_label.setStyleSheet(f"color:{NEON_GREEN}")
        h_layout.addWidget(h_label)
        self.pages.addWidget(history)

        filament = QtWidgets.QWidget()
        fl_layout = QtWidgets.QVBoxLayout(filament)
        fl_label = QtWidgets.QLabel("Filament tracking not set up yet.")
        fl_label.setStyleSheet(f"color:{NEON_GREEN}")
        fl_layout.addWidget(fl_label)
        self.pages.addWidget(filament)

        settings = QtWidgets.QWidget()
        s_layout = QtWidgets.QVBoxLayout(settings)
        s_label = QtWidgets.QLabel("Settings page placeholder.")
        s_label.setStyleSheet(f"color:{NEON_GREEN}")
        s_layout.addWidget(s_label)
        self.pages.addWidget(settings)

    def load_existing_files(self):
        try:
            for fname in os.listdir(MYPRINTS_DIR):
                if fname.lower().endswith(".gcode"):
                    self.file_list.addItem(fname)
        except Exception as e:
            print("Error loading existing files:", e)

    def upload_gcode_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select G-code File",
            "",
            "G-code Files (*.gcode)",
        )

        if not file_path:
            return

        fname = os.path.basename(file_path)
        dest = os.path.join(MYPRINTS_DIR, fname)

        try:
            with open(file_path, "rb") as src, open(dest, "wb") as dst:
                dst.write(src.read())
            self.file_list.addItem(fname)
        except Exception as e:
            print("Upload error:", e)

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

    def add_selected_to_queue(self):
        item = self.file_list.currentItem()
        if not item:
            return
        filename = item.text()
        self.add_to_queue(filename)
        self.pages.setCurrentIndex(2)

    def add_to_queue(self, filename: str):
        widget = QueueItemWidget(filename, self)
        list_item = QListWidgetItem(self.queue_list)
        list_item.setSizeHint(widget.sizeHint())
        self.queue_list.addItem(list_item)
        self.queue_list.setItemWidget(list_item, widget)

    def start_job(self, item_widget: QueueItemWidget):
        filepath = os.path.join(MYPRINTS_DIR, item_widget.filename)

        delay_str = self.delay_input.text().strip()
        try:
            copies = int(self.copies_input.text())
        except ValueError:
            copies = 1
        try:
            height = float(self.height_input.text())
        except ValueError:
            height = 0.0

        try:
            delay_min, delay_sec = parse_delay_input(delay_str)
            success = modify_gcode(filepath, delay_min, delay_sec, copies, height)

            output_path = os.path.splitext(filepath)[0] + "_modified.gcode"

            if success and os.path.exists(output_path):
                item_widget.output_path = output_path
                item_widget.status_label.setText("G-code Ready")
            else:
                item_widget.status_label.setText("Error")
        except Exception as e:
            print("Error in start_job:", e)
            item_widget.status_label.setText("Error")

    def pause_job(self, item_widget: QueueItemWidget):
        item_widget.status_label.setText("Paused")

    def remove_job(self, item_widget: QueueItemWidget):
        for i in range(self.queue_list.count()):
            item = self.queue_list.item(i)
            w = self.queue_list.itemWidget(item)
            if w is item_widget:
                self.queue_list.takeItem(i)
                break

    def download_modified(self):
        item = self.file_list.currentItem()
        if not item:
            QtWidgets.QMessageBox.warning(
                self, "No file selected", "Please select a G-code file first."
            )
            return

        filename = item.text()
        filepath = os.path.join(MYPRINTS_DIR, filename)

        delay_str = self.delay_input.text().strip()
        try:
            copies = int(self.copies_input.text())
        except ValueError:
            copies = 1
        try:
            height = float(self.height_input.text())
        except ValueError:
            height = 0.0

        try:
            delay_min, delay_sec = parse_delay_input(delay_str)
            success = modify_gcode(filepath, delay_min, delay_sec, copies, height)
            if not success:
                QtWidgets.QMessageBox.critical(self, "Error", "G-code modification failed.")
                return
            modified_path = os.path.splitext(filepath)[0] + "_modified.gcode"
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"G-code modification failed:\n{e}")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Modified G-code",
            os.path.basename(modified_path),
            "G-code Files (*.gcode)",
        )
        if save_path:
            try:
                with open(modified_path, "rb") as src, open(save_path, "wb") as dst:
                    dst.write(src.read())
                QtWidgets.QMessageBox.information(self, "Saved", f"Saved to {save_path}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    launcher = ClassicLauncher()
    launcher.show()
    sys.exit(app.exec())