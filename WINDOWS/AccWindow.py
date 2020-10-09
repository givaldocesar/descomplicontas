from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QWidget, QToolBar)
from PyQt5.QtCore import Qt
from .BaseWindow import BaseWindow
from .TREE import Tree, TreeItem
from .DIALOGS import AddAccount, DeleteDialog, Invoice
from VARIABLES import BOLD, Icon, DATABASE, BANK, CARD, BROKER, defineColor, ACCOUNT

COLUMNS = ['Instituição', 'Saldo', 'Limite Disponível']


class AccountsWindow(BaseWindow):
    def __init__(self, mainWindows=None):
        super().__init__(mainWindows, "Contas", 0, 0, 0.25, 0.45, "piggy-bank.png")
        self.createLayout()

    def addItem(self):
        dialog = AddAccount(self, "Adicionar Conta: ")
        result = dialog.exec_()
        if result:
            dialog.process(None)
            self.loadInfo()

    def createLayout(self):
        base = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.view = Tree(3)
        self.view.setColumnWidth(1, 75)
        self.view.setResizeColumn(1)
        self.view.itemDoubleClicked.connect(self.editItem)
        layout.addWidget(self.view)

        self.balance = QLabel()
        self.balance.setFont(BOLD)
        self.balance.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.balance)

        base.setLayout(layout)
        self.setWidget(base)

    def createMenusAndToolbar(self):
        add = self.mainWindow.operationsMenu.addAction("Adicionar Conta")
        add.setIcon(Icon("bank.png"))
        add.triggered.connect(self.addItem)

        invoice = self.mainWindow.operationsMenu.addAction("Ver Fatura/Extrato")
        invoice.setIcon(Icon("fatura.png"))
        invoice.triggered.connect(self.showInvoice)

        delete = self.mainWindow.operationsMenu.addAction("Excluir Contas")
        delete.setIcon(Icon("del-inst.png"))
        delete.triggered.connect(self.deleteItems)

        toolbar = QToolBar("Operações de Conta")
        toolbar.addAction(add)
        toolbar.addAction(invoice)
        toolbar.addAction(delete)
        self.mainWindow.addToolBar(toolbar)

    def deleteItems(self):
        items = DATABASE.getAccounts()
        dialog = DeleteDialog(self, "Deletar Contas", "del-inst.png",
                              ["Conta", "Transações"],
                              items)
        result = dialog.exec_()
        if result:
            dialog.process(_type=ACCOUNT)
            self.mainWindow.loadInfo()

    def editItem(self, item, column):
        if item.parent():
            dialog = AddAccount(self, "Editar Conta: ", item)
            result = dialog.exec_()
            if result:
                dialog.process(item)
                self.mainWindow.loadInfo()

    def loadInfo(self):
        self.view.clear()
        self.view.setHeaderLabels(COLUMNS)

        banks = TreeItem(self.view, "Bancos")
        banks.setFont(1, BOLD)
        banks.setTextAlignment(1, Qt.AlignRight)
        banks.setFont(2, BOLD)
        banks.setTextAlignment(2, Qt.AlignRight)
        cards = TreeItem(self.view, u"Cartões de Crédito")
        cards.setFont(1, BOLD)
        cards.setTextAlignment(1, Qt.AlignRight)
        cards.setFont(2, BOLD)
        cards.setTextAlignment(2, Qt.AlignRight)
        brokers = TreeItem(self.view, "Corretoras")
        brokers.setFont(1, BOLD)
        brokers.setTextAlignment(1, Qt.AlignRight)

        accounts = DATABASE.getAccounts(info=True)
        for account in accounts:
            balance = DATABASE.getBalance(account[0])
            if account[1] == BANK:
                item = TreeItem(banks, account[0])
                if balance >= 0:
                    item.setText(2, "R$ %.2f" % account[2])
                else:
                    item.setText(2, "R$ %.2f" % (account[2] + balance))
                item.setText(1, "R$ %.2f" % balance)
                defineColor(item, balance, 1)

            elif account[1] == CARD:
                item = TreeItem(cards, account[0])
                item.setText(2, "R$ %.2f" % (account[2] + balance))
                item.setText(1, "R$ %.2f" % balance)
                defineColor(item, balance, 1)
            else:
                item = TreeItem(brokers, account[0])
                item.setText(1, "R$ %.2f" % (balance + DATABASE.getBalanceFromBroker(account[0])))
                defineColor(item, balance + DATABASE.getBalanceFromBroker(account[0]), 1)
            item.setTextAlignment(1, Qt.AlignRight)
            item.setTextAlignment(2, Qt.AlignRight)

        value = DATABASE.getBalance(_type=BANK)
        banks.setText(1, "R$ %.2f" % value)
        defineColor(banks, value, 1)
        accounts = DATABASE.getAccounts(info=True)
        limitDisp = 0
        for account in accounts:
            balance = DATABASE.getBalance(account[0])
            if account[1] == BANK and balance < 0:
                limitDisp += account[2] + balance
            elif account[1] == BANK:
                limitDisp += account[2]
        banks.setText(2, "R$ %.2f" % limitDisp)

        value = DATABASE.getBalance(_type=CARD)
        cards.setText(1, "R$ %.2f" % value)
        defineColor(cards, value, 1)
        limitDisp = 0
        for account in accounts:
            balance = DATABASE.getBalance(account[0])
            if account[1] == CARD:
                limitDisp += account[2] + balance
        cards.setText(2, "R$ %.2f" % limitDisp)

        brokers.setText(1, "R$ %.2f" % (DATABASE.getBalance(_type=BROKER) +
                                        DATABASE.getBalanceFromBroker()))
        defineColor(brokers,
                    DATABASE.getBalance(_type=BROKER) + DATABASE.getBalanceFromBroker(),
                    1)

        balance = DATABASE.getBalance() + DATABASE.getBalanceFromBroker()
        self.balance.setText("Balanço Total: R$ %.2f" % balance)
        if balance > 0:
            self.balance.setStyleSheet("QLabel {color:#007E00}")
        elif balance == 0:
            self.balance.setStyleSheet("QLabel {color:#000000}")
        else:
            self.balance.setStyleSheet("QLabel {color:#7E0000}")

        self.view.expandAll()
        self.view.resizeColumnToContents(0)
        self.view.sortItems(0, Qt.AscendingOrder)

    def showInvoice(self):
        dialog = Invoice(self)
        dialog.show()