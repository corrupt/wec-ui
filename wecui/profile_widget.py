import tkinter as tk
from tkinter import ttk
from datetime import datetime

from wecui.utils import *
from wecui.ask_confirmation import askConfirmation
from wecui.ask_string import askString
from wecui.show_message import showMessage
from wecui.run_wec import start_wec, start_chromium
#from wecui.l10n import _
class profileWidget(ttk.Frame):

    def __init__(self, parent, project, filename, chromium, wec):
        super().__init__(parent, padding=10)
        self.project = project
        self.filename = filename
        self.profile = filename2Profile(filename)

        self.CHROMIUM = chromium
        self.WEC_LOCATION = wec

        self.bind('<<destroy>>', self.onDestroy)

        self.url = tk.StringVar()
        self.projectTitle = tk.StringVar()
        self.visitpages = tk.StringVar()

        self.url.trace_add('write', self.startButtonState)
        self.visitpages.trace_add('write', self.startButtonState)

        self.createUI()
        self.data = self.openProfile(self.filename)
        try:
            if self.data is not None:
                self.url.set(self.data['url'])
                self.projectTitle.set(self.data['title'])
                self.visitpages.set(self.data['visitpages'])
        finally:
            self.startButtonState(None, None, None)



    def startButtonState(self, var, index, mode):
        url = self.url.get()
        vp = self.visitpages.get()
        if url and vp:
            self.btn_start['state'] = tk.ACTIVE
        else:
            self.btn_start['state'] = tk.DISABLED

    def onDestroy(self, event):
        print(f'destroying widget for {self.filename}')


    def clearWidgets(self):
        self.txt_mustvisit.delete('1.0', tk.END)
        self.url.set('')
        self.projectTitle.set('')
        self.visitpages.set('')


    #def disableProfileControls(self):
    #    #self.combobox['state'] = tk.DISABLED
    #    #self.btn_add_profile['state'] = tk.DISABLED
    #    self.btn_copy_profile['state'] = tk.DISABLED
    #    self.btn_save_profile['state'] = tk.DISABLED
    #    #self.btn_delete_profile['state'] = tk.DISABLED
    #    self.lbl_title['state'] = tk.DISABLED
    #    self.txt_title['state'] = tk.DISABLED
    #    self.lbl_url['state'] = tk.DISABLED
    #    self.txt_url['state'] = tk.DISABLED
    #    self.lbl_visitpages['state'] = tk.DISABLED
    #    self.spn_visitpages['state'] = tk.DISABLED
    #    self.lbl_mustvisit['state'] = tk.DISABLED
    #    self.txt_mustvisit['state'] = tk.DISABLED
    #    self.btn_start['state'] = tk.DISABLED


    #def enableProfileControls(self, profile_present=False):
    #    if (profile_present):
    #        #self.combobox['state'] = 'readonly'

    #        self.btn_save_profile['state'] = tk.NORMAL
    #        self.btn_copy_profile['state'] = tk.NORMAL
    #        self.btn_save_profile['state'] = tk.NORMAL
    #        self.btn_delete_profile['state'] = tk.NORMAL
    #        self.lbl_title['state'] = tk.NORMAL
    #        self.txt_title['state'] = tk.NORMAL
    #        self.lbl_url['state'] = tk.NORMAL
    #        self.txt_url['state'] = tk.NORMAL
    #        self.lbl_visitpages['state'] = tk.NORMAL
    #        self.spn_visitpages['state'] = tk.NORMAL
    #        self.lbl_mustvisit['state'] = tk.NORMAL
    #        self.txt_mustvisit['state'] = tk.NORMAL
    #        self.btn_start['state'] = tk.NORMAL

    #    #self.btn_add_profile['state'] = tk.NORMAL


    def openProfile(self, filename):
        if not filename:
            return None

        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None


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
        if not saveProfile(
            json,
            project,
            profile
        ):
            showMessage(
                self,
                _("Fehler"),
                _("Konnte Profil {} nicht speichern.").format(profile)
            )


    def deleteProfile(self, project, profile):
        if askConfirmation(
            self,
            _("Profil Löschen?"),
            _("Soll das Profil {} mit allen Ergebnissen wirklich unwiderruflich gelöscht werden?").format(profile)
        ):
            if not deleteProfile(project, profile):
                showMessage(
                    self,
                    _("Fehler"),
                    _("Profil {} konnte nicht gelöscht werden").format(profile)
                )
            self.profile_update_event()


    def renameProfile(self, project, profile):
        check = False
        while not check:
            newProfile = askString(
                self,
                _("Profil Umbenennen"),
                _("Neuer Name des Profils:"),
                profile
            )
            if newProfile is None:
                return
            check = renameProfile(profile, newProfile, self.project)
            if not check:
                showMessage(
                    self,
                    _("Profil existiert bereits"),
                    _("Ein Profil mit diesem Namen existiert bereits"),
                    _("{}_kopie").format(profile)
                )
        self.profile_update_event()



    def profile_update_event(self):
        self.event_generate('<<profile_update>>')


    def profile_copy_event(self):
        self.event_generate('<<profile_copy>>')


    def startScan(self):
        url = self.url.get()
        title = self.projectTitle.get()
        num_pages = self.visitpages.get()
        must_visit = self.txt_mustvisit.get("1.0", tk.END).split()
        timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M')
        browser_profile = join(CONFIG_DIR, self.project, '_'.join(f"chromium-profile-{title}-{timestamp}".split()))
        output = '_'.join(f"output-{title}-{timestamp}".split())
        cwd = join(CONFIG_DIR, self.project)

        try:
            self.t1 = start_chromium(url, browser_profile, self.CHROMIUM)
            self.t1.join()

            self.t2 = start_wec(
                url,
                browser_profile,
                title,
                output,
                cwd,
                self.WEC_LOCATION,
                num_pages,
                must_visit,
            )
            #self.t2.join()
        finally:
            return


    def createUI(self):

        self.btn_save_profile = ttk.Button(
            self,
            text=_("Profil Speichern"),
            command=lambda: self.saveProfile(
                self.project,
                self.profile
            )
        )
        self.btn_save_profile.grid(column=0, row=0, sticky=tk.EW)


        self.btn_delete_profile = ttk.Button(
            self,
            text = _("Profil Löschen"),
            command = lambda: self.deleteProfile(
                self.project,
                self.profile
            )
        )
        self.btn_delete_profile.grid(column=1, padx="5", row=0, sticky=tk.EW)


        self.btn_copy_profile = ttk.Button(
            self,
            text=_("Profil Kopieren"),
            command=self.profile_copy_event
        )
        self.btn_copy_profile.grid(column=2, row=0, sticky=tk.EW)


        self.btn_rename_profile = ttk.Button(
            self,
            text=_("Profil Umbenennen"),
            command= lambda: self.renameProfile(
                self.project,
                self.profile
            )
        )
        self.btn_rename_profile.grid(column=3, row=0, padx="5", sticky=tk.EW)


        self.lbl_title = ttk.Label(
            self,
            text=_("Profiltitel:")
        )
        self.lbl_title.grid(column=0,columnspan=5, row=1,sticky="nw")


        self.txt_title = ttk.Entry(
            self,
            textvariable=self.projectTitle,
        )
        self.txt_title.grid(column=0,columnspan=5,row=2,sticky="new")


        self.lbl_url = ttk.Label(
            self,
            text=_("URL:")
        )
        self.lbl_url.grid(column=0,columnspan=5,row=3,sticky="nw")


        self.txt_url = ttk.Entry(
            self,
            textvariable=self.url,
        )
        self.txt_url.grid(column=0,columnspan=5,row=4,sticky="new")


        self.lbl_visitpages = ttk.Label(
            self,
            text=_("Anzahl Seiten:")
        )
        self.lbl_visitpages.grid(column=0,columnspan=5,row=5,sticky="nw")

        self.spn_visitpages = ttk.Spinbox(
            self,
            from_=1,
            to=200,
            textvariable=self.visitpages,
            wrap=True
        )
        self.spn_visitpages.grid(column=0,columnspan=5,row=6, sticky=tk.NW)

        self.lbl_mustvisit = ttk.Label(
            self,
            text=_("URLs die besucht werden müssen (eine pro Zeile)")
        )
        self.lbl_mustvisit.grid(column=0, columnspan=5, row=7, sticky=tk.NW)
        self.txt_mustvisit = tk.Text(
            self,
            height=8
        )
        self.txt_mustvisit.grid(column=0, columnspan=5, row=8, sticky=tk.EW)


        self.btn_start = ttk.Button(
            self,
            text=_("Start"),
            command=lambda: self.startScan()
        )
        self.btn_start.grid(column=0,columnspan=1, pady=5, row=9, sticky=tk.EW)


        self.btn_open_dir = ttk.Button(
            self,
            text=_("Projektordner öffnen"),
            command=lambda: openDirectory(self.project)
        )
        self.btn_open_dir.grid(column=4, columnspan=1, pady=5, row=9,sticky=tk.EW)
