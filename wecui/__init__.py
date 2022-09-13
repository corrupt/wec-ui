
import tkinter as tk
import json
from tkinter import ttk
from datetime import datetime
from os.path import join

from wecui.utils import *

from wecui.ask_string import askString
from wecui.show_message import showMessage
from wecui.run_wec import start_wec, start_chromium

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('WEC remote')

        self.project = None

        self.url = tk.StringVar()
        self.projectTitle = tk.StringVar()
        self.visitpages = tk.StringVar()
        self.profile = tk.StringVar()

        self.createUI()
        self.disableProfileControls()
        self.updateProjects()
        self.treeview.bind('<<TreeviewSelect>>', self.treeviewItemSelected)
        self.combobox.bind('<<ComboboxSelected>>', self.comboboxItemSelected)


    def newProject(self, project):
        if project is not None:
            newProject(project)
            self.updateProjects()


    def newProfile(self, profile, project):
        if False == newProfile(profile, project):
            showMessage(
                self,
                "Kann Profil nicht erstellen",
                "Ein Profil mit diesem Namen existiert bereits"
            )


    def copyProfile(self, profile, project):
        check = False
        while not check:
            newProfile = askString(
                self,
                "Profil Kopieren",
                "Name des neuen Profils:",
                profile
            )
            if newProfile is None:
                return
            check = copyProfile(profile, newProfile, self.project)
            if not check:
                showMessage(
                    self,
                    "Profil existiert bereits",
                    "Ein Profil mit diesem Namen existiert bereits"
                )


    def delProject(self, project=None):
        return


    def updateProjects(self):
        for i in self.treeview.get_children():
            self.treeview.delete(i)

        projects = getProjectList()
        for (path, name) in projects:
            self.treeview.insert('', tk.END, text=name, values=[name], tags=[path])
        children = self.treeview.get_children()
        if children:
            self.treeview.focus(children[0])
            self.treeview.selection_set(children[0])
            self.treeview.focus_set()


    def updateProfiles(self, project=None):
        if project is None:
            project = self.project
        profiles = list(map(filename2Profile, getProfiles(project)))
        if len(profiles) > 0:
            self.combobox['values'] = tuple(profiles)
            self.combobox.current(0)
            self.comboboxItemSelected(None)
            self.enableProfileControls()
        else:
            self.profile.set('')
            self.comboboxItemSelected(None)
            self.disableProfileControls()


    def treeviewItemSelected(self, event):
        for item in self.treeview.selection():
            self.project = self.treeview.item(item)['text']
            self.updateProfiles(self.project)
            profiles = getProfiles(self.project)
            self.enableProfileControls(len(profiles) > 0)
            self.comboboxItemSelected(None)


    def comboboxItemSelected(self, event):
        self.clearWidgets()
        profile = openProfile(self.project, self.profile.get())
        if profile is not None:
            self.url.set(profile['url'])
            self.projectTitle.set(profile['title'])
            self.visitpages.set(profile['visitpages'])
            self.txt_mustvisit.insert('1.0', "\n".join(profile['mustvisit']))


    def clearWidgets(self):
        self.txt_mustvisit.delete('1.0', tk.END)
        self.url.set('')
        self.projectTitle.set('')
        self.visitpages.set('')


    def disableProfileControls(self):
        self.combobox['state'] = tk.DISABLED
        self.btn_add_profile['state'] = tk.DISABLED
        self.btn_copy_profile['state'] = tk.DISABLED
        self.btn_save_profile['state'] = tk.DISABLED
        self.btn_delete_profile['state'] = tk.DISABLED
        self.lbl_title['state'] = tk.DISABLED
        self.txt_title['state'] = tk.DISABLED
        self.lbl_url['state'] = tk.DISABLED
        self.txt_url['state'] = tk.DISABLED
        self.lbl_visitpages['state'] = tk.DISABLED
        self.spn_visitpages['state'] = tk.DISABLED
        self.lbl_mustvisit['state'] = tk.DISABLED
        self.txt_mustvisit['state'] = tk.DISABLED
        self.btn_start['state'] = tk.DISABLED


    def enableProfileControls(self, profile_present=False):
        if (profile_present):
            self.combobox['state'] = 'readonly'

            self.btn_save_profile['state'] = tk.NORMAL
            self.btn_copy_profile['state'] = tk.NORMAL
            self.btn_save_profile['state'] = tk.NORMAL
            self.btn_delete_profile['state'] = tk.NORMAL
            self.lbl_title['state'] = tk.NORMAL
            self.txt_title['state'] = tk.NORMAL
            self.lbl_url['state'] = tk.NORMAL
            self.txt_url['state'] = tk.NORMAL
            self.lbl_visitpages['state'] = tk.NORMAL
            self.spn_visitpages['state'] = tk.NORMAL
            self.lbl_mustvisit['state'] = tk.NORMAL
            self.txt_mustvisit['state'] = tk.NORMAL
            self.btn_start['state'] = tk.NORMAL

        self.btn_add_profile['state'] = tk.NORMAL


    def getProfileJSON(self):
        data = {
            "title": self.projectTitle.get(),
            "url": self.url.get(),
            "visitpages": self.visitpages.get(),
            "mustvisit": self.txt_mustvisit.get("1.0", tk.END).split()
        }
        return json.dumps(data)


    def saveProfile(self, project, profile):
        json = self.getProfileJSON()
        if not saveProfile(json, self.project, self.profile.get()):
            #show error
            return
        return

    def startScan(self):
        url = self.url.get()
        title = self.projectTitle.get()
        num_pages = self.visitpages.get()
        must_visit = self.txt_mustvisit.get("1.0", tk.END).split()
        timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M')
        browser_profile = join(CONFIG_DIR, self.project, '_'.join(f"chromium-profile-{title}-{timestamp}".split()))
        output = join(CONFIG_DIR, self.project, '_'.join(f"output-{title}-{timestamp}".split()))

        print(browser_profile)

        try:
            self.disableProfileControls()
            t1 = start_chromium(url, browser_profile)
            t1.join()

            t2 = start_wec(
                url,
                browser_profile,
                title,
                output,
                num_pages,
                must_visit,
            )
            t2.join()
        finally:
            self.enableProfileControls(True)


    def createUI(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=5)

        l_frame = ttk.Frame(self, padding="10 10 5 10")
        r_frame = ttk.Frame(self, padding="5 10 10 10")
        l_frame.grid(column=0, row=0, sticky="NEW")
        r_frame.grid(column=1, row=0, sticky="NEW")

        r_frame.columnconfigure(0, weight=6)
        r_frame.columnconfigure(1, weight=1)
        r_frame.columnconfigure(2, weight=1)
        r_frame.columnconfigure(3, weight=1)
        r_frame.columnconfigure(4, weight=1)


        self.treeview = ttk.Treeview(
            l_frame,
            columns=(
                'name',
            ),
            displaycolumns=('name'),
            selectmode='browse',
            show='',
        )
        self.treeview.pack(fill=tk.BOTH, expand=True)

        lb_frame = ttk.Frame(l_frame)
        lb_frame.pack()


        self.btn_add = ttk.Button(
            lb_frame,
            command=lambda: self.newProject(
                askString(
                    self,
                    "Neues Projekt",
                    "Projektname (z.B. Website):"
                )
            ),
            text="+"
        )
        self.btn_add.pack(expand=True, fill=tk.X, side=tk.LEFT)


        self.btn_del = ttk.Button(
            lb_frame,
            command=self.delProject,
            text="-"
        )
        self.btn_del.pack(expand=True, fill=tk.X, side=tk.RIGHT)


        self.combobox = ttk.Combobox(
            r_frame,
            textvariable=self.profile
        )
        self.combobox.grid(column=0, row=0, sticky=tk.EW)


        self.btn_save_profile = ttk.Button(
            r_frame,
            text="Profil Speichern",
            command=lambda: self.saveProfile(
                self.project,
                self.profile
            )
        )
        self.btn_save_profile.grid(column=1, padx="5", row=0, sticky=tk.EW)


        self.btn_delete_profile = ttk.Button(
            r_frame,
            text="Profil Löschen",
            command=lambda: deleteProfile(
                self.project,
                self.profile
            )
        )
        self.btn_delete_profile.grid(column=2, padx="5", row=0, sticky=tk.EW)

        self.btn_copy_profile = ttk.Button(
            r_frame,
            text="Profil Kopieren",
            command=lambda: self.copyProfile(
                self.profile,
                self.project
            )
        )
        self.btn_copy_profile.grid(column=3, row=0, sticky=tk.EW)

        self.btn_add_profile = ttk.Button(
            r_frame,
            text="Neues Profil",
            command=lambda: self.newProfile(
                askString(
                    self,
                    "Neues Profil",
                    "Neuer Profilname:"
                ),
                self.project
            )
        )
        self.btn_add_profile.grid(column=4, padx="5", row=0, sticky=tk.EW)



        self.lbl_title = ttk.Label(
            r_frame,
            text="Profilname:"
        )
        self.lbl_title.grid(column=0,columnspan=5,row=1,sticky="nw")

        self.txt_title = ttk.Entry(
            r_frame,
            textvariable=self.projectTitle,
        )
        self.txt_title.grid(column=0,columnspan=5,row=2,sticky="new")

        self.lbl_url = ttk.Label(
            r_frame,
            text="URL:"
        )
        self.lbl_url.grid(column=0,columnspan=5,row=3,sticky="nw")

        self.txt_url = ttk.Entry(
            r_frame,
            textvariable=self.url,
        )
        self.txt_url.grid(column=0,columnspan=5,row=4,sticky="new")

        self.lbl_visitpages = ttk.Label(
            r_frame,
            text="Anzahl Seiten:"
        )
        self.lbl_visitpages.grid(column=0,columnspan=5,row=5,sticky="nw")

        self.spn_visitpages = ttk.Spinbox(
            r_frame,
            from_=1,
            to=200,
            textvariable=self.visitpages,
            wrap=True
        )
        self.spn_visitpages.grid(column=0,columnspan=5,row=6, sticky=tk.NW)

        self.lbl_mustvisit = ttk.Label(
            r_frame,
            text="URLs die besucht werden müssen (eine pro Zeile)"
        )
        self.lbl_mustvisit.grid(column=0, columnspan=5, row=7, sticky=tk.NW)
        self.txt_mustvisit = tk.Text(
            r_frame,
            height=8
        )
        self.txt_mustvisit.grid(column=0, columnspan=5, row=8, sticky=tk.EW)

        self.btn_start = ttk.Button(
            r_frame,
            text="Start",
            command=lambda: self.startScan()
        )
        self.btn_start.grid(column=0,columnspan=5, row=9, sticky=tk.NE)


        self.testbutton = ttk.Button(
            self,
            text="test",
            command=self.getProfileJSON
        )
        self.testbutton.grid()