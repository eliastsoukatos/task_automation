import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import pyautogui

class CoordinatePicker(QtWidgets.QDialog):
    coords = QtCore.pyqtSignal(int, int)

    def __init__(self):
        super().__init__(None, QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self._cover_all_screens()
        self.setWindowOpacity(0.4)
        self.setCursor(QtCore.Qt.CrossCursor)

    def _cover_all_screens(self):
        screens = QtWidgets.QApplication.screens()
        rect = QtCore.QRect()
        for screen in screens:
            rect = rect.united(screen.geometry())
        self.setGeometry(rect)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.coords.emit(event.globalX(), event.globalY())
            self.accept()

class DebugOverlay(QtWidgets.QWidget):
    """Small crosshair overlay to visualize a click position."""

    def __init__(self, x, y, timeout=500):
        super().__init__(
            None,
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.Tool,
        )
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.resize(20, 20)
        self.move(x - 10, y - 10)
        QtCore.QTimer.singleShot(timeout, self.close)
        self.show()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen(QtGui.QColor("red"), 2)
        painter.setPen(pen)
        painter.drawLine(0, 10, 20, 10)
        painter.drawLine(10, 0, 10, 20)

class ActionWorker(QtCore.QThread):
    action_signal = QtCore.pyqtSignal(str)
    debug_click = QtCore.pyqtSignal(int, int)
    finished = QtCore.pyqtSignal()

    def __init__(self, actions, cycles, delay=500):
        super().__init__()
        self.actions = actions
        self.cycles = cycles
        self.delay = delay

    def run(self):
        for c in range(self.cycles):
            for action in self.actions:
                if action["type"] == "click":
                    msg = f"Click at ({action['x']}, {action['y']})"
                else:
                    msg = f"Sleep {action['seconds']}s"
                self.action_signal.emit(f"Cycle {c+1}: {msg}")

                if action["type"] == "click":
                    self.debug_click.emit(action['x'], action['y'])
                    pyautogui.click(x=action['x'], y=action['y'])
                    pos = pyautogui.position()
                    self.action_signal.emit(f"Actual mouse position {pos}")
                else:
                    self.msleep(int(action["seconds"] * 1000))

                self.msleep(self.delay)
        self.finished.emit()

class AutomationWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automation Runner")
        self.resize(400, 300)
        self.actions = []
        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout()

        self.list_widget = QtWidgets.QListWidget()
        layout.addWidget(self.list_widget)

        btn_layout = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Add Action")
        self.edit_btn = QtWidgets.QPushButton("Edit Action")
        self.play_btn = QtWidgets.QPushButton("Play")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.play_btn)
        layout.addLayout(btn_layout)

        cycle_layout = QtWidgets.QHBoxLayout()
        cycle_layout.addWidget(QtWidgets.QLabel("Cycles:"))
        self.cycle_spin = QtWidgets.QSpinBox()
        self.cycle_spin.setMinimum(1)
        self.cycle_spin.setValue(1)
        cycle_layout.addWidget(self.cycle_spin)
        layout.addLayout(cycle_layout)

        self.debug_check = QtWidgets.QCheckBox("Debug")
        layout.addWidget(self.debug_check)

        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.setLayout(layout)

        self.add_btn.clicked.connect(self.add_action)
        self.edit_btn.clicked.connect(self.edit_action)
        self.play_btn.clicked.connect(self.start_automation)

    def _pick_coordinates(self, start_x=None, start_y=None):
        picker = CoordinatePicker()
        coords = {}

        def save_coords(x, y):
            coords['x'] = x
            coords['y'] = y

        picker.coords.connect(save_coords)
        picker.exec_()
        if 'x' not in coords:
            return None

        if self.debug_check.isChecked():
            DebugOverlay(coords['x'], coords['y'])
            self.append_log(
                f"Picked global ({coords['x']}, {coords['y']})"
            )
        return coords['x'], coords['y']

    def add_action(self):
        action_types = ["Click", "Sleep"]
        choice, ok = QtWidgets.QInputDialog.getItem(
            self, "Add Action", "Action Type:", action_types, 0, False)
        if not ok:
            return
        if choice == "Click":
            result = self._pick_coordinates()
            if result is None:
                return
            x, y = result
            action = {"type": "click", "x": x, "y": y}
            label = f"Click ({x}, {y})"
        else:
            secs, ok = QtWidgets.QInputDialog.getDouble(
                self, "Sleep", "Seconds:", 1.0, 0.1, 3600.0, decimals=2)
            if not ok:
                return
            action = {"type": "sleep", "seconds": float(secs)}
            label = f"Sleep {secs:.2f}s"
        self.actions.append(action)
        self.list_widget.addItem(label)

    def edit_action(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Select an action to edit")
            return
        action = self.actions[row]
        if action["type"] == "click":
            result = self._pick_coordinates()
            if result is None:
                return
            x, y = result
            action["x"] = x
            action["y"] = y
            label = f"Click ({x}, {y})"
        else:
            secs, ok = QtWidgets.QInputDialog.getDouble(
                self, "Sleep", "Seconds:", action["seconds"], 0.1, 3600.0, decimals=2)
            if not ok:
                return
            action["seconds"] = float(secs)
            label = f"Sleep {secs:.2f}s"
        self.actions[row] = action
        self.list_widget.item(row).setText(label)

    def append_log(self, text):
        self.log.appendPlainText(text)

    def show_debug_marker(self, x, y):
        if self.debug_check.isChecked():
            DebugOverlay(x, y)

    def start_automation(self):
        if not self.actions:
            QtWidgets.QMessageBox.warning(self, "No Actions", "Add at least one action")
            return
        cycles = self.cycle_spin.value()
        self.play_btn.setEnabled(False)
        self.worker = ActionWorker(self.actions, cycles)
        self.worker.action_signal.connect(self.append_log)
        self.worker.debug_click.connect(self.show_debug_marker)
        self.worker.finished.connect(lambda: self.play_btn.setEnabled(True))
        self.worker.start()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = AutomationWindow()
    win.show()
    sys.exit(app.exec_())
