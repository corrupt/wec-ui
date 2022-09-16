import threading
import subprocess

from wecui.utils import openFile
from os.path import join

def __run_wec__(
    url,
    browser_profile,
    title,
    output,
    cwd,
    wec_dir,
    num_pages,
    must_visit,
    first_party
):

    first_party = list(map(lambda s: f"-f {s}", first_party))
    must_visit = list(map(lambda s: f"-l {s}", must_visit))

    subprocess.run([
        'node',
        join(wec_dir, 'bin', 'website-evidence-collector.js'),
        url,
        '--html',
        '--overwrite',
        '--headless=false',
        *first_party,
        *must_visit,
        f'--browser-profile={browser_profile}',
        '-t',  title,
        '-m', num_pages,
        '-o', output,
        '--',
        '--no-sandbox'
        ],
        cwd=cwd
    )
    openFile(join(cwd, output, "inspection.html"))


def __run_chromium__(
    url,
    browser_profile,
    browser_binary,
):
    subprocess.run([
        browser_binary,
        f'--user-data-dir={browser_profile}',
        "--no-first-run",
        "--no-default-browser-check",
        url
    ])


def start_chromium(
    url,
    browser_profile,
    browser_binary,
):
    t = threading.Thread(
        target=__run_chromium__,
        args=(
            url,
            browser_profile,
            browser_binary
        ),
        daemon=True
    )
    t.start()
    return t


def start_wec(
    url,
    browser_profile,
    title,
    output,
    cwd,
    wec_dir,
    num_pages = 50,
    must_visit = [],
    first_party = [],
):
    t = threading.Thread(
        target=__run_wec__,
        args=(
            url,
            browser_profile,
            title,
            output,
            cwd,
            wec_dir,
            num_pages,
            must_visit,
            first_party,
        ),
        daemon=True
    )
    t.start()
    return t