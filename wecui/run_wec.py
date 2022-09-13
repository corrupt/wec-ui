import threading
import subprocess

def __run_wec__(
    url,
    browser_profile,
    title,
    output,
    num_pages,
    must_visit,
    first_party,
):

    first_party = list(map(lambda s: f"-f {s}", first_party))
    must_visit = list(map(lambda s: f"-l {s}", must_visit))

    subprocess.run([
        'node',
        '/home/corrupt/git/website-evidence-collector/bin/website-evidence-collector.js',
        url,
        '--html',
        '--overwrite',
        '--headless=false',
        *first_party,
        *must_visit,
        f'--browser-profile={browser_profile}',
        f'-t {title}',
        f'-m {num_pages}',
        f'-o {output}',
        '--',
        '--no-sandbox'
    ])

def __run_chromium__(
    url,
    browser_profile,
):
    subprocess.run([
        "/home/corrupt/git/website-evidence-collector/node_modules/puppeteer/.local-chromium/linux-901912/chrome-linux/chrome",
        f'--user-data-dir={browser_profile}',
        "--no-first-run",
        "--no-default-browser-check",
        url
    ])


def start_chromium(
    url,
    browser_profile,
):
    t = threading.Thread(
        target=__run_chromium__,
        args=(
            url,
            browser_profile
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
            num_pages,
            must_visit,
            first_party,
        ),
        daemon=True
    )
    t.start()
    return t