import tkinter as tk
from tkinter import ttk

class _askString(tk.Toplevel):

    def __init__(self, parent, title=None, question=None, defaultText='', **kwargs):
        super().__init__(parent, **kwargs)

        self.textvar = tk.StringVar()
        self.textvar.set(defaultText)
        self.ret = None

        self.title = title
        self.question = question

        self.createUI()
        self.transient(parent)

        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)


    def btnCancelClick(self):
        self.ret = None
        self.destroy()


    def btnOkClick(self):
        self.ret = self.textvar.get()
        self.destroy()


    def createUI(self):

        frame1 = ttk.Frame(self)
        frame1.grid(padx="10", pady="10", ipadx="10", ipady="10")

        label = ttk.Label(
            frame1,
            text=self.question
        ).grid(column=0, row=0, sticky=tk.EW)

        entry = ttk.Entry(
            frame1,
            textvariable = self.textvar
        ).grid(column=0, row=1, sticky=tk.EW )

        frame2 = ttk.Frame(frame1)
        frame2.grid(column=0,row=2, padx="10", pady="10", ipadx="10", ipady="10")

        btn_cancel = ttk.Button(
            frame2,
            text="abbrechen",
            command = self.btnCancelClick,
        )
        btn_cancel.pack(expand=True, side=tk.LEFT)

        btn_ok = ttk.Button(
            frame2,
            text="ok",
            command = self.btnOkClick
        )
        btn_ok.pack(expand=True, side=tk.LEFT)


def askString(parent, title, question, defaultText='', **kwargs):
    ask = _askString(parent, title, question, defaultText, **kwargs)
    return ask.ret