import sys
from PyQt5 import QtWidgets, QtCore
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

class ActionWorker(QtCore.QThread):
    action_signal = QtCore.pyqtSignal(str)
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
                    pyautogui.click(x=action['x'], y=action['y'])
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
        self.play_btn = QtWidgets.QPushButton("Play")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.play_btn)
        layout.addLayout(btn_layout)

        cycle_layout = QtWidgets.QHBoxLayout()
        cycle_layout.addWidget(QtWidgets.QLabel("Cycles:"))
        self.cycle_spin = QtWidgets.QSpinBox()
        self.cycle_spin.setMinimum(1)
        self.cycle_spin.setValue(1)
        cycle_layout.addWidget(self.cycle_spin)
        layout.addLayout(cycle_layout)

        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.setLayout(layout)

        self.add_btn.clicked.connect(self.add_action)
        self.play_btn.clicked.connect(self.start_automation)

    def add_action(self):
        action_types = ["Click", "Sleep"]
        choice, ok = QtWidgets.QInputDialog.getItem(
            self, "Add Action", "Action Type:", action_types, 0, False)
        if not ok:
            return
        if choice == "Click":
            picker = CoordinatePicker()
            coords = {}

            def save_coords(x, y):
                coords['x'] = x
                coords['y'] = y

            picker.coords.connect(save_coords)
            picker.exec_()
            if 'x' not in coords:
                return

            screen = QtWidgets.QApplication.screenAt(QtCore.QPoint(coords['x'], coords['y']))
            dpr = screen.devicePixelRatio() if screen else 1.0
            phys_x = int(coords['x'] * dpr)
            phys_y = int(coords['y'] * dpr)
            action = {"type": "click", "x": phys_x, "y": phys_y}
            label = f"Click ({coords['x']}, {coords['y']})"
        else:
            secs, ok = QtWidgets.QInputDialog.getDouble(
                self, "Sleep", "Seconds:", 1.0, 0.1, 3600.0, decimals=2)
            if not ok:
                return
            action = {"type": "sleep", "seconds": float(secs)}
            label = f"Sleep {secs:.2f}s"
        self.actions.append(action)
        self.list_widget.addItem(label)

    def append_log(self, text):
        self.log.appendPlainText(text)

    def start_automation(self):
        if not self.actions:
            QtWidgets.QMessageBox.warning(self, "No Actions", "Add at least one action")
            return
        cycles = self.cycle_spin.value()
        self.play_btn.setEnabled(False)
        self.worker = ActionWorker(self.actions, cycles)
        self.worker.action_signal.connect(self.append_log)
        self.worker.finished.connect(lambda: self.play_btn.setEnabled(True))
        self.worker.start()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = AutomationWindow()
    win.show()
    sys.exit(app.exec_())
