#-*- encoding: utf-8 -*-

from tkinter import Tk
from piscis.ui.window import MainWindow

if __name__ == '__main__':
    root = Tk()
    root.resizable(0, 0)
    window = MainWindow(root)
    window.run()
