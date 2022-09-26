from wecui import App
from os import getenv
from os.path import join,dirname,normpath
import gettext

if getenv('LANG').startswith('en'):
    en = gettext.translation('wecui', localedir=normpath(join(dirname(__file__), 'l10n')), languages=['en'])
    en.install()
else:
    gettext.install('wecui', normpath(join(dirname(__file__), 'l10n')))

if __name__ == "__main__":
    app = App()
    app.mainloop()