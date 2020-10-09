from PyQt5.QtWidgets import (QDialog, QFormLayout, QHBoxLayout, QDateEdit, QLineEdit, QCompleter,
                             QComboBox, QDoubleSpinBox,
                             QPushButton)
from PyQt5.QtCore import Qt, QDate
from VARIABLES import Icon, DATABASE, TRANSFERS


class AddTransfer(QDialog):
    def __init__(self, parent=None):
        super(AddTransfer, self).__init__(parent)
        self.setFixedWidth(300)
        self.setWindowTitle("Adicionar Transferência")
        self.setWindowIcon(Icon('transfer.png'))
        self.statusBar = self.parent().mainWindow.statusBar()
        self.createLayout()

    def createLayout(self):
        layout = QFormLayout()

        self.date = QDateEdit()
        self.date.setDate(QDate.currentDate())
        self.date.setCalendarPopup(True)
        self.date.setFocusPolicy(Qt.StrongFocus)
        layout.addRow("Data", self.date)

        self.description = QLineEdit()
        self.description.setMaxLength(40)
        completer = QCompleter(DATABASE.getDescriptions())
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        self.description.setCompleter(completer)
        layout.addRow("Descrição", self.description)

        self.account1 = QComboBox()
        self.account2 = QComboBox()
        self.account1.setEditable(False)
        self.account2.setEditable(False)
        accounts = DATABASE.getAccounts()
        for item in accounts:
            self.account1.addItem(item)
            self.account2.addItem(item)
        self.account2.setCurrentIndex(1)
        layout.addRow("De", self.account1)
        layout.addRow("Para", self.account2)

        self.value = QDoubleSpinBox()
        self.value.setDecimals(2)
        self.value.setPrefix("R$ ")
        self.value.setSingleStep(100)
        self.value.setRange(0, 1000000000)
        layout.addRow("Valor", self.value)

        sublayout = QHBoxLayout()
        self.ok = QPushButton("Adicionar")
        self.ok.clicked.connect(self.accept)
        if not accounts:
            self.ok.setEnabled(False)

        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(self.reject)

        sublayout.addWidget(self.ok)
        sublayout.addWidget(cancel)
        layout.addRow(sublayout)

        self.setLayout(layout)

    def process(self):
        date = self.date.date()
        transaction = [date.day(), date.month(), date.year()]
        transaction += [self.description.text(), TRANSFERS, None]
        transaction += [self.account1.currentText(), -self.value.value()]
        DATABASE.addTransaction(transaction)
        transaction[6:8] = [self.account2.currentText(), self.value.value()]
        DATABASE.addTransaction(transaction)