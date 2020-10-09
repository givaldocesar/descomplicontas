# -*- coding:utf-8 -*-
import os
import pickle
from PyQt5.QtWidgets import (QMainWindow, QDialog, QGridLayout, QLabel, QPushButton,
                             QLineEdit, QProgressBar, QFileDialog, QMdiArea)
from PyQt5.QtCore import Qt, QDateTime
from VARIABLES import Icon, DATABASE
from .TransWindow import TransactionWindow
from .AccWindow import AccountsWindow
from .CatWindow import CategoriesWindow
from .InvestWindow import InvestimentsWindow
from .GraphWindow import GraphWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("De$compliconta$")
        self.setWindowIcon(Icon("main-icon.png"))

        self.area = QMdiArea()
        self.area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.area)

        DATABASE.showInfo()

        self.createMenus()
        self.createWindows()

        self.loadInfo()
        self.showMaximized()
        self.showMessage("Iniciado")

    def closeEvent(self, event):
        DATABASE.close()


    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("Arquivo")
        import_ = self.fileMenu.addAction("Importar Transações")
        import_.triggered.connect(self.importWindow)
        export_ = self.fileMenu.addAction("Exportar Transações")
        export_.triggered.connect(self.exportWindow)
        self.fileMenu.addSeparator()
        close_ = self.fileMenu.addAction("Fechar")
        close_.triggered.connect(self.close)

        self.operationsMenu = self.menuBar().addMenu("Operações")
        self.windowsMenu = self.menuBar().addMenu("Janelas")

    def createWindows(self):
        self.accWindow = AccountsWindow(self)
        self.area.addSubWindow(self.accWindow)
        self.accWindow.show()

        self.catWindow = CategoriesWindow(self)
        self.area.addSubWindow(self.catWindow)
        self.catWindow.show()

        self.transWindow = TransactionWindow(self)
        self.area.addSubWindow(self.transWindow)
        self.transWindow.show()

        self.investWindow = InvestimentsWindow(self)
        self.area.addSubWindow(self.investWindow)
        self.investWindow.show()

        self.graphsWindow = GraphWindow(self)
        self.area.addSubWindow(self.graphsWindow)
        self.graphsWindow.show()

        self.accWindow.createMenusAndToolbar()
        self.operationsMenu.addSeparator()
        self.catWindow.createMenusAndToolbar()
        self.operationsMenu.addSeparator()
        self.transWindow.createMenusAndToolbar()
        self.operationsMenu.addSeparator()
        self.investWindow.createMenusAndToolbar()

    def exportWindow(self):
        self.db.cursor.execute("""SELECT * FROM transactions""")
        result = self.db.cursor.fetchall()
        fileDir = QFileDialog.getSaveFileName(self, "Exportar para: ", os.environ["HOMEPATH"],
                                              "Transações (*.trans)")
        file = open(os.path.join(os.getcwd(), fileDir[0]), 'wb')
        pickle.dump(result, file)
        self.showMessage("%d transações exportadas." % len(result))

    def importWindow(self):
        bar = QProgressBar()
        bar.setTextVisible(True)
        bar.setValue(0)

        fileDir = QLineEdit()
        fileDir.setReadOnly(True)

        start = QPushButton("Importar")

        def importItems():
            try:
                transactions = pickle.load(open(fileDir.text(), "rb"))
                bar.setRange(0, len(transactions))
                count = 0
                for transaction in transactions:
                    self.db.addTransaction(transaction[1:])
                    count += 1
                    bar.setValue(count)
                self.showMessage("%d transações importadas." % len(transactions))
                start.setEnabled(False)
            except:
                self.showMessage("OPS! Algo deu errado.")

        dialog = QDialog(self)
        dialog.setWindowTitle("Importar Transações")
        layout = QGridLayout()
        layout.addWidget(QLabel("Arquivo: "), 0, 0)
        layout.addWidget(fileDir, 0, 1)
        search = QPushButton("...")
        search.clicked.connect(lambda: fileDir.setText(
                                            QFileDialog.getOpenFileName(dialog,
                                                "Importar de: ", os.environ['HOMEPATH'],
                                                "Transações (*.trans)")[0]
                                            )
                               )
        layout.addWidget(search, 0, 2)
        layout.addWidget(QLabel("Progresso: "), 1, 0)
        layout.addWidget(bar, 1, 1, 1, 3)
        start.clicked.connect(importItems)
        layout.addWidget(start, 2, 1)
        dialog.setLayout(layout)
        dialog.exec_()

    def loadInfo(self):
        self.accWindow.loadInfo()
        self.catWindow.loadInfo()
        self.transWindow.loadInfo()
        self.investWindow.loadInfo()
        self.graphsWindow.updatePlot()

    def showMessage(self, text):
        msg = QDateTime.currentDateTime().toString("dd/MM/yyyy hh:mm ")
        msg += text
        print(msg)
        self.statusBar().showMessage(msg)