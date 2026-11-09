"""Build and check every public HTML/CSS file, using exact filesystem spelling.

Python 3.11+, standard library only. No server or network for local integrity.
"""
from __future__ import annotations

import concurrent.futures
import base64
import hashlib
import json
import re
import shutil
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "site.config.json").read_text(encoding="utf-8"))
BASE = CONFIG["origin"] + CONFIG["basePath"]
IGNORED = {"node_modules", "dist", "reports", "tools", "docs"}
EXTENSIONS = {".html", ".css", ".js", ".mjs", ".json", ".png", ".jpg", ".jpeg",
              ".gif", ".webp", ".svg", ".ico", ".avif", ".woff", ".woff2", ".ttf",
              ".mp4", ".webm", ".mp3", ".ogg", ".pdf", ".txt", ".xml", ".webmanifest"}
DEVELOPMENT = {"package.json", "package-lock.json", "site.config.json"}


def inventory(root=ROOT):
    """All static assets, including unlinked pages; development folders are private."""
    def walk(directory):
        for entry in sorted(directory.iterdir()):
            if entry.name.startswith(".") or entry.name in IGNORED:
                continue
            if entry.is_symlink():
                raise ValueError(f"Symlink is not publishable: {entry}")
            if entry.is_dir():
                yield from walk(entry)
            elif entry.name not in DEVELOPMENT and (
                entry.suffix.lower() in EXTENSIONS or entry.name == "CNAME"
            ):
                yield entry.relative_to(root).as_posix()
    return list(walk(root))


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.references = []
        self.resources = []
        self.duplicates = []
        self.style_depth = False
        self.inline_css = []
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "link" and "stylesheet" in attrs.get("rel", "").split() and attrs.get("href"):
            self.resources.append((attrs["href"], attrs.get("integrity")))
        if tag == "script" and attrs.get("src"):
            self.resources.append((attrs["src"], attrs.get("integrity")))
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.duplicates.append(attrs["id"])
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("name"):
            self.ids.add(attrs["name"])
        if tag == "base":
            raise ValueError("<base> changes URL semantics; use explicit relative paths")
        for key in ("href", "src", "poster", "data", "action", "formaction", "cite", "background"):
            if key in attrs:
                self.references.append(attrs[key])
        if "srcset" in attrs:
            # Data URLs require a full srcset parser; fail explicitly rather than omit them.
            if "data:" in attrs["srcset"]:
                raise ValueError("Data URL in srcset is not supported by the integrity checker")
            self.references.extend(part.strip().split()[0] for part in attrs["srcset"].split(",") if part.strip())
        if tag == "meta" and attrs.get("http-equiv", "").lower() == "refresh":
            match = re.search(r"url\s*=\s*(.*)", attrs.get("content", ""), re.I)
            if match:
                self.references.append(match[1].strip(" '\""))
        if "style" in attrs:
            self.inline_css.append(attrs["style"])
        if tag == "style":
            self.style_depth = True

    handle_startendtag = handle_starttag

    def handle_endtag(self, tag):
        if tag == "style":
            self.style_depth = False

    def handle_data(self, data):
        if self.style_depth:
            self.inline_css.append(data)


def css_references(source):
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    # Escaped CSS paths are deliberately rejected to avoid an incorrect successful check.
    patterns = [r"url\(\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s)]*))\s*\)",
                r"@import\s+(?:\"([^\"]*)\"|'([^']*)')"]
    references = [next(v for v in match if v) for pattern in patterns
                  for match in re.findall(pattern, source, re.I)]
    if any("\\" in ref for ref in references):
        raise ValueError("Escaped CSS URLs must be replaced with percent-encoded URLs")
    return references


def resolve_reference(page, reference, files, documents):
    """Return an external URL, or raise for a broken local URL (even on Windows)."""
    if "\\" in reference:
        raise ValueError("backslash in URL")
    url = urlsplit(urljoin(BASE + page, reference))
    if url.scheme not in {"http", "https"}:
        if url.scheme in {"mailto", "tel", "data", "blob"}:
            return None
        raise ValueError(f"unsupported URL scheme: {url.scheme}")
    if url.netloc.lower() != urlsplit(BASE).netloc.lower():
        return url.geturl()
    path = unquote(url.path, errors="strict")
    if not path.startswith(CONFIG["basePath"]):
        raise ValueError(f"escapes Pages base path {CONFIG['basePath']}: {path}")
    target = path[len(CONFIG["basePath"]):]
    if any(part in {"..", "."} for part in target.split("/")):
        raise ValueError("encoded path traversal")
    if not target or target.endswith("/"):
        target += "index.html"
    if target not in files:
        hint = next((f for f in files if f.casefold() == target.casefold()), None)
        raise ValueError(f"missing local file: {target}" + (f" (case mismatch; actual: {hint})" if hint else ""))
    if url.fragment and target in documents:
        anchor = unquote(url.fragment, errors="strict")
        if anchor not in documents[target].ids:
            raise ValueError(f"missing anchor: {target}#{anchor}")
    return None


