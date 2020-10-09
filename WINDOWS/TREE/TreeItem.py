from PyQt5.QtWidgets import QTreeWidgetItem


class TreeItem(QTreeWidgetItem):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.setText(0, text)
        self.ident = None

    def children(self):
        children = []
        for i in range(self.childCount()):
            children.append(self.child(i))
        return children

    def setIdent(self, value):
        self.ident = value