from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QWidget, QToolBar, QMessageBox)
from PyQt5.QtCore import Qt
from .BaseWindow import BaseWindow
from .TREE import Tree, TreeItem
from .DIALOGS import AddCategory, DeleteDialog
from VARIABLES import BOLD, Icon, DATABASE, defineColor, CATEGORY, TRANSFERS


class CategoriesWindow(BaseWindow):
    def __init__(self, mainWindows=None):
        super().__init__(mainWindows, "Categorias", 0, 0.45, 0.25, 0.37, "category.png")
        self.createLayout()

    def addItem(self):
        dialog = AddCategory(self, "Adicionar Categoria: ")
        result = dialog.exec_()
        if result:
            dialog.process(None)
            self.loadInfo()

    def createLayout(self):
        base = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.view = Tree(2)
        self.view.itemDoubleClicked.connect(self.editItem)
        self.view.setResizeColumn(1)
        layout.addWidget(self.view)

        self.balance = QLabel()
        self.balance.setFont(BOLD)
        self.balance.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.balance)

        base.setLayout(layout)
        self.setWidget(base)

    def createMenusAndToolbar(self):
        add = self.mainWindow.operationsMenu.addAction("Adicionar Categoria")
        add.setIcon(Icon("category.png"))
        add.triggered.connect(self.addItem)

        delete = self.mainWindow.operationsMenu.addAction("Excluir Categorias")
        delete.setIcon(Icon("del-cat.png"))
        delete.triggered.connect(self.deleteItems)

        toolbar = QToolBar("Operações de Categoria")
        toolbar.addAction(add)
        toolbar.addAction(delete)
        self.mainWindow.addToolBar(toolbar)

    def deleteItems(self):
        items = DATABASE.getCategories()
        dialog = DeleteDialog(self, "Deletar Categorias", "del-cat.png",
                              ["Categoria", "Transações", "Filhas", "Trans. Filhas"],
                              items)
        result = dialog.exec_()
        if result:
            dialog.process(_type=CATEGORY)
            self.mainWindow.loadInfo()

    def editItem(self, item, column):
        dialog = AddCategory(self, "Editar Categoria: ", item)
        result = dialog.exec_()
        if result:
            dialog.process(item)
            self.mainWindow.loadInfo()

    def loadInfo(self):
        date = self.mainWindow.transWindow.date.date()
        self.view.clear()
        self.view.setHeaderLabels(['Categoria', 'Gasto em ' + date.toString("MMMM yyyy")])
        for category in DATABASE.getCategoriesParent():
            if category != TRANSFERS:
                item = TreeItem(self.view, category)
                item.setFont(1, BOLD)
                self.formatItem(item)
                for children in DATABASE.getChildrenFrom(category):
                    child = TreeItem(item, children)
                    self.formatItem(child)

        self.view.resizeColumnToContents(0)
        self.view.sortItems(0, Qt.AscendingOrder)

        balance = DATABASE.getMonthlyBalance(date)
        self.balance.setText("Balanço Mensal: R$ %.2f" % balance)
        if balance > 0:
            self.balance.setStyleSheet("QLabel {color:#007E00}")
        elif balance == 0:
            self.balance.setStyleSheet("QLabel {color:#000000}")
        else:
            self.balance.setStyleSheet("QLabel {color:#7E0000}")

    def formatItem(self, item):
        value = DATABASE.getBalanceFromCategory(item.text(0),
                                                self.mainWindow.transWindow.date.date())
        item.setText(1, "R$ %.2f" % value)
        defineColor(item, value, 1)
        item.setTextAlignment(1, Qt.AlignRight)