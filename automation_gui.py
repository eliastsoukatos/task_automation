import sys
import os
import json
from PyQt5 import QtWidgets, QtCore, QtGui
import pyautogui


class CycleManager:
    """Handle saving and loading of action cycles."""

    FILE = "cycles.json"

    def __init__(self):
        self.cycles = []
        self.load()

    def load(self):
        if os.path.exists(self.FILE):
            try:
                with open(self.FILE, "r", encoding="utf-8") as fh:
                    self.cycles = json.load(fh)
            except (OSError, json.JSONDecodeError):
                self.cycles = []

    def save(self):
        try:
            with open(self.FILE, "w", encoding="utf-8") as fh:
                json.dump(self.cycles, fh, indent=2)
        except OSError:
            pass

    def add_cycle(self, name, actions):
        self.cycles.append({"name": name, "actions": actions})
        self.save()

    def delete_cycle(self, index):
        if 0 <= index < len(self.cycles):
            self.cycles.pop(index)
            self.save()

    def rename_cycle(self, index, new_name):
        if 0 <= index < len(self.cycles):
            self.cycles[index]["name"] = new_name
            self.save()


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
        self.resize(600, 400)
        self.actions = []
        self.cycle_manager = CycleManager()
        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout()

        action_btns = QtWidgets.QHBoxLayout()
        self.add_click_btn = QtWidgets.QPushButton("Add Click")
        self.add_sleep_btn = QtWidgets.QPushButton("Add Sleep")
        action_btns.addWidget(self.add_click_btn)
        action_btns.addWidget(self.add_sleep_btn)
        layout.addLayout(action_btns)

        auto_sleep_layout = QtWidgets.QHBoxLayout()
        self.auto_sleep_check = QtWidgets.QCheckBox("Automatic Sleep")
        self.auto_sleep_spin = QtWidgets.QDoubleSpinBox()
        self.auto_sleep_spin.setDecimals(2)
        self.auto_sleep_spin.setRange(0.1, 3600.0)
        self.auto_sleep_spin.setValue(0.5)
        self.auto_sleep_spin.setVisible(False)
        auto_sleep_layout.addWidget(self.auto_sleep_check)
        auto_sleep_layout.addWidget(self.auto_sleep_spin)
        layout.addLayout(auto_sleep_layout)

        lists_layout = QtWidgets.QHBoxLayout()
        left_layout = QtWidgets.QVBoxLayout()
        right_layout = QtWidgets.QVBoxLayout()

        self.list_widget = QtWidgets.QListWidget()
        left_layout.addWidget(self.list_widget)

        edit_layout = QtWidgets.QHBoxLayout()
        self.edit_btn = QtWidgets.QPushButton("Edit Action")
        self.save_cycle_btn = QtWidgets.QPushButton("Save Cycle")
        self.play_btn = QtWidgets.QPushButton("Play")
        edit_layout.addWidget(self.edit_btn)
        edit_layout.addWidget(self.save_cycle_btn)
        edit_layout.addWidget(self.play_btn)
        left_layout.addLayout(edit_layout)

        lists_layout.addLayout(left_layout)

        right_layout.addWidget(QtWidgets.QLabel("Saved Cycles"))
        self.cycle_list = QtWidgets.QListWidget()
        right_layout.addWidget(self.cycle_list)
        cycle_btns = QtWidgets.QHBoxLayout()
        self.insert_cycle_btn = QtWidgets.QPushButton("Insert")
        self.rename_cycle_btn = QtWidgets.QPushButton("Rename")
        self.delete_cycle_btn = QtWidgets.QPushButton("Delete")
        cycle_btns.addWidget(self.insert_cycle_btn)
        cycle_btns.addWidget(self.rename_cycle_btn)
        cycle_btns.addWidget(self.delete_cycle_btn)
        right_layout.addLayout(cycle_btns)

        lists_layout.addLayout(right_layout)

        layout.addLayout(lists_layout)

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

        self.add_click_btn.clicked.connect(self.add_click)
        self.add_sleep_btn.clicked.connect(self.add_sleep)
        self.auto_sleep_check.toggled.connect(self.auto_sleep_spin.setVisible)
        self.edit_btn.clicked.connect(self.edit_action)
        self.save_cycle_btn.clicked.connect(self.save_cycle)
        self.insert_cycle_btn.clicked.connect(self.insert_cycle)
        self.rename_cycle_btn.clicked.connect(self.rename_cycle)
        self.delete_cycle_btn.clicked.connect(self.delete_cycle)
        self.play_btn.clicked.connect(self.start_automation)

        self._refresh_cycle_list()


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

    def _add_action(self, action):
        if action["type"] == "click":
            label = f"Click ({action['x']}, {action['y']})"
        else:
            label = f"Sleep {action['seconds']:.2f}s"
        self.actions.append(action)
        self.list_widget.addItem(label)

    def add_click(self):
        result = self._pick_coordinates()
        if result is None:
            return
        x, y = result
        self._add_action({"type": "click", "x": x, "y": y})

        if self.auto_sleep_check.isChecked():
            self._add_action({"type": "sleep", "seconds": float(self.auto_sleep_spin.value())})

    def add_sleep(self):
        secs, ok = QtWidgets.QInputDialog.getDouble(
            self, "Sleep", "Seconds:", 1.0, 0.1, 3600.0, decimals=2)
        if not ok:
            return
        self._add_action({"type": "sleep", "seconds": float(secs)})

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

    def save_cycle(self):
        if not self.actions:
            QtWidgets.QMessageBox.warning(self, "Empty", "No actions to save")
            return
        name, ok = QtWidgets.QInputDialog.getText(self, "Save Cycle", "Name:")
        if not ok or not name.strip():
            return
        # store a deep copy
        actions_copy = [dict(a) for a in self.actions]
        self.cycle_manager.add_cycle(name.strip(), actions_copy)
        self._refresh_cycle_list()

    def insert_cycle(self):
        row = self.cycle_list.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Select a cycle")
            return
        cycle = self.cycle_manager.cycles[row]
        for action in cycle["actions"]:
            self._add_action(dict(action))

    def delete_cycle(self):
        row = self.cycle_list.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Select a cycle")
            return
        if QtWidgets.QMessageBox.question(
            self,
            "Delete",
            "Delete selected cycle?",
        ) == QtWidgets.QMessageBox.Yes:
            self.cycle_manager.delete_cycle(row)
            self._refresh_cycle_list()

    def rename_cycle(self):
        row = self.cycle_list.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Select a cycle")
            return
        name, ok = QtWidgets.QInputDialog.getText(
            self, "Rename Cycle", "New name:", text=self.cycle_manager.cycles[row]["name"]
        )
        if not ok or not name.strip():
            return
        self.cycle_manager.rename_cycle(row, name.strip())
        self._refresh_cycle_list()

    def _refresh_cycle_list(self):
        self.cycle_list.clear()
        for cycle in self.cycle_manager.cycles:
            self.cycle_list.addItem(cycle["name"]) 

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
