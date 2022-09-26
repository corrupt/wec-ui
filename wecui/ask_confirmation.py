import tkinter as tk
from tkinter import ttk

#from wecui.l10n import _

class _askConfirmation(tk.Toplevel):

    def __init__(self, parent, title=None, question=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.ret = None

        self.title = title
        self.question = question

        self.createUI()
        self.transient(parent)

        self.grab_set()
        self.wait_window(self)


    def btnCancelClick(self):
        self.ret = False
        self.destroy()


    def btnOkClick(self):
        self.ret = True
        self.destroy()


    def createUI(self):

        frame1 = ttk.Frame(self)
        frame1.grid(padx="10", pady="10", ipadx="10", ipady="10")

        label = ttk.Label(
            frame1,
            text=self.question
        ).grid(column=0, row=0, sticky=tk.EW)

        frame2 = ttk.Frame(frame1)
        frame2.grid(column=0,row=2, padx="10", pady="10", ipadx="10", ipady="10")

        btn_cancel = ttk.Button(
            frame2,
            text=_("abbrechen"),
            command = self.btnCancelClick,
        )
        btn_cancel.pack(expand=True, side=tk.LEFT)

        btn_ok = ttk.Button(
            frame2,
            text=_("ok"),
            command = self.btnOkClick
        )
        btn_ok.pack(expand=True, side=tk.LEFT)


def askConfirmation(parent, title, question, **kwargs):
    ask = _askConfirmation(parent, title, question, **kwargs)
    return ask.ret