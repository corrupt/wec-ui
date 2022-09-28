import tkinter as tk
import json
import gettext

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
#from wecui.l10n import _
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
                _("Fehler"),
                _("Konnte keine Puppeteeer Installation unter {} finden").format(self.WEC_LOCATION)
            )
            exit(1)

        #self.project = None


        self.createUI()
        self.updateProjects()
        self.treeview.bind('<<TreeviewSelect>>', self.treeviewItemSelected)
        self.notebook.bind('<<NotebookTabChanged>>', self.tabChanged)

    def getProject(self):
        for c in self.treeview.selection():
            return self.treeview.item(c)['text']
        return None

    def tabChanged(self, event):
        if len(self.notebook.tabs()) > 0:
            if self.notebook.select() == self.notebook.tabs()[-1]:
                if self.lastTab is not None:
                    self.notebook.select(self.lastTab)
                self.newProfile(
                    askString(
                        self,
                        _("Neues Profil"),
                        _("Neuer Profilname:")
                    ),
                    self.getProject
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
        if profile is None:
            return
        if len(self.notebook.tabs()) > 0:
            for t in self.notebook.tabs():
                if self.notebook.tab(t, 'text') == profile:
                    self.notebook.select(t)


    def loadConfig(self):
        config = join(CONFIG_DIR, 'wecui.cfg')
        try:
            with open(config, 'r') as f:
                c = json.load(f)
                self.WEC_LOCATION = c['wec_location']
        except:
            showMessage(
                self,
                _("Keine Konfiguration"),
                _("Konnte keine Konfigurationsdatei ({}) finden.").format(config)
            )
            exit(1)


    def newProject(self, project):
        if project is not None:
            if newProject(project):
                self.updateProjects()
                #self.selectProject(project)
            else:
                showMessage(
                    self,
                    _("Fehler"),
                    _("Konnte Projekt {} nich erstellen").format(project)
                )


    def newProfile(self, profile, project):
        if profile is None:
            return
        if False == newProfile(
            profile,
            project,
            profile_default=default_profile(profileTitle(project, profile))
        ):
            showMessage(
                self,
                _("Kann Profil nicht erstellen"),
                _("Ein Profil mit diesem Namen existiert bereits")
            )
        else:
            self.updateProfiles(project)
            self.selectProfile(profile)


    def copyProfile(self, profile, project):
        check = False
        while not check:
            newProfile = askString(
                self,
                _("Profil Kopieren"),
                _("Name des neuen Profils:"),
                f"{profile}_kopie"
            )
            if newProfile is None:
                return
            check = copyProfile(profile, newProfile, self.getProject())
            if not check:
                showMessage(
                    self,
                    _("Profil existiert bereits"),
                    _("Ein Profil mit diesem Namen existiert bereits"),
                    _("{}_kopie").format(profile)
                )
        self.updateProfiles(project)
        self.selectProfile(newProfile)

    def deleteProject(self):

        item = self.treeview.selection()[0]
        project = self.treeview.item(item)['text']

        def onError(f,p,e):
            showMessage(self, _("Fehler"), _("Kann Projekt {} nicht löschen").format(project))

        if askConfirmation(
            self,
            _("Projekt Löschen?"),
            _("Soll das Projekt {} wirklich unwiderruflich gelöscht werden?").format(project)
        ):
            deleteProject(project, onError)
            self.updateProjects()
            self.updateProfiles(self.getProject())


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
        if project is None:
            return

        profiles = getProfiles(project)
        for filename in profiles:
            w = profileWidget(self.notebook, project, filename, self.CHROMIUM, self.WEC_LOCATION)
            w.bind('<<profile_update>>', lambda e: self.updateProfiles(project))
            w.bind('<<profile_copy>>', lambda e: self.copyProfile(filename2Profile(filename), project))
            self.notebook.add(
                w,
                text=filename2Profile(filename)
            )
        if len(profiles) > 0:
            self.notebook.add(ttk.Frame(), text='+')
        else:
            self.newProfile(
                askString(
                    self,
                    _("Neues Profil für {}").format(project),
                    _("Neues Profil für {}:").format(project)
                ),
                project
            )


    def treeviewItemSelected(self, event):
        for item in self.treeview.selection():
            self.updateProfiles(self.getProject())


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
                    _("Neues Projekt"),
                    _("Projektname (z.B. Website):")
                )
            ),
            text=_("Neues Projekt")
        )
        self.btn_add.pack(expand=True, side=tk.LEFT)


        self.btn_del = ttk.Button(
            lb_frame,
            command=self.deleteProject,
            text=_("Projekt Löschen")
        )
        self.btn_del.pack(expand=True, fill=tk.BOTH, side=tk.RIGHT)


        self.notebook = ttk.Notebook(
            r_frame,
        )
        self.notebook.grid(column=0, row=0, sticky=tk.NSEW)

