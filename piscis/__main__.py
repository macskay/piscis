# -*- encoding: utf-8 -*-

from tkinter import Tk
from piscis.ui.window import MainWindow, SecondaryWindow
from logging import basicConfig, DEBUG

if __name__ == '__main__':
    basicConfig(level=DEBUG)
    main_root = Tk()
    main_root.resizable(0, 0)

    main_window = MainWindow(main_root)

    main_root.mainloop()
