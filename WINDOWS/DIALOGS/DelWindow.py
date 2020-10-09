from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QVariant
from VARIABLES import Icon
from ..TREE import Tree, TreeItem
from VARIABLES import DATABASE, CATEGORY, ACCOUNT


class DeleteDialog(QDialog):
    def __init__(self, parent, title, iconPath, headers, items):
        super().__init__(parent)
        self.setFixedWidth(400)
        self.setWindowTitle(title)
        self.setWindowIcon(Icon(iconPath))
        self.showMessage = self.parent().mainWindow.showMessage
        self.createLayout(headers, items)

    def createLayout(self, headers, items):
        layout = QVBoxLayout()

        self.view = Tree(len(headers))
        self.view.setResizeColumn(0)
        self.view.setColumnWidth(1, 75)
        self.view.setColumnWidth(2, 45)
        self.view.setColumnWidth(3, 75)
        self.view.setHeaderLabels(headers)
        for aux in items:
            item = TreeItem(self.view, aux)
            item.setCheckState(0, Qt.Unchecked)
            item.emitDataChanged()
            for i in range(1, len(headers)):
                item.setData(i, Qt.CheckStateRole, QVariant())

        def activateItem(item, column):
            if column == 0:
                for j in range(1, len(headers)):
                    if item.checkState(0):
                        item.setData(j, Qt.CheckStateRole, Qt.Unchecked)
                    else:
                        item.setData(j, Qt.CheckStateRole, QVariant())

        self.view.itemChanged.connect(activateItem)
        layout.addWidget(self.view)

        sublayout = QHBoxLayout()
        self.ok = QPushButton("Apagar")
        self.ok.clicked.connect(self.accept)
        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(self.reject)
        sublayout.addWidget(self.ok)
        sublayout.addWidget(cancel)
        layout.addLayout(sublayout)

        self.setLayout(layout)

    def process(self, _type=None):
        checkedItems = self.view.getChecked(0)
        if _type == CATEGORY:
            for category in checkedItems:
                msg = "Categoria %s Apagada. " % category.text(0)
                if category.checkState(1):
                    DATABASE.delCategories(category.text(0), transaction=True)
                    msg += "\n\t\t Suas transações também foram apagadas."

                if category.checkState(2):
                    DATABASE.delCategories(category.text(0), children=True)
                    msg += "\n\t\t Suas categorias filhas também foram apagadas"
                else:
                    DATABASE.promoveChildrenFrom(category.text(0))

                if category.checkState(3):
                    DATABASE.delCategories(category.text(0), transChildren=True)
                    msg += "\n\t\t As transações de suas categorias filhas também foram apagadas."

                DATABASE.delCategories(category.text(0))
                self.showMessage(msg)
        elif _type == ACCOUNT:
            for account in checkedItems:
                if account.checkState(1):
                    DATABASE.delAccounts(account.text(0), True)
                    self.showMessage("Conta %s e suas transações foram apagadas." % account.text(0))
                else:
                    DATABASE.delAccounts(account.text(0))
                    self.showMessage("Conta %s foi apagada." % account.text(0))





