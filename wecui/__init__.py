
import tkinter as tk
import json
from tkinter import ttk
from datetime import datetime
from os.path import join
from wecui.profile_widget import profileWidget

from wecui.utils import *

from wecui.ask_string import askString
from wecui.ask_confirmation import askConfirmation
from wecui.show_message import showMessage
from wecui.run_wec import start_wec, start_chromium
from wecui.profile_default import default_profile

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('WEC remote')

        self.lastTab = 0

        self.loadConfig()

        self.CHROMIUM = findChromium(self.WEC_LOCATION)
        if self.CHROMIUM is None:
            showMessage(
                self,
                "Fehler",
                f"Konnte keine Puppeteeer Installation unter {self.WEC_LOCATION} finden"
            )
            exit(1)

        self.project = None


        self.createUI()
        self.updateProjects()
        self.treeview.bind('<<TreeviewSelect>>', self.treeviewItemSelected)
        self.notebook.bind('<<NotebookTabChanged>>', self.tabChanged)


    def tabChanged(self, event):
        if self.notebook.select() == self.notebook.tabs()[-1]:
            self.notebook.select(self.lastTab)
            self.newProfile(
                askString(
                    self,
                    "Neues Profil",
                    "Neuer Profilname:"
                ),
                self.project
            )
            self.updateProjects()
        else:
            self.lastTab = self.notebook.select()


    def selectProject(self, project):
        for c in self.treeview.get_children():
            if self.treeview.item(c)['text'] == project:
                self.treeview.selection_set(c)
                break


    def selectProfile(self, profile):
        for t in self.notebook.tabs():
            if self.notebook.tab(t, 'text') == profile:
                self.notebook.select(t)
                self.mainloop()


    def loadConfig(self):
        config = join(CONFIG_DIR, 'wecui.cfg')
        try:
            with open(config, 'r') as f:
                c = json.load(f)
                self.WEC_LOCATION = c['wec_location']
        except:
            showMessage(
                self,
                "Keine Konfiguration",
                f"Konnte keine Konfigurationsdatei ({config}) finden."
            )
            exit(1)


    def newProject(self, project):
        if project is not None:
            if newProject(project):
                self.updateProjects()
                self.selectProject(project)
            else:
                showMessage(
                    self,
                    "Fehler",
                    f"Konnte Projekt {project} nich erstellen"
                )


    def newProfile(self, profile, project):
        if False == newProfile(
            profile,
            project,
            profile_default=default_profile(profileTitle(project, profile))
        ):
            showMessage(
                self,
                "Kann Profil nicht erstellen",
                "Ein Profil mit diesem Namen existiert bereits"
            )
        else:
            self.updateProfiles(project)
            self.selectProfile(profile)


    def copyProfile(self, profile, project):
        check = False
        while not check:
            newProfile = askString(
                self,
                "Profil Kopieren",
                "Name des neuen Profils:",
                f"{profile}_kopie"
            )
            if newProfile is None:
                return
            check = copyProfile(profile, newProfile, self.project)
            if not check:
                showMessage(
                    self,
                    "Profil existiert bereits",
                    "Ein Profil mit diesem Namen existiert bereits"
                    f"{profile}_kopie"
                )
        self.updateProfiles(self.project)
        self.selectProfile(newProfile)

    def deleteProject(self):

        item = self.treeview.selection()[0]
        project = self.treeview.item(item)['text']

        def onError(f,p,e):
            showMessage(self, "Fehler", f"Kann Projekt {project} nicht löschen")

        if askConfirmation(
            self,
            "Projekt Löschen?",
            f"Soll das Projekt {project} wirklich unwiderruflich gelöscht werden?"
        ):
            deleteProject(project, onError)
            self.updateProjects()


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

    def clearTabs(self):
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

    def updateProfiles(self, project):
        self.clearTabs()

        for filename in getProfiles(project):
            w = profileWidget(self.notebook, project, filename)
            w.bind('<<profile_update>>', lambda e: self.updateProfiles(project))
            w.bind('<<profile_copy>>', lambda e: self.copyProfile(filename2Profile(filename), project))
            self.notebook.add(
                w,
                text=filename2Profile(filename)
            )
        self.notebook.add(ttk.Frame(), text='+')


    def treeviewItemSelected(self, event):
        for item in self.treeview.selection():
            self.project = self.treeview.item(item)['text']
            self.updateProfiles(self.project)
            #profiles = getProfiles(self.project)
            #self.enableProfileControls(len(profiles) > 0)
            #self.comboboxItemSelected(None)


    def comboboxItemSelected(self, event):
        self.clearWidgets()
        profile = openProfile(self.project, self.profile.get())
        if profile is not None:
            self.url.set(profile['url'])
            self.projectTitle.set(profile['title'])
            self.visitpages.set(profile['visitpages'])
            self.txt_mustvisit.insert('1.0', "\n".join(profile['mustvisit']))


    def createUI(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=5)

        l_frame = ttk.Frame(self, padding="10 10 5 10")
        r_frame = ttk.Frame(self, padding="5 10 10 10")
        l_frame.grid(column=0, row=0, sticky="NEW")
        r_frame.grid(column=1, row=0, sticky="NEW")


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
        self.btn_add.pack(expand=True, fill=tk.BOTH)


        self.btn_del = ttk.Button(
            lb_frame,
            command=self.deleteProject,
            text="-"
        )
        self.btn_del.pack(expand=True, fill=tk.BOTH, side=tk.RIGHT)


        self.notebook = ttk.Notebook(
            r_frame,
        )
        self.notebook.grid(column=0, row=0, sticky=tk.NSEW)

