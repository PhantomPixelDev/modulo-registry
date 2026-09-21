"""Rebuild registry.json from the latest release of every repository in sources.json.

Each release must carry <slug>-<version>.zip and <slug>-<version>.zip.sha256, as
the plugin template's release workflow publishes. The checksum is recomputed from
the downloaded zip and must match the published one; a mismatch fails the build
rather than writing a checksum nobody verified.
"""

import hashlib
import json
import subprocess
import sys
import urllib.request


def gh(*args):
    return json.loads(subprocess.check_output(["gh", "api", *args]))


def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def build_entry(source):
    repo = source["repository"]
    release = gh(f"repos/{repo}/releases/latest")
    tag = release["tag_name"]

    manifest = json.loads(fetch(f"https://raw.githubusercontent.com/{repo}/{tag}/plugin.json"))
    version = manifest["version"]
    if tag.lstrip("v") != version:
        raise SystemExit(f"{repo}: tag {tag} does not match plugin.json {version}")

    name = f"{manifest['slug']}-{version}.zip"
    assets = {a["name"]: a["browser_download_url"] for a in release["assets"]}
    if name not in assets or name + ".sha256" not in assets:
        raise SystemExit(f"{repo}: release {tag} lacks {name} or its .sha256")

    published = fetch(assets[name + ".sha256"]).decode().split()[0].lower()
    actual = hashlib.sha256(fetch(assets[name])).hexdigest()
    if published != actual:
        raise SystemExit(f"{repo}: published checksum {published} != actual {actual}")

    return {
        "slug": manifest["slug"],
        "name": manifest.get("name", manifest["slug"]),
        "namespace": manifest.get("namespace"),
        "description": manifest.get("description", ""),
        "author": manifest.get("author", ""),
        "license": source.get("license", ""),
        "repository": f"https://github.com/{repo}",
        "latest": {
            "version": version,
            "asset_url": assets[name],
            "sha256": actual,
            "min_core_version": source.get("min_core_version"),
            "released_at": release.get("published_at"),
        },
    }


def main():
    sources = json.load(open("sources.json"))["plugins"]
    entries = sorted((build_entry(s) for s in sources), key=lambda e: e["slug"])
    with open("registry.json", "w", newline="\n") as out:
        json.dump({"schema": 1, "plugins": entries}, out, indent=2)
        out.write("\n")
    print(f"registry.json: {len(entries)} plugin(s)", file=sys.stderr)


if __name__ == "__main__":
    main()
