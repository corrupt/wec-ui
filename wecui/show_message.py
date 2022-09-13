import tkinter as tk
from tkinter import ttk

class _showMessage(tk.Toplevel):

    def __init__(self, parent, title=None, message=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.title = title
        self.message = message

        self.createUI()
        self.transient(parent)

        self.grab_set()
        self.wait_window(self)


    def btnOkClick(self):
        self.destroy()


    def createUI(self):
        frame1 = ttk.Frame(self)
        frame1.grid()

        label = ttk.Label(
            frame1,
            text = self.message
        )
        label.grid(column=0, row=0, columnspan=2)

        btn_ok = ttk.Button(
            frame1,
            text="ok",
            command=self.btnOkClick
        )
        btn_ok.grid(column=1, row=1)


def showMessage(parent, title, message, **kwargs):
    show = _showMessage(parent, title, message, **kwargs)