def check(root=ROOT):
    files = inventory(root)
    documents = {f: Document((root / f).read_text(encoding="utf-8"))
                 for f in files if f.lower().endswith(".html")}
    if not documents:
        raise ValueError("No HTML pages found")
    errors, external = [], set()
    for page, document in documents.items():
        errors.extend(f"{page}: duplicate id {value}" for value in document.duplicates)
        for reference, integrity in document.resources:
            if not integrity:
                continue  # Missing attributes are errors in HTML Validate.
            try:
                if resolve_reference(page, reference, files, documents):
                    continue
                asset = unquote(urlsplit(urljoin(BASE + page, reference)).path)[len(CONFIG["basePath"]):]
                if not valid_integrity((root / asset).read_bytes(), integrity):
                    errors.append(f"{page}: stale or invalid SRI for {reference}; run npm run update:sri")
            except ValueError as error:
                errors.append(f"{page}: {reference!r}: {error}")
    for file in files:
        references = []
        if file in documents:
            references = documents[file].references[:]
            for css in documents[file].inline_css:
                references.extend(css_references(css))
        elif file.lower().endswith(".css"):
            references = css_references((root / file).read_text(encoding="utf-8"))
        for ref in references:
            try:
                remote = resolve_reference(file, ref, files, documents)
                if remote:
                    external.add(remote)
            except ValueError as error:
                errors.append(f"{file}: {ref!r}: {error}")
    report = {"baseUrl": BASE, "pages": sorted(documents), "files": files,
              "errors": errors, "externalUrls": sorted(external)}
    return report


def valid_integrity(content, integrity):
    candidates = [token.split("-", 1) for token in integrity.split() if "-" in token]
    supported = [(algorithm, value) for algorithm, value in candidates
                 if algorithm in {"sha256", "sha384", "sha512"}]
    if not supported:
        return False
    # Like the browser, require a match from the strongest provided algorithm.
    strongest = max(algorithm for algorithm, _ in supported)
    actual = base64.b64encode(hashlib.new(strongest, content).digest()).decode("ascii")
    return any(value == actual for algorithm, value in supported if algorithm == strongest)


def update_sri(root=ROOT):
    files = inventory(root)
    # Hash the same LF bytes that Git checks out on Linux (see .gitattributes).
    for file in files:
        if file.lower().endswith(".css"):
            content = (root / file).read_text(encoding="utf-8")
            with (root / file).open("w", encoding="utf-8", newline="\n") as output:
                output.write(content)
    documents = {file: Document((root / file).read_text(encoding="utf-8"))
                 for file in files if file.lower().endswith(".html")}
    for page in documents:
        def replace(match):
            tag = match.group(0)
            resources = Document(tag).resources
            if not resources:
                return tag
            reference, _ = resources[0]
            if resolve_reference(page, reference, files, documents):
                return tag  # No fetching or changing third-party SRI.
            asset = unquote(urlsplit(urljoin(BASE + page, reference)).path)[len(CONFIG["basePath"]):]
            digest = base64.b64encode(hashlib.sha384((root / asset).read_bytes()).digest()).decode("ascii")
            tag = re.sub(r'''\s+integrity\s*=\s*(?:"[^"]*"|'[^']*')''', "", tag, flags=re.I)
            return tag[:-1] + f' integrity="sha384-{digest}">'
        source = (root / page).read_text(encoding="utf-8")
        source = re.sub(r"<(?:link|script)\b[^>]*>", replace, source, flags=re.I)
        with (root / page).open("w", encoding="utf-8", newline="\n") as output:
            output.write(source)
    print(f"Updated local stylesheet/script SRI in {len(documents)} HTML pages")


def build():
    files = inventory()
    destination = ROOT / "dist"
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir()
    for file in files:
        target = destination / file
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / file, target)
    (destination / ".nojekyll").touch()
    save_report("public-files.json", {"files": files})
    print(f"Built {len(files)} public files in dist (plus .nojekyll)")


def external_check(url):
    last_error = None
    for method in ("HEAD", "GET"):
        try:
            request = urllib.request.Request(url, method=method, headers={"User-Agent": "about-me-link-check/1.0"})
            with urllib.request.urlopen(request, timeout=10) as response:
                return {"url": url, "status": response.status, "warning": None}
        except (OSError, ValueError) as error:
            last_error = str(error)
    return {"url": url, "warning": last_error}


def save_report(name, content):
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / name).write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "check"
    if command == "build":
        build()
        return
    if command == "sri":
        update_sri()
        return
    report = check()
    save_report("integrity.json", report)
    for page in report["pages"]:
        print(f"PAGE {page}")
    for error in report["errors"]:
        print(f"ERROR {error}")
    if report["errors"]:
        raise SystemExit(1)
    if command == "external":
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(external_check, report["externalUrls"]))
        save_report("external-links.json", results)
        for result in results:
            if result["warning"]:
                message = f"{result['url']}: {result['warning']}"
                print(f"WARNING {message}")
                if "GITHUB_ACTIONS" in __import__("os").environ:
                    print("::warning::" + message.replace("%", "%25").replace("\n", "%0A").replace("\r", "%0D"))
    elif command != "check":
        raise ValueError(f"Unknown command: {command}")
    print(f"PASS: {len(report['pages'])} pages, {len(report['files'])} public files; no local errors")


if __name__ == "__main__":
    main()
