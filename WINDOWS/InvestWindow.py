from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget,
                             QToolBar, QWidget, QMessageBox)
from PyQt5.QtCore import Qt
from .BaseWindow import BaseWindow
from .TREE import Tree, TreeItem
from .DIALOGS import AddInvestiments
from VARIABLES import BOLD, Icon, DATABASE,  TREASURE, STOCK

COLUMNSTREASURE = ['Nome', 'Valor Atual']
COLUMNSSTOCK = ['Nome', 'Qtd.', 'Unidade', 'Total']


class InvestimentsWindow(BaseWindow):
    def __init__(self, mainWindows=None):
        super().__init__(mainWindows, "Investimentos", 0.75, 0, 0.25, 0.55, "cash.png")
        self.createLayout()

    def addItem(self):
        dialog = AddInvestiments(self, "Adicionar Investimento: ")
        result = dialog.exec_()
        if result:
            dialog.process(None)
            self.mainWindow.loadInfo()

    def createLayout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget(self)
        tabs.setMovable(True)

        self.viewTreasure = Tree(2)
        self.viewTreasure.itemDoubleClicked.connect(self.editItem)
        self.viewTreasure.setResizeColumn(1)
        tabs.addTab(self.viewTreasure, "Tesouro Direto")

        self.viewStocks = Tree(4)
        self.viewStocks.itemDoubleClicked.connect(self.editItem)
        self.viewStocks.setResizeColumn(1)
        self.viewStocks.setColumnWidth(1, 40)
        self.viewStocks.setColumnWidth(2, 80)
        self.viewStocks.setColumnWidth(3, 85)
        tabs.addTab(self.viewStocks, "Ações")

        layout.addWidget(tabs)

        subLayout = QHBoxLayout()
        subLayout.setContentsMargins(0, 0, 0, 0)
        self.updateBtn = QPushButton()
        self.updateBtn.setIcon(Icon("refresh.png"))
        self.updateBtn.clicked.connect(self.updateStocks)
        subLayout.addStretch(1)
        subLayout.addWidget(self.updateBtn)
        layout.addLayout(subLayout)

        base = QWidget()
        base.setLayout(layout)
        self.setWidget(base)

    def createMenusAndToolbar(self):
        add = self.mainWindow.operationsMenu.addAction("Adicionar Investimento")
        add.setIcon(Icon("cash.png"))
        add.triggered.connect(self.addItem)

        delete = self.mainWindow.operationsMenu.addAction("Apagar Investimentos")
        delete.setIcon(Icon("del-invest.png"))
        delete.triggered.connect(self.deleteItems)

        toolbar = QToolBar("Operações de Investimentos")
        toolbar.addAction(add)
        toolbar.addAction(delete)
        self.mainWindow.addToolBar(toolbar)

    def deleteItems(self):
        items = self.viewTreasure.getChecked(0)
        items += self.viewStocks.getChecked(0)
        if items:
            result = QMessageBox.question(self, "Apagar Invetimentos",
                                          "Deseja realmente apagar os %d investimentos selecionados?"
                                          % len(items))
            if result == QMessageBox.Yes:
                for item in items:
                    DATABASE.delInvestiments(item.text(0))
                self.mainWindow.showMessage("%d investimentos Apagados." % len(items))
                self.mainWindow.loadInfo()

    def editItem(self, item, column):
        dialog = AddInvestiments(self, "Editar Investimento: ", item)
        result = dialog.exec_()
        if result:
            dialog.process(item)
            self.mainWindow.loadInfo()

    def loadInfo(self):
        brokers = DATABASE.getBrokers()

        self.viewTreasure.clear()
        self.viewTreasure.setHeaderLabels(COLUMNSTREASURE)

        self.viewStocks.clear()
        self.viewStocks.setHeaderLabels(COLUMNSSTOCK)

        for broker in brokers:
            treasureItem = TreeItem(self.viewTreasure, broker)
            treasureItem.setFont(0, BOLD)
            treasureItem.setText(1, "R$ %.2f" % DATABASE.getBalanceFromBroker(broker, TREASURE))
            treasureItem.setTextAlignment(1, Qt.AlignRight)
            stockItem = TreeItem(self.viewStocks, broker)
            stockItem.setFont(0, BOLD)
            stockItem.setText(3, "R$ %.2f" % DATABASE.getBalanceFromBroker(broker, STOCK))
            stockItem.setTextAlignment(3, Qt.AlignRight)
            investiments = DATABASE.getInvestiments(broker)
            for investiment in investiments:
                if investiment[2] == TREASURE:
                    item = TreeItem(treasureItem, investiment[0])
                    item.setCheckState(0, Qt.Unchecked)
                    item.setText(1, "R$ %.2f" % investiment[3])
                    item.setTextAlignment(1, Qt.AlignRight)
                elif investiment[2] == STOCK:
                    item = TreeItem(stockItem, investiment[0])
                    item.setCheckState(0, Qt.Unchecked)
                    item.setText(1, "%d" % investiment[1])
                    item.setTextAlignment(1, Qt.AlignCenter)
                    item.setText(2, "R$ %.2f" % investiment[3])
                    item.setTextAlignment(2, Qt.AlignRight)
                    item.setText(3, "R$ %.2f" % (investiment[1] * investiment[3]))
                    item.setTextAlignment(3, Qt.AlignRight)

        self.viewTreasure.expandAll()
        self.viewTreasure.resizeColumnToContents(0)
        self.viewTreasure.sortItems(0, Qt.AscendingOrder)

        self.viewStocks.expandAll()
        self.viewStocks.resizeColumnToContents(0)
        self.viewStocks.sortItems(0, Qt.AscendingOrder)

    def updateStocks(self):
        pass