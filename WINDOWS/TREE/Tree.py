from PyQt5.QtWidgets import QTreeWidget, QAbstractItemView, QHeaderView
from PyQt5.QtCore import Qt


class Tree(QTreeWidget):
    def __init__(self, columns):
        super().__init__()
        self.setColumnCount(columns)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setUniformRowHeights(True)
        self.header().setDefaultAlignment(Qt.AlignCenter)

    def getChecked(self, column):
        checked = []
        for topItem in self.getTopItems():
            if topItem.checkState(column):
                checked.append(topItem)
            for item in topItem.children():
                if item.checkState(column):
                    checked.append(item)
        return checked

    def getTopItem(self, data):
        for i in range(self.topLevelItemCount()):
            if self.topLevelItem(i).data(0, Qt.DisplayRole) == data:
                return self.topLevelItem(i)
        return None

    def getTopItems(self):
        tops = []
        for i in range(self.topLevelItemCount()):
            tops.append(self.topLevelItem(i))
        return tops

    def setResizeColumn(self, column):
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(column, QHeaderView.Stretch)