import argparse
import logging
import os

import requests
from OBAS_utils.release_utils import check_release, closeRelease

logging.basicConfig(encoding="utf-8", level=logging.INFO)

parser = argparse.ArgumentParser("release")
parser.add_argument(
    "branch_client_python", help="The new version number of the release.", type=str
)
parser.add_argument(
    "previous_version", help="The previous version number of the release.", type=str
)
parser.add_argument(
    "new_version", help="The new version number of the release.", type=str
)
parser.add_argument(
    "github_token", help="The github token to use for the release note.", type=str
)
parser.add_argument(
    "--dev", help="Flag to prevent pushing the release.", action="store_true"
)
args = parser.parse_args()

previous_version = args.previous_version
new_version = args.new_version
branch_client_python = args.branch_client_python
github_token = args.github_token

os.environ["DRONE_COMMIT_AUTHOR"] = "Filigran-Automation"
os.environ["GIT_AUTHOR_NAME"] = "Filigran Automation"
os.environ["GIT_AUTHOR_EMAIL"] = "automation@filigran.io"
os.environ["GIT_COMMITTER_NAME"] = "Filigran Automation"
os.environ["GIT_COMMITTER_EMAIL"] = "automation@filigran.io"

# Python library release
logging.info("[client-python] Starting the release")
with open("./pyobas/__init__.py", "r") as file:
    filedata = file.read()
filedata = filedata.replace(previous_version, new_version)
with open("./pyobas/__init__.py", "w") as file:
    file.write(filedata)
with open("./pyobas/_version.py", "r") as file:
    filedata = file.read()
filedata = filedata.replace(previous_version, new_version)
with open("./pyobas/_version.py", "w") as file:
    file.write(filedata)

# Commit the change
logging.info("[client-python] Pushing to " + branch_client_python)
os.system('git commit -a -m "[client] Release ' + new_version + '"')
if not args.dev:
    os.system("git push origin " + branch_client_python)

logging.info("[client-python] Tagging")
os.system("git tag -f " + new_version)
if not args.dev:
    os.system("git push -f --tags > /dev/null 2>&1")

logging.info("[client-python] Generating release")
os.system("gren release > /dev/null 2>&1")

# Modify the release note
logging.info("[client-python] Getting the current release note")
release = requests.get(
    "https://api.github.com/repos/OpenBAS-Platform/client-python/releases/latest",
    headers={
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + github_token,
        "X-GitHub-Api-Version": "2022-11-28",
    },
)
release_data = release.json()
release_body = release_data["body"]

logging.info("[client-python] Generating the new release note")
if not args.dev:
    github_release_note = requests.post(
        "https://api.github.com/repos/OpenBAS-Platform/client-python/releases/generate-notes",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + github_token,
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={"tag_name": new_version, "previous_tag_name": previous_version},
    )
    github_release_note_data = github_release_note.json()
    github_release_note_data_body = github_release_note_data["body"]
    if "Full Changelog" not in release_body:
        new_release_note = (
            release_body
            + "\n"
            + github_release_note_data_body.replace(
                "## What's Changed", "#### Pull Requests:\n"
            ).replace("## New Contributors", "#### New Contributors:\n")
        )
    else:
        new_release_note = release_body

    logging.info("[client-python] Updating the release")
    requests.patch(
        "https://api.github.com/repos/OpenBAS-Platform/client-python/releases/"
        + str(release_data["id"]),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + github_token,
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={"body": new_release_note},
    )

if not args.dev:
    closeRelease(
        "https://api.github.com/repos/OpenBAS-Platform/client-python",
        new_version,
        github_token,
    )

logging.info(
    "[client-python] Release done! Waiting 10 minutes for CI/CD and publication..."
)

if not args.dev:
    check_release("https://pypi.org/simple/pyobas/", "pyobas-" + new_version, 10)
