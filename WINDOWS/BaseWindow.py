from PyQt5.QtWidgets import QApplication, QMdiSubWindow
from VARIABLES import Icon


class BaseWindow(QMdiSubWindow):
    active = True

    def __init__(self, mainWindow=None, title='', x=0, y=0, width=0, height=0, iconPath=''):
        super(BaseWindow, self).__init__()
        self.setWindowTitle(title)
        screen = QApplication.instance().primaryScreen()
        self.setGeometry(screen.size().width() * x,
                         screen.size().height() * y,
                         screen.size().width() * width,
                         screen.size().height() * height)
        self.setWindowIcon(Icon(iconPath))

        self.mainWindow = mainWindow

        self.action = self.mainWindow.windowsMenu.addAction(title)
        self.action.setCheckable(True)
        self.action.setChecked(True)

        def showOrHide():
            if self.active:
                self.hide()
            else:
                self.show()
            self.active = not self.active

        self.action.triggered.connect(showOrHide)

    def closeEvent(self, event):
        self.active = False
        self.action.setChecked(False)

    def createMenusAndToolbar(self):
        pass

    def loadInfo(self):
        pass

