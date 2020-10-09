from PyQt5.QtWidgets import (QDialog, QFormLayout, QGroupBox, QRadioButton, QHBoxLayout,
                             QDateEdit, QLineEdit, QCompleter, QComboBox, QDoubleSpinBox,
                             QPushButton, QSpinBox, QLabel, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from VARIABLES import Icon, changePrefix, DATABASE


class AddTransDialog(QDialog):
    def __init__(self, parent=None, title='', item=None):
        super(AddTransDialog, self).__init__(parent)
        self.setFixedWidth(300)
        self.setWindowTitle(title)
        self.setWindowIcon(Icon('money.png'))
        self.showMessage = self.parent().mainWindow.showMessage
        self.createLayout(item)

    def createLayout(self, item):
        layout = QFormLayout()

        types = QGroupBox("Tipo", self)
        self.expense = QRadioButton("Despesa")
        self.expense.setChecked(True)
        self.expense.toggled.connect(lambda: changePrefix(self))
        self.income = QRadioButton("Receita")
        self.income.toggled.connect(lambda: changePrefix(self))

        hbox = QHBoxLayout()
        hbox.addWidget(self.expense)
        hbox.addWidget(self.income)
        types.setLayout(hbox)
        layout.addRow(types)

        self.date = QDateEdit()
        self.date.setDate(QDate.currentDate())
        self.date.setCalendarPopup(True)
        self.date.setFocusPolicy(Qt.StrongFocus)
        layout.addRow("Data", self.date)

        self.description = QLineEdit()
        self.description.setMaxLength(40)
        completer = QCompleter(DATABASE.getDescriptions())
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.InlineCompletion)
        self.description.setCompleter(completer)
        layout.addRow("Descrição", self.description)

        self.category = QComboBox()
        self.category.setEditable(True)
        self.category.completer().setCompletionMode(QCompleter.PopupCompletion)
        categories = DATABASE.getCategories()
        if not categories:
            DATABASE.populateCategories()
            categories = DATABASE.getCategories()
        for cat in categories:
            self.category.addItem(cat)
        layout.addRow("Categoria", self.category)

        self.account = QComboBox()
        self.account.setEditable(False)
        accounts = DATABASE.getAccounts()
        for acc in accounts:
            self.account.addItem(acc)
        layout.addRow("Conta", self.account)

        self.value = QDoubleSpinBox()
        self.value.setDecimals(2)
        self.value.setSingleStep(100)
        self.value.setRange(0, 1000000000)
        layout.addRow("Valor", self.value)

        divBox = QHBoxLayout()
        self.initial = QSpinBox()
        self.initial.setRange(1, 1000)
        label = QLabel(" de ")
        label.setAlignment(Qt.AlignCenter)
        self.subdivision = QSpinBox()
        self.subdivision.setRange(1, 1000)
        self.subdivision.setSuffix(" parcelas")
        self.subdivision.setAlignment(Qt.AlignCenter)
        divBox.addWidget(self.initial)
        divBox.addWidget(label)
        divBox.addWidget(self.subdivision)
        layout.addRow("Parcelas", divBox)

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

        if item:
            info = DATABASE.getTransactions(ident=item.ident)
            if info[-1] >= 0:
                self.income.setChecked(True)
                self.value.setPrefix("R$ ")
            else:
                self.expense.setChecked(True)
                self.value.setPrefix("R$ -")
            self.date.setDate(QDate(info[3], info[2], info[1]))
            self.description.setText(info[4])
            idx = self.category.findText(info[5], Qt.MatchExactly)
            self.category.setCurrentIndex(idx)
            idx = self.account.findText(info[7], Qt.MatchExactly)
            self.account.setCurrentIndex(idx)
            self.value.setValue(abs(info[8]))
            self.ok.setText("Editar")
            self.initial.setEnabled(False)
            label.setEnabled(False)
            self.subdivision.setEnabled(False)

        self.setLayout(layout)

    def process(self, item):
        if DATABASE.getCategories(self.category.currentText()):
            self.insertTransaction(item)
            self.parent().mainWindow.loadInfo()
        else:
            message = QMessageBox(QMessageBox.Warning, "Categoria Inexistente",
                                  "Deseja adicionar a categoria %s" % self.category.currentText(),
                                   QMessageBox.Ok | QMessageBox.Cancel)
            resultMsg = message.exec_()
            if resultMsg == QMessageBox.Ok:
                self.insertTransaction(item, True)
                self.parent().mainWindow.loadInfo()

    def insertTransaction(self, item, newCategory=False):
        if self.expense.isChecked():
            value = -self.value.value()
        else:
            value = self.value.value()

        if not item:
            value = value / self.subdivision.value()
            count = 0
            for i in range(self.initial.value(), self.subdivision.value() + 1):
                date = self.date.date().addMonths(count)
                transaction = [date.day(), date.month(), date.year()]
                if self.subdivision.value() > 1:
                    transaction += [self.description.text() + " (%d/%d)" % (i, self.subdivision.value())]
                else:
                    transaction += [self.description.text()]
                if newCategory:
                    transaction += [self.category.currentText(), None]
                else:
                    transaction += [self.category.currentText(),
                                    DATABASE.getCategories(self.category.currentText(), infos=True)[1]]
                transaction += [self.account.currentText(), value]
                DATABASE.addTransaction(transaction)
                self.showMessage("Transação Adicionada.")

                count += 1
        else:
            date = self.date.date()
            transaction = [date.day(), date.month(), date.year()]
            transaction += [self.description.text()]
            if newCategory:
                transaction += [self.category.currentText(), None]
            else:
                transaction += [self.category.currentText(),
                                DATABASE.getCategories(self.category.currentText(), infos=True)[1]]
            transaction += [self.account.currentText(), value, item.ident]
            DATABASE.updateTransaction(transaction)
            self.showMessage("Transação Editada.")



