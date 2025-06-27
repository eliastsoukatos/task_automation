import sys
from PyQt5 import QtWidgets, QtCore

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
                self.action_signal.emit(f"Cycle {c+1}: {action}")
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
        name = f"Action {len(self.actions)+1}"
        self.actions.append(name)
        self.list_widget.addItem(name)

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
