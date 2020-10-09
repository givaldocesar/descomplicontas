import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QToolButton, QDateEdit, QWidget,
                             QToolBar, QMessageBox)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from .BaseWindow import BaseWindow
from VARIABLES import Icon, DATABASE


class Canvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(Canvas, self).__init__(fig)


class GraphWindow(BaseWindow):
    def __init__(self, mainWindow=None):
        super().__init__(mainWindow, "Balanço x Dia", 0.25, 0.55, 0.5, 0.27, "graph.png")
        self.createLayout()

    def createLayout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = Canvas(layout, width=5, height=5, dpi=75)
        layout.addWidget(self.canvas)

        base = QWidget()
        base.setLayout(layout)
        self.setWidget(base)

    def updatePlot(self):
        self.canvas.axes.cla()
        date = self.mainWindow.transWindow.date.date()
        x = range(0, date.daysInMonth() + 1)
        previewBalance = DATABASE.getBalanceTo(QDate(date.addMonths(-1).year(),
                                                     date.addMonths(-1).month(),
                                                     date.addMonths(-1).daysInMonth()
                                                     ))
        y = [previewBalance]
        for i in range(1, len(x)):
            dayBalance = previewBalance + DATABASE.getBalanceFromDay(QDate(date.year(), date.month(), i))
            y += [previewBalance + DATABASE.getBalanceFromDay(QDate(date.year(), date.month(), i))]
            previewBalance = dayBalance

        self.canvas.axes.plot(x, y)
        self.canvas.draw()