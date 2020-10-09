import os
from PyQt5.QtGui import QIcon, QFont, QBrush, QColor
from DATABASE import Database

IMGDIR = os.path.join(os.getcwd(), 'img')
DATABASE = Database()

BANK = 'bank'
CARD = 'card'
BROKER = 'broker'

ACCOUNT = "ACCOUNT"
CATEGORY = "CATEGORY"
TRANSFERS = "Transferências"

BOLD = QFont()
BOLD.setBold(True)

TREASURE = "treasure"
STOCK = "stock"


class Icon(QIcon):
    def __init__(self, name):
        super(Icon, self).__init__(os.path.join(IMGDIR, name))


def changePrefix(dialog):
    if dialog.expense.isChecked():
        dialog.value.setPrefix("R$ - ")
    elif dialog.income.isChecked():
        dialog.value.setPrefix("R$ ")


def defineColor(reg, valor, column):
    if valor < 0:
        reg.setForeground(column, QBrush(QColor(125, 0, 0)))
    elif valor > 0:
        reg.setForeground(column, QBrush(QColor(0, 125, 0)))
    else:
        reg.setForeground(column, QBrush(QColor(0, 0, 0)))
