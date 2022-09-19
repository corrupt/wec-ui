import tkinter as tk
from tkinter import ttk
from datetime import datetime

from wecui.utils import *
from wecui.ask_confirmation import askConfirmation
from wecui.ask_string import askString
from wecui.show_message import showMessage
from wecui.run_wec import start_wec, start_chromium


class profileWidget(ttk.Frame):

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

        self.bind('<<destroy>>', self.onDestroy)

        self.createUI()


    def onDestroy(self, event):
        print(f'destroying widget for {self.filename}')


    def clearWidgets(self):
        self.txt_mustvisit.delete('1.0', tk.END)
        self.url.set('')
        self.projectTitle.set('')
        self.visitpages.set('')
    

    def disableProfileControls(self):
        #self.combobox['state'] = tk.DISABLED
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
        if not saveProfile(
            json,
            project,
            profile
        ):
            showMessage(
                self,
                "Fehler",
                f"Konnte Profil {profile} nicht speichern."
            )


    def deleteProfile(self, project, profile):
        if askConfirmation(
            self,
            "Profil Löschen?",
            f"Soll das Profil {profile} mit allen Ergebnissen wirklich unwiderruflich gelöscht werden?"
        ):
            if not deleteProfile(project, profile):
                showMessage(
                    self,
                    "Fehler",
                    f"Profil {profile} konnte nicht gelöscht werden"
                )
            self.updateProjects()
            self.selectProject(project)
            self.updateProfiles(project)



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
            self.disableProfileControls()
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
            self.enableProfileControls(True)


    def createUI(self):

        self.btn_save_profile = ttk.Button(
            self,
            text="Profil Speichern",
            command=lambda: self.saveProfile(
                self.project,
                self.profile.get()
            )
        )
        self.btn_save_profile.grid(column=1, padx="5", row=0, sticky=tk.EW)


        self.btn_delete_profile = ttk.Button(
            self,
            text = "Profil Löschen",
            command = lambda: self.deleteProfile(
                self.project,
                self.profile.get()
            )
        )
        self.btn_delete_profile.grid(column=2, padx="5", row=0, sticky=tk.EW)

        self.btn_copy_profile = ttk.Button(
            self,
            text="Profil Kopieren",
            command=lambda: self.copyProfile(
                self.profile.get(),
                self.project
            )
        )
        self.btn_copy_profile.grid(column=3, row=0, sticky=tk.EW)

        self.btn_add_profile = ttk.Button(
            self,
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
            self,
            text="Profilname:"
        )
        self.lbl_title.grid(column=0,columnspan=5,row=1,sticky="nw")


        self.txt_title = ttk.Entry(
            self,
            textvariable=self.projectTitle,
        )
        self.txt_title.grid(column=0,columnspan=5,row=2,sticky="new")


        self.lbl_url = ttk.Label(
            self,
            text="URL:"
        )
        self.lbl_url.grid(column=0,columnspan=5,row=3,sticky="nw")


        self.txt_url = ttk.Entry(
            self,
            textvariable=self.url,
        )
        self.txt_url.grid(column=0,columnspan=5,row=4,sticky="new")


        self.lbl_visitpages = ttk.Label(
            self,
            text="Anzahl Seiten:"
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
            text="URLs die besucht werden müssen (eine pro Zeile)"
        )
        self.lbl_mustvisit.grid(column=0, columnspan=5, row=7, sticky=tk.NW)
        self.txt_mustvisit = tk.Text(
            self,
            height=8
        )
        self.txt_mustvisit.grid(column=0, columnspan=5, row=8, sticky=tk.EW)


        self.btn_start = ttk.Button(
            self,
            text="Start",
            command=lambda: self.startScan()
        )
        self.btn_start.grid(column=0,columnspan=1, row=9, sticky=tk.EW)


        self.btn_open_dir = ttk.Button(
            self,
            text="Projektordner öffnen",
            command=lambda: openDirectory(self.project)
        )
        self.btn_open_dir.grid(column=4, columnspan=1,row=9,sticky=tk.EW)
