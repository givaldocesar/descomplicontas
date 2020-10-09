# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import (QDialog, QFormLayout, QComboBox, QDateEdit, QLabel,
                             QHBoxLayout, QToolButton)
from PyQt5.QtCore import Qt, QDate
from VARIABLES import DATABASE, Icon, defineColor
from ..TREE import TreeItem, Tree


class Invoice(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(600, 650)
        self.setWindowTitle("Ver Fatura\Extrato: ")
        self.setWindowIcon(Icon('fatura.png'))

        layout = QFormLayout()
        self.account = QComboBox()
        accounts = DATABASE.getAccounts()
        for account in accounts:
            self.account.addItem(account)
        self.account.activated.connect(self.attPeriod)
        layout.addRow("Conta", self.account)

        self.period1 = QDateEdit()
        self.period1.setCalendarPopup(True)
        label = QLabel(" a ")
        label.setAlignment(Qt.AlignCenter)
        self.period2 = QDateEdit()
        self.period2.setCalendarPopup(True)
        dateLayout = QHBoxLayout()
        dateLayout.addWidget(self.period1, 1)
        dateLayout.addWidget(label)
        dateLayout.addWidget(self.period2, 1)
        layout.addRow("Periodo", dateLayout)

        infoBox = QHBoxLayout()
        infos = QFormLayout()
        self.accountView = QLabel()
        self.totalValue = QLabel()
        self.date1 = QLabel()
        label2 = QLabel(" a ")
        label2.setAlignment(Qt.AlignCenter)
        self.date2 = QLabel()
        dateLayout2 = QHBoxLayout()
        dateLayout2.addWidget(self.date1, 1)
        dateLayout2.addWidget(label2)
        dateLayout2.addWidget(self.date2, 1)
        infos.addRow("Conta", self.accountView)
        infos.addRow("Período ", dateLayout2)
        infos.addRow("Total", self.totalValue)
        infoBox.addLayout(infos)

        left = QToolButton()
        left.setArrowType(Qt.LeftArrow)
        left.clicked.connect(self.previousMonth)
        right = QToolButton()
        right.setArrowType(Qt.RightArrow)
        right.clicked.connect(self.nextMonth)
        infoBox.addWidget(left)
        infoBox.addWidget(right)
        infoBox.addStretch(1)
        layout.addRow(infoBox)

        self.table = Tree(4)
        self.table.setHeaderLabels(['Data', 'Descrição', 'Categoria', 'Valor'])
        self.table.setResizeColumn(2)
        self.table.itemDoubleClicked.connect(self.editItem)
        self.table.itemClicked.connect(self.alterSum)
        layout.addRow(self.table)

        self.attPeriod(0)
        self.period1.dateChanged.connect(self.showTable)
        self.period2.dateChanged.connect(self.showTable)
        self.setLayout(layout)

    def alterSum(self, item, column):
        if column == 1:
            suma = 0
            for itemTree in self.table.getChecked(1):
                if itemTree.checkState(1):
                    suma += float(itemTree.text(4)[3:])
            self.totalValue.setText("R$ %.2f" % suma)

    def attPeriod(self, index):
        info = DATABASE.getAccounts(name=self.account.itemText(index), info=True)
        currentDate = QDate.currentDate()
        if info[3]:
            currentDate.setDate(currentDate.year(), currentDate.month() - 1, info[3] + 1)
            self.period1.setDate(currentDate.addDays(-10))
            self.period2.setDate(currentDate.addMonths(1).addDays(-11))
            self.showTable()
        else:
            currentDate.setDate(currentDate.year(), currentDate.month(), 1)
            self.period1.setDate(currentDate)
            self.period2.setDate(QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth()))
            self.showTable(inverse=True)

    def editItem(self, item, column):
        self.parent().mainWindow.transWindow.editItem(item, column, invoice=True)
        self.showTable()

    def nextMonth(self):
        self.period1.setDate(self.period1.date().addMonths(1))
        self.period2.setDate(self.period2.date().addMonths(1))

    def previousMonth(self):
        self.period1.setDate(self.period1.date().addMonths(-1))
        self.period2.setDate(self.period2.date().addMonths(-1))

    def showTable(self, inverse=False):
        self.table.clear()
        self.table.setHeaderLabels(["#",'Data', 'Descrição', 'Categoria', 'Valor'])
        self.accountView.setText(self.account.currentText())
        self.date1.setText(self.period1.date().toString("dd/MM/yyyy"))
        self.date2.setText(self.period2.date().toString("dd/MM/yyyy"))
        transactions = DATABASE.getTransactionsFrom(self.period1.date(),
                                                    self.period2.date(),
                                                    self.account.currentText())
        suma = 0
        count = 1
        for trans in transactions:
            row = TreeItem(self.table, '')
            row.setIdent(trans[0])
            row.setData(0, Qt.DisplayRole, count)
            row.setData(1, Qt.DisplayRole, QDate(trans[3], trans[2], trans[1]), )
            row.setCheckState(1, Qt.Checked)
            row.setText(2, trans[4])
            row.setText(3, trans[5])
            if inverse:
                row.setText(4, "R$ %.2f" % trans[8])
                suma += trans[8]
            else:
                row.setText(4, "R$ %.2f" % -trans[8])
                suma -= trans[8]
            if trans[8] > 0:
                defineColor(row, trans[8], 2)
            count += 1

        self.totalValue.setText("R$ %.2f" % suma)
        self.table.resizeColumnToContents(0)