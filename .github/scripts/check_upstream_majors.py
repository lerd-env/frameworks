"""Find frameworks whose upstream shipped a stable major the store has no definition for.

Each framework's composer detect packages are looked up on Packagist, in order,
and the newest stable major is compared with the index's `latest`. Prints the
findings as JSON for the workflow to turn into issues, and lists what it could
not check in the job summary.

    python3 .github/scripts/check_upstream_majors.py
"""

import json
import os
import pathlib
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]

# Frameworks detected by files alone still ship on Packagist under a name the
# detect rules never needed.
EXTRA_PACKAGES = {
    "bedrock": ["roots/bedrock"],
    "wordpress": ["roots/wordpress"],
    "testbench": ["orchestra/testbench"],
}


def fetch_releases(package):
    url = f"https://repo.packagist.org/p2/{package}.json"
    req = urllib.request.Request(url, headers={"User-Agent": "lerd-frameworks-upstream-check"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)["packages"][package]


def newest_stable_major(releases):
    majors = [int(r["version_normalized"].split(".")[0])
              for r in releases if "-" not in r["version_normalized"]]
    return max(majors, default=None)


def packages_for(framework):
    detected = [d["composer"] for d in framework["detect"] if "composer" in d]
    return detected + EXTRA_PACKAGES.get(framework["name"], [])


def upstream_major(packages, fetch):
    # A 404 means the package lives off Packagist (Magento's own repo), so the
    # next candidate is tried; anything else is a real failure.
    for package in packages:
        try:
            return package, newest_stable_major(fetch(package))
        except urllib.error.HTTPError as err:
            if err.code != 404:
                raise
    return None, None


def find_new_majors(index, fetch):
    found, unchecked = [], []
    for fw in index["frameworks"]:
        package, upstream = upstream_major(packages_for(fw), fetch)
        if upstream is None:
            unchecked.append(fw["name"])
            continue
        latest = int(fw["latest"])
        if upstream > latest:
            found.append({"name": fw["name"], "label": fw["label"], "package": package,
                          "latest": latest, "upstream": upstream})
    return found, unchecked


def main():
    index = json.loads((ROOT / "frameworks" / "index.json").read_text())
    found, unchecked = find_new_majors(index, fetch_releases)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary and unchecked:
        with open(summary, "a") as out:
            out.write("Not on Packagist, check by hand: " + ", ".join(unchecked) + "\n")
    print(json.dumps(found))


if __name__ == "__main__":
    main()
