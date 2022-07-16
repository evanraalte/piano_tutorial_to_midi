from dataclasses import dataclass
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore


class PanelWidget(QtWidgets.QWidget):
    button_next: QtWidgets.QPushButton = None

    def reset_view(self):
        pass

    def create_view(self):
        pass


@dataclass
class PanelConstructor:
    widget: type[PanelWidget] = PanelWidget
    description: str = "No description"
    button_next_text: str = "next"


class Panel(QtWidgets.QFrame):
    signal_button_next_clicked = QtCore.Signal()

    def reset_view(self):
        self.button_next.setEnabled(False)
        self.widget.reset_view()

    def create_view(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.description = QtWidgets.QLabel(self.constructor.description)
        self.description.setMaximumWidth(400)
        self.description.setWordWrap(True)
        self.layout.addWidget(self.description)

        self.widget = self.constructor.widget()
        self.layout.addWidget(self.widget)
        self.button_next = QtWidgets.QPushButton(self.constructor.button_next_text)
        self.button_next.released.connect(self.signal_button_next_clicked)
        self.widget.button_next = self.button_next
        self.layout.addWidget(self.button_next)
        self.setLayout(self.layout)
        self.setFrameStyle(QtWidgets.QFrame.Box)

    def __init__(self, constructor: PanelConstructor):
        super(Panel, self).__init__()
        self.constructor = constructor
        self.create_view()
