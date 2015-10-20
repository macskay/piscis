# -*- encoding: utf-8 -*-

from tkinter import Tk
from piscis.ui.window import MainWindow, SecondaryWindow

if __name__ == '__main__':
    main_root = Tk()
    main_root.resizable(0, 0)

    main_window = MainWindow(main_root)

    main_root.mainloop()
