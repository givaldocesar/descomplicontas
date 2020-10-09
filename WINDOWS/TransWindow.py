from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QToolButton, QDateEdit, QWidget,
                             QToolBar, QMessageBox)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from .BaseWindow import BaseWindow
from .TREE import Tree, TreeItem
from .DIALOGS import AddTransDialog, AddTransfer
from VARIABLES import Icon, DATABASE

COLUMNS = ['Data', 'Descrição', 'Categoria', 'Conta', 'Valor', '']


class DeleteButton(QToolButton):
    clicked = pyqtSignal(TreeItem)

    def __init__(self, parent=None, treeItem=None):
        super().__init__(parent)
        self.setIcon(Icon('delete.png'))
        self.treeItem = treeItem

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.treeItem)


class TransactionWindow(BaseWindow):
    def __init__(self, mainWindows=None):
        super().__init__(mainWindows, "Transações", 0.25, 0, 0.5, 0.55, "budget.png")
        self.createLayout()

    def addTransaction(self):
        dialog = AddTransDialog(self, "Adicionar Transação: ")
        result = dialog.exec_()
        if result:
            dialog.process(None)

    def addTransfer(self):
        dialog = AddTransfer(self)
        result = dialog.exec_()
        if result:
            dialog.process()
            self.mainWindow.loadInfo()

    def createLayout(self):
        base = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        monthBox = QHBoxLayout()
        self.date = QDateEdit(QDate.currentDate())
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("MMMM yyyy")
        self.date.setAlignment(Qt.AlignCenter)

        def dateChanged():
            msg = "Exibindo transações de %s" % (self.date.date().toString("MM-yyyy"))
            self.mainWindow.showMessage(msg)
            self.mainWindow.loadInfo()

        self.date.dateChanged.connect(dateChanged)

        left = QToolButton()
        left.setArrowType(Qt.LeftArrow)
        left.clicked.connect(lambda: self.date.setDate(self.date.date().addMonths(-1)))

        right = QToolButton()
        right.setArrowType(Qt.RightArrow)
        right.clicked.connect(lambda: self.date.setDate(self.date.date().addMonths(1)))

        monthBox.addStretch(1)
        monthBox.addWidget(left)
        monthBox.addWidget(self.date, 1)
        monthBox.addWidget(right)
        monthBox.addStretch(1)

        self.view = Tree(6)
        self.view.setResizeColumn(2)
        self.view.setColumnWidth(0, 75)
        self.view.setColumnWidth(1, 175)
        self.view.setColumnWidth(2, 200)
        self.view.setColumnWidth(3, 100)
        self.view.setColumnWidth(5, 10)
        self.view.itemDoubleClicked.connect(self.editItem)

        layout.addLayout(monthBox)
        layout.addWidget(self.view, 1)
        base.setLayout(layout)
        self.setWidget(base)
        self.setFocusPolicy(Qt.StrongFocus)

    def createMenusAndToolbar(self):
        add = self.mainWindow.operationsMenu.addAction("Adicionar Transação")
        add.setIcon(Icon("money.png"))
        add.triggered.connect(self.addTransaction)

        addTransfer = self.mainWindow.operationsMenu.addAction("Adicionar Transferência")
        addTransfer.setIcon(Icon("transfer.png"))
        addTransfer.triggered.connect(self.addTransfer)

        delete = self.mainWindow.operationsMenu.addAction("Apagar Transações")
        delete.setIcon(Icon("del-trans.png"))
        delete.triggered.connect(self.deleteItems)

        toolbar = QToolBar("Operações de Transação")
        toolbar.addAction(add)
        toolbar.addAction(addTransfer)
        toolbar.addAction(delete)
        self.mainWindow.addToolBar(toolbar)

    def deleteItem(self, item):
        date = item.parent().data(0, Qt.DisplayRole)
        result = QMessageBox.question(self, "Apagar Transação",
                                      "Deseja realmente apagar a transação:\n\n"+
                                      ">%s\n" % date.toString("dd/MM/yyyy") +
                                      ">%s\n" % item.text(1) +
                                      ">Conta:\t\t%s\n" % item.text(3) +
                                      ">Categoria:\t%s\n" % item.text(2) +
                                      ">Valor:\t\t%s" % item.text(4))
        if result == QMessageBox.Yes:
            DATABASE.delTransaction(item.ident)
            self.mainWindow.showMessage("Transação Apagada.")
            self.mainWindow.loadInfo()

    def deleteItems(self):
        items = self.view.getChecked(0)
        if items:
            result = QMessageBox.question(self, "Apagar Transações",
                                          "Deseja realmente apagar as %d transações selecionadas?"
                                          % len(items))
            if result == QMessageBox.Yes:
                for item in items:
                    DATABASE.delTransaction(item.ident)
                self.mainWindow.showMessage("%d transações Apagadas." % len(items))
                self.mainWindow.loadInfo()

    def editItem(self, item, column, invoice=False):
        if item.parent() or invoice:
            dialog = AddTransDialog(self, "Editar Transação: ", item)
            result = dialog.exec_()
            if result:
                dialog.process(item)

    def loadInfo(self):
        self.view.clear()
        self.view.setHeaderLabels(COLUMNS)
        for item in DATABASE.getTransactions(self.date.date()):
            itemDate = QDate(item[3], item[2], item[1])
            topDate = self.view.getTopItem(itemDate)
            if topDate:
                reg = TreeItem(topDate, '')
            else:
                top = TreeItem(self.view, '')
                top.setData(0, Qt.DisplayRole, itemDate)
                reg = TreeItem(top, '')
            reg.setIdent(item[0])
            reg.setCheckState(0, Qt.Unchecked)
            reg.setText(1, item[4])
            reg.setText(2, item[5])
            reg.setTextAlignment(2, Qt.AlignCenter)
            reg.setText(3, item[7])
            reg.setTextAlignment(3, Qt.AlignCenter)
            reg.setText(4, "R$ %.2f  " % item[8])
            reg.setTextAlignment(4, Qt.AlignRight)
            delBtn = DeleteButton(treeItem=reg)
            delBtn.clicked.connect(self.deleteItem)
            self.view.setItemWidget(reg, 5, delBtn)

            self.view.resizeColumnToContents(0)
            self.view.expandAll()
            self.view.sortItems(0, Qt.DescendingOrder)