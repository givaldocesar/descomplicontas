from PyQt5.QtWidgets import (QDialog, QFormLayout, QGroupBox, QRadioButton, QHBoxLayout,
                             QLineEdit, QDoubleSpinBox, QPushButton, QSpinBox, QComboBox)
from PyQt5.QtCore import Qt
from VARIABLES import Icon, DATABASE, TREASURE, STOCK


class AddInvestiments(QDialog):
    def __init__(self, parent=None, title='', item=None):
        super(AddInvestiments, self).__init__(parent)
        self.setFixedWidth(300)
        self.setWindowTitle(title)
        self.setWindowIcon(Icon("cash.png"))
        self.showMessage = self.parent().mainWindow.showMessage
        self.createLayout(item)

    def createLayout(self, item):
        layout = QFormLayout()

        types = QGroupBox("Tipo", self)
        self.treasure = QRadioButton("Tesouro Direto")
        self.treasure.setChecked(True)
        self.stock = QRadioButton("Ações")
        hbox = QHBoxLayout()
        hbox.addWidget(self.treasure)
        hbox.addWidget(self.stock)
        types.setLayout(hbox)
        layout.addRow(types)

        self.name = QLineEdit()
        self.name.textChanged.connect(self.enableButton)
        self.name.setMaxLength(30)
        layout.addRow("Nome", self.name)

        self.qtd = QSpinBox()
        self.qtd.setSuffix(" papéis")
        self.qtd.setRange(1, 100000000)
        self.qtd.setEnabled(False)
        self.treasure.toggled.connect(lambda: self.qtd.setEnabled(not self.treasure.isChecked()))
        layout.addRow("Quantidade", self.qtd)

        self.unit = QDoubleSpinBox()
        self.unit.setPrefix("R$ ")
        self.unit.setDecimals(2)
        self.unit.setSingleStep(25)
        self.unit.setRange(0, 100000000)
        layout.addRow("Valor Unitário", self.unit)

        self.broker = QComboBox()
        brokers = DATABASE.getBrokers()
        self.broker.addItems(brokers)
        layout.addRow("Corretora", self.broker)

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
            info = DATABASE.getInvestiments(name=item.text(0))
            if info[2] == TREASURE:
                self.treasure.setChecked(True)
            else:
                self.stock.setChecked(True)
            self.name.setText(info[0])
            self.qtd.setValue(info[1])
            self.unit.setValue(info[3])
            idx = self.broker.findText(info[4], Qt.MatchExactly)
            self.broker.setCurrentIndex(idx)
            self.ok.setText("Editar")
        self.setLayout(layout)

    def enableButton(self):
        if len(self.name.text()) > 0 and self.broker.count() > 0:
            self.ok.setEnabled(True)
        else:
            self.ok.setEnabled(False)

    def process(self, item):
        investiment = [self.name.text()]
        if self.treasure.isChecked():
            investiment += [1, TREASURE]
        else:
            investiment += [self.qtd.value(), STOCK]
        investiment += [self.unit.value(), self.broker.currentText()]

        if not item:
            msg = DATABASE.addInvestiment(investiment)
            self.showMessage(msg)
        else:
            investiment += [item.text(0)]
            DATABASE.updateInvestiment(investiment)
            msg = "Investimento %s Atualizada para %s." % (item.text(0), self.name.text())
            self.showMessage(msg)