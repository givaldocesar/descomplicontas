from PyQt5.QtWidgets import (QDialog, QFormLayout, QHBoxLayout, QLineEdit, QPushButton,
                             QComboBox)
from PyQt5.QtCore import Qt
from VARIABLES import Icon, DATABASE


class AddCategory(QDialog):
    def __init__(self, parent=None, title='', item=None):
        super(AddCategory, self).__init__(parent)
        self.setFixedWidth(300)
        self.setWindowTitle(title)
        self.setWindowIcon(Icon('category.png'))
        self.showMessage = self.parent().mainWindow.showMessage
        self.createLayout(item)

    def createLayout(self, item):
        layout = QFormLayout()

        self.name = QLineEdit()
        self.name.textChanged.connect(self.enableButton)
        self.name.setMaxLength(30)
        layout.addRow("Nome", self.name)

        self.parentCat = QComboBox()
        self.parentCat.addItem("")
        parents = DATABASE.getCategories(infos=True)
        for parentCat in parents:
            if not parentCat[1]:
                self.parentCat.addItem(parentCat[0])
        layout.addRow("Categoria Pai", self.parentCat)

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
            parentCat = DATABASE.getCategories(name=item.text(0))[1]
            idx = self.parentCat.findText(parentCat, Qt.MatchExactly)
            self.parentCat.setCurrentIndex(idx)
            if idx == 0:
                self.parentCat.removeItem(self.parentCat.findText(item.text(0), Qt.MatchExactly))
            self.ok.setText("Editar")

        self.setLayout(layout)

    def enableButton(self):
        if len(self.name.text()) > 0:
            self.ok.setEnabled(True)
        else:
            self.ok.setEnabled(False)

    def process(self, item):
        category = [self.name.text(), self.parentCat.currentText()]

        if not item:
            msg = DATABASE.addCategory(category)
            self.showMessage(msg)
        else:
            category += [item.text(0)]
            DATABASE.updateCategory(category)
            msg = "Categoria %s atualizada para %s." % (item.text(0), self.name.text())
            self.showMessage(msg)