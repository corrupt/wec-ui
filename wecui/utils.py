from os import listdir, makedirs, remove, walk, rename
from os.path import isfile, isdir, join, abspath, basename
import os
from xdg import xdg_config_home
from shutil import copyfile, SameFileError, rmtree
import subprocess
import sys
import json
import re

CONFIG_DIR=join(xdg_config_home(), "wecui")

def getProjects(dir=CONFIG_DIR):
    absdir = abspath(dir)
    makedirs(absdir, exist_ok=True)
    return [join(absdir,f) for f in listdir(absdir) if isdir(join(absdir,f))]

def getProfiles(project,  dir=CONFIG_DIR):
    absdir = join(abspath(dir), project)
    makedirs(absdir, exist_ok=True)
    files = [join(absdir, f) for f in listdir(absdir) if isfile(join(absdir,f))]
    return list(filter(
        lambda f: f.endswith(".json"),
        files
    ))

def getTitle(profile, dir=CONFIG_DIR):
    absdir=abspath(dir)
    makedirs(absdir, exist_ok=True)
    f = join(absdir, profile)
    if isfile(f):
        with open(f) as p:
            data = json.load(p)
            return data['title']


def getProjectName(project):
    return basename(project)


def getProjectList(dir=CONFIG_DIR):
    p = getProjects()
    return sorted([(x, getProjectName(x)) for x in p])


def newProject(project, dir=CONFIG_DIR):
    absdir = abspath(dir)
    project = join(absdir, project)
    try:
        makedirs(project)
        return True
    except FileExistsError:
        return False

def deleteProject(project, onError, dir=CONFIG_DIR):
    absdir = abspath(dir)
    project = join(absdir, project)
    try:
        rmtree(project, onerror=onError)
    finally:
        return



def newProfile(profile, project, dir=CONFIG_DIR, profile_default=""):
    absdir=abspath(dir)
    p = join(absdir, project, profile2filename(profile))

    try:
        with open(p, 'x') as f:
            f.write(profile_default)
            return True
        return False
    except:
        return False


def copyProfile(profile, newProfile, project, dir=CONFIG_DIR):
    if project is None:
        return
    absdir=abspath(dir)
    src = join(absdir, project, profile2filename(profile))
    dst = join(absdir, project, profile2filename(newProfile))
    try:
        copyfile(src, dst)
        with open(dst, 'r+') as f:
            d = json.load(f)
            d['title'] = profileTitle(project, newProfile)
            f.seek(0)
            f.truncate()
            json.dump(d, f)
        return True
    except SameFileError:
        return False


def renameProfile(profile, newProfile, project, dir=CONFIG_DIR):
    absdir=abspath(dir)
    src = join(absdir, project, profile2filename(profile))
    dst = join(absdir, project, profile2filename(newProfile))

    try:
        rename(src, dst)
        return True
    except Exception as e:
        print(e)
        return False


def profileTitle(project, profile):
    return f"{project} - {profile}"


def saveProfile(data, project, profile, dir=CONFIG_DIR):
    absdir=abspath(dir)
    p = join(absdir, project, profile2filename(profile))

    with open(p, 'w') as f:
        f.write(data)
        return True
    return False


def filename2Profile(filename):
    p = re.compile("wec-(.*)-profile\.json")
    result = p.search(filename)
    return result.group(1)


def profile2filename(profile):
    return f"wec-{profile}-profile.json"


def openProfile(project, profile, dir=CONFIG_DIR):
    if not profile:
        return None

    absdir = abspath(dir)
    p = join(absdir, project, profile2filename(profile))

    try:
        with open(p, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None


def deleteProfile(project, profile, dir=CONFIG_DIR):
    absdir=abspath(dir)
    p = join(absdir, project, profile2filename(profile))
    try:
        remove(p)
        return True
    except FileNotFoundError:
        return False


def openDirectory(project, dir=CONFIG_DIR):
    absdir=abspath(dir)
    d = join(absdir, project)

    if sys.platform.startswith('linux'):
        subprocess.Popen([
            'dbus-send',
            '--session',
            '--print-reply',
            '--dest=org.freedesktop.FileManager1',
            '--type=method_call',
            '/org/freedesktop/FileManager1',
            'org.freedesktop.FileManager1.ShowItems',
            f'array:string:file://{d}/',
            'string:""'
        ])
    elif sys.platform.startswith('win32'):
        os.startfile(d)
    elif sys.platform.startswith('darwin'):
        subprocess.Popen(['open', d])


def openFile(f):
    if sys.platform.startswith('linux'):
        subprocess.Popen(['xdg-open', f])
    elif sys.platform.startswith('win32'):
        os.startfile(f)
    elif sys.platform.startswith('darwin'):
        subprocess.Popen(['open', f])


def findChromium(wec_location):
    puppeteer_dir = join(
        wec_location,
        'node_modules',
        'puppeteer',
        '.local-chromium'
    )

    try:
        chrome1 = next(walk(puppeteer_dir))[1][0]
        puppeteer_dir = join(puppeteer_dir, chrome1)

        chrome2 = next(walk(puppeteer_dir))[1][0]
        puppeteer_dir = join(puppeteer_dir, chrome2)
    except:
        return None

    if sys.platform.startswith('darwin'):
        chrome_binary = join(
            puppeteer_dir,
            'Chromium.app',
            'Contents',
            'MacOS',
            'Chromium'
        )
    else:
        chrome_binary = join(puppeteer_dir, 'chrome')

    if isfile(chrome_binary):
        return chrome_binary
    return None


