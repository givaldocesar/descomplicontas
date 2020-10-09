from PyQt5.QtWidgets import (QDialog, QFormLayout, QGroupBox, QRadioButton, QHBoxLayout,
                             QLineEdit, QDoubleSpinBox, QPushButton, QSpinBox)
from VARIABLES import Icon, BANK, CARD, BROKER, DATABASE


class AddAccount(QDialog):
    def __init__(self, parent=None, title='', item=None):
        super(AddAccount, self).__init__(parent)
        self.setFixedWidth(300)
        self.setWindowTitle(title)
        self.setWindowIcon(Icon('bank.png'))
        self.showMessage = self.parent().mainWindow.showMessage
        self.createLayout(item)

    def createLayout(self, item):
        layout = QFormLayout()

        types = QGroupBox("Tipo", self)
        self.bank = QRadioButton("Banco")
        self.bank.setChecked(True)
        self.card = QRadioButton("Cartão de Crédito")
        self.broker = QRadioButton("Corretora")
        hbox = QHBoxLayout()
        hbox.addWidget(self.bank)
        hbox.addWidget(self.card)
        hbox.addWidget(self.broker)
        types.setLayout(hbox)
        layout.addRow(types)

        self.name = QLineEdit()
        self.name.textChanged.connect(self.enableButton)
        self.name.setMaxLength(20)
        layout.addRow("Nome", self.name)

        self.limit = QDoubleSpinBox()
        self.limit.setPrefix("R$ ")
        self.limit.setDecimals(2)
        self.limit.setSingleStep(100)
        self.limit.setRange(0, 100000000)
        self.broker.toggled.connect(lambda: self.limit.setEnabled(not self.broker.isChecked()))
        layout.addRow("Limite", self.limit)

        self.expiration = QSpinBox()
        self.expiration.setPrefix("Dia ")
        self.expiration.setRange(1, 31)
        self.expiration.setEnabled(False)
        self.card.toggled.connect(lambda: self.expiration.setEnabled(self.card.isChecked()))
        layout.addRow("Vencimento da fatura", self.expiration)

        sublayout = QHBoxLayout()
        self.ok = QPushButton("Adicionar")
        self.ok.clicked.connect(self.accept)
        self.ok.setEnabled(False)
        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(self.reject)
        sublayout.addWidget(self.ok)
        sublayout.addWidget(cancel)
        layout.addRow(sublayout)

        if item:
            self.name.setText(item.text(0))
            account = DATABASE.getAccounts(True, item.text(0))
            self.limit.setValue(account[2])
            if account[1] == BANK:
                self.bank.setChecked(True)
            elif account[1] == CARD:
                self.card.setChecked(True)
            else:
                self.broker.setChecked(True)
            if account[3]:
                self.expiration.setValue(account[3])
            self.ok.setText("Editar")

        self.setLayout(layout)

    def enableButton(self):
        if len(self.name.text()) > 0:
            self.ok.setEnabled(True)
        else:
            self.ok.setEnabled(False)

    def process(self, item):
        account = [self.name.text()]
        if self.bank.isChecked():
            account += [BANK, self.limit.value(), 0]
        elif self.card.isChecked():
            account += [CARD, self.limit.value(), self.expiration.value()]
        else:
            account += [BROKER, "-------", 0]

        if not item:
            msg = DATABASE.addAccount(account)
            self.showMessage(msg)
        else:
            account += [item.text(0)]
            DATABASE.updateAccount(account)
            msg = "Conta %s Atualizada para %s." % (item.text(0), self.name.text())
            self.showMessage(msg)
