#!/usr/bin/env python3
"""Validate the generated public SEO output. Run `npm run build` first."""

from __future__ import annotations

from collections import defaultdict
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import struct
import unittest
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
ORIGIN = "https://oh-my-health-data.com"
ROUTES = {"/": "index.html", "/sources/": "sources/index.html"}
SOCIAL_IMAGES = {"/": "/og/home.png", "/sources/": "/og/sources.png"}


class Document(HTMLParser):
    """Keep duplicate elements and rendered text without executing scripts."""

    def __init__(self, source: str) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, list[str]] = defaultdict(list)
        self.links: list[dict[str, str]] = []
        self.anchors: list[dict[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.titles: list[str] = []
        self.headings: list[str] = []
        self.json_ld: list[str] = []
        self.languages: list[str] = []
        self.charsets: list[str] = []
        self.visible: list[str] = []
        self.stack: list[tuple[str, bool]] = []
        self.capture: tuple[str, list[str]] | None = None
        self.feed(source)
        self.close()

    def handle_starttag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        attrs = {key.lower(): value or "" for key, value in attributes}
        hidden = (
            any(item[1] for item in self.stack)
            or tag in {"script", "style", "template", "noscript", "head"}
            or "hidden" in attrs
            or attrs.get("aria-hidden", "").lower() == "true"
        )
        if tag == "html":
            self.languages.append(attrs.get("lang", ""))
        elif tag == "meta":
            for key in ("name", "property"):
                if key in attrs:
                    self.meta[attrs[key].lower()].append(attrs.get("content", ""))
            if "charset" in attrs:
                self.charsets.append(attrs["charset"].lower())
        elif tag == "link":
            self.links.append(attrs)
        elif tag == "a" and not hidden:
            self.anchors.append(attrs)
        elif tag in {"img", "source"}:
            self.images.append(attrs)
        if tag in {"title", "h1"}:
            self.capture = (tag, [])
        elif tag == "script" and attrs.get("type", "").lower() == "application/ld+json":
            self.capture = ("json_ld", [])
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.stack.append((tag, hidden))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if self.capture and (
            self.capture[0] == tag or (self.capture[0] == "json_ld" and tag == "script")
        ):
            kind, chunks = self.capture
            value = "".join(chunks)
            if kind == "json_ld":
                self.json_ld.append(value)
            elif kind == "title":
                self.titles.append(value.strip())
            else:
                self.headings.append(value.strip())
            self.capture = None
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.capture[1].append(data)
        if not any(item[1] for item in self.stack):
            self.visible.append(data)


def walk_json(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def has_type(node: dict, expected: str) -> bool:
    value = node.get("@type", [])
    return expected in (value if isinstance(value, list) else [value])


class SeoOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not BUILD.is_dir():
            raise AssertionError(f"Missing {BUILD}; run `npm run build` before SEO tests.")

    def document(self, relative: str) -> Document:
        path = BUILD / relative
        self.assertTrue(path.is_file(), f"Missing built page: {path}; run `npm run build`.")
        try:
            return Document(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError as error:
            self.fail(f"{path} is not valid UTF-8: {error}")

    def single_meta(self, doc: Document, key: str, page: str) -> str:
        values = doc.meta[key]
        self.assertEqual(len(values), 1, f"{page}: expected exactly one {key}, found {values!r}")
        self.assertTrue(values[0].strip(), f"{page}: {key} must not be empty")
        return values[0]

    def canonical_url(self, value: str, expected: str, label: str) -> None:
        parsed = urlsplit(value)
        self.assertEqual(value, expected, f"{label}: expected {expected!r}, got {value!r}")
        self.assertEqual((parsed.scheme, parsed.netloc), ("https", "oh-my-health-data.com"), label)
        self.assertFalse(parsed.query or parsed.fragment, f"{label}: query/hash is not canonical")
        self.assertTrue(parsed.path.endswith("/"), f"{label}: canonical page path needs a trailing slash")

    def local_asset(self, reference: str, label: str, page: str = "/") -> Path | None:
        if reference.startswith("data:"):
            return None
        parsed = urlsplit(urljoin(ORIGIN + page, reference))
        if parsed.netloc != "oh-my-health-data.com":
            return None
        path = BUILD / unquote(parsed.path).lstrip("/")
        self.assertTrue(path.resolve().is_relative_to(BUILD.resolve()), f"{label}: asset escapes build")
        self.assertTrue(path.is_file(), f"{label}: referenced asset is missing: {path}")
        return path

    def png_size(self, path: Path, expected: tuple[int, int], label: str) -> None:
        self.assertTrue(path.is_file(), f"{label}: missing PNG: {path}")
        data = path.read_bytes()
        self.assertGreaterEqual(len(data), 33, f"{label}: truncated PNG: {path}")
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n", f"{label}: invalid PNG signature: {path}")
        self.assertEqual(data[8:16], b"\x00\x00\x00\rIHDR", f"{label}: missing PNG IHDR: {path}")
        self.assertEqual(struct.unpack(">II", data[16:24]), expected, f"{label}: wrong PNG dimensions: {path}")

    def test_public_pages_have_unique_complete_metadata(self) -> None:
        titles, descriptions = [], []
        for route, relative in ROUTES.items():
            with self.subTest(route=route):
                doc = self.document(relative)
                self.assertEqual(doc.languages, ["ko"], f"{route}: expected one <html lang='ko'>")
                self.assertEqual(doc.charsets, ["utf-8"], f"{route}: expected one UTF-8 charset")
                self.assertEqual(len(doc.titles), 1, f"{route}: duplicate or missing title: {doc.titles!r}")
                self.assertTrue(doc.titles[0], f"{route}: empty title")
                self.assertEqual(len(doc.headings), 1, f"{route}: expected one H1: {doc.headings!r}")
                self.assertTrue(doc.headings[0], f"{route}: empty H1")
                description = self.single_meta(doc, "description", route)
                canonical = [link.get("href", "") for link in doc.links if "canonical" in link.get("rel", "").lower().split()]
                self.assertEqual(len(canonical), 1, f"{route}: duplicate or missing canonical: {canonical!r}")
                self.canonical_url(canonical[0], ORIGIN + route, f"{route} canonical")
                expected = {
                    "og:title": doc.titles[0], "og:description": description,
                    "og:type": "website", "og:url": canonical[0], "og:locale": "ko_KR",
                    "og:image": ORIGIN + SOCIAL_IMAGES[route],
                    "og:image:width": "1200", "og:image:height": "630",
                    "twitter:card": "summary_large_image", "twitter:title": doc.titles[0],
                    "twitter:description": description, "twitter:image": ORIGIN + SOCIAL_IMAGES[route],
                }
                for key, value in expected.items():
                    self.assertEqual(self.single_meta(doc, key, route), value, f"{route}: {key} disagrees with page metadata")
                for key in ("og:site_name", "og:image:alt", "twitter:image:alt"):
                    self.single_meta(doc, key, route)
                for name in ("robots", "googlebot", "bingbot"):
                    for value in doc.meta[name]:
                        self.assertFalse(re.search(r"\b(?:noindex|none)\b", value, re.I), f"{route}: {name} prevents indexing: {value}")
                titles.append(doc.titles[0])
                descriptions.append(description)
        if len(titles) == len(ROUTES):
            self.assertEqual(len(set(titles)), len(ROUTES), "Public routes must have distinct titles")
            self.assertEqual(len(set(descriptions)), len(ROUTES), "Public routes must have distinct descriptions")

    def test_social_images_and_referenced_assets_exist(self) -> None:
        for route, reference in SOCIAL_IMAGES.items():
            with self.subTest(route=route):
                for directory in (ROOT / "static", BUILD):
                    self.png_size(directory / reference.lstrip("/"), (1200, 630), route)
                doc = self.document(ROUTES[route])
                for image in doc.images:
                    if image.get("src"):
                        self.local_asset(image["src"], f"{route} image", route)
                    for candidate in image.get("srcset", "").split(","):
                        if candidate.strip() and not image.get("srcset", "").startswith("data:"):
                            self.local_asset(candidate.strip().split()[0], f"{route} srcset", route)
                for link in doc.links:
                    rel = link.get("rel", "").lower().split()
                    if any(item in rel for item in ("icon", "apple-touch-icon", "mask-icon")):
                        path = self.local_asset(link.get("href", ""), f"{route} icon", route)
                        if path and path.suffix.lower() == ".png":
                            declared = link.get("sizes", "")
                            match = re.fullmatch(r"(\d+)x(\d+)", declared)
                            size = tuple(map(int, match.groups())) if match else ((180, 180) if "apple-touch-icon" in rel else (48, 48))
                            self.png_size(path, size, f"{route} icon")

    def test_json_ld_graph_matches_page_and_site_urls(self) -> None:
        for route, relative in ROUTES.items():
            with self.subTest(route=route):
                doc = self.document(relative)
                self.assertEqual(len(doc.json_ld), 1, f"{route}: expected one JSON-LD graph, found {len(doc.json_ld)}")
                try:
                    schema = json.loads(doc.json_ld[0])
                except (json.JSONDecodeError, IndexError) as error:
                    self.fail(f"{route}: invalid JSON-LD: {error}")
                self.assertIsInstance(schema, dict, f"{route}: JSON-LD root must be an object")
                self.assertIn(schema.get("@context"), ("https://schema.org", "https://schema.org/"), f"{route}: unexpected schema context")
                graph = schema.get("@graph")
                self.assertIsInstance(graph, list, f"{route}: JSON-LD needs @graph")
                self.assertTrue(all(isinstance(node, dict) for node in graph), f"{route}: @graph contains a non-object")
                for kind in ("WebSite", "Organization"):
                    nodes = [node for node in graph if has_type(node, kind)]
                    self.assertEqual(len(nodes), 1, f"{route}: expected exactly one {kind} node")
                    if kind == "WebSite":
                        self.canonical_url(nodes[0].get("url", ""), ORIGIN + "/", f"{route} WebSite.url")
                    elif "url" in nodes[0]:
                        publisher_url = urlsplit(nodes[0]["url"])
                        self.assertEqual(publisher_url.scheme, "https", f"{route}: publisher URL must be absolute HTTPS")
                        self.assertTrue(publisher_url.netloc, f"{route}: publisher URL needs a host")
                        self.assertFalse(publisher_url.query or publisher_url.fragment, f"{route}: publisher URL contains query/hash")
                pages = [node for node in graph if has_type(node, "WebPage") or has_type(node, "CollectionPage")]
                self.assertEqual(len(pages), 1, f"{route}: expected exactly one WebPage/CollectionPage")
                if route == "/sources/":
                    self.assertTrue(has_type(pages[0], "CollectionPage"), "Sources schema must describe a CollectionPage")
                self.canonical_url(pages[0].get("url", ""), ORIGIN + route, f"{route} WebPage.url")
                nodes = list(walk_json(schema))
                defined_ids = [node["@id"] for node in nodes if "@id" in node and len(node) > 1]
                self.assertEqual(len(defined_ids), len(set(defined_ids)), f"{route}: duplicate JSON-LD entity @id")
                for node in nodes:
                    identifier = node.get("@id")
                    if identifier:
                        parsed = urlsplit(identifier)
                        self.assertEqual((parsed.scheme, parsed.netloc), ("https", "oh-my-health-data.com"), f"{route}: noncanonical @id {identifier!r}")
                        self.assertFalse(parsed.query, f"{route}: @id contains query: {identifier}")
                        if parsed.path not in ROUTES:
                            self.local_asset(identifier, f"{route} schema @id", route)
                        if len(node) == 1 and parsed.fragment:
                            self.assertIn(identifier, defined_ids, f"{route}: unresolved JSON-LD reference {identifier}")
                    for key in ("image", "logo", "contentUrl", "thumbnailUrl"):
                        value = node.get(key)
                        if isinstance(value, str):
                            self.local_asset(value, f"{route} schema {key}", route)
                        elif isinstance(value, dict) and isinstance(value.get("url"), str):
                            self.local_asset(value["url"], f"{route} schema {key}.url", route)
                breadcrumbs = [node for node in graph if has_type(node, "BreadcrumbList")]
                self.assertLessEqual(len(breadcrumbs), 1, f"{route}: duplicate BreadcrumbList")
                if route == "/sources/":
                    self.assertEqual(len(breadcrumbs), 1, "Sources schema must include its BreadcrumbList")
                    items = breadcrumbs[0].get("itemListElement", [])
                    self.assertEqual(len(items), 2, "Sources breadcrumb must contain home and sources")
                    for position, (item, expected_route) in enumerate(zip(items, ROUTES), 1):
                        self.assertEqual(item.get("position"), position, "Breadcrumb positions must be 1, 2")
                        target = item.get("item")
                        if isinstance(target, dict):
                            target = target.get("@id", target.get("url", ""))
                        self.canonical_url(target or "", ORIGIN + expected_route, f"breadcrumb {position}")

    def test_robots_allows_public_crawling_and_points_to_sitemap(self) -> None:
        path = BUILD / "robots.txt"
        self.assertTrue(path.is_file(), f"Missing {path}")
        directives = defaultdict(list)
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.split("#", 1)[0].strip()
            if ":" in line:
                key, value = line.split(":", 1)
                directives[key.lower().strip()].append(value.strip())
        self.assertIn("*", directives["user-agent"], "robots.txt needs a public User-agent: * group")
        self.assertIn("/", directives["allow"], "robots.txt needs Allow: /")
        self.assertEqual(directives["sitemap"], [ORIGIN + "/sitemap.xml"], "robots.txt needs one absolute canonical sitemap URL")
        for rule in directives["disallow"]:
            self.assertFalse(rule.startswith("/_app"), f"robots.txt blocks required application assets: {rule}")
            self.assertNotIn(rule, {"/", "/*", "/sources", "/sources/"}, f"robots.txt blocks a public page: {rule}")

    def test_sitemap_contains_only_canonical_built_public_routes(self) -> None:
        path = BUILD / "sitemap.xml"
        self.assertTrue(path.is_file(), f"Missing {path}")
        try:
            tree = ET.fromstring(path.read_bytes())
        except ET.ParseError as error:
            self.fail(f"Invalid sitemap XML: {error}")
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        self.assertEqual(tree.tag, ns + "urlset", "Expected a sitemap urlset with standard namespace")
        locations = [node.text or "" for node in tree.findall(f"{ns}url/{ns}loc")]
        expected = {ORIGIN + route for route in ROUTES}
        self.assertEqual(len(locations), len(expected), f"Sitemap must contain exactly two URLs: {locations}")
        self.assertEqual(set(locations), expected, "Sitemap has missing or unexpected canonical routes")
        for location in locations:
            self.canonical_url(location, ORIGIN + urlsplit(location).path, "sitemap loc")
        built_routes = set()
        for file in BUILD.rglob("*.html"):
            relative = file.relative_to(BUILD).as_posix()
            if relative == "404.html":
                continue
            if relative == "index.html":
                built_routes.add("/")
            elif relative.endswith("/index.html"):
                built_routes.add("/" + relative.removesuffix("index.html"))
            else:
                built_routes.add("/" + relative)
        self.assertEqual(built_routes, set(ROUTES), f"Built HTML routes drifted from sitemap contract: {sorted(built_routes)}")

    def test_static_404_has_noindex_visible_error_and_home_link(self) -> None:
        doc = self.document("404.html")
        self.assertEqual(doc.languages, ["ko"], "404 page must declare Korean language")
        self.assertEqual(doc.charsets, ["utf-8"], "404 page must declare UTF-8")
        robots = self.single_meta(doc, "robots", "/404.html")
        self.assertRegex(robots.lower(), r"\bnoindex\b", "404 page must explicitly declare noindex")
        visible = " ".join(doc.visible)
        self.assertRegex(visible, r"(?i)(404|not\s+found|찾을\s*수\s*없|존재하지\s*않|페이지가\s*없)", "404 page needs visible error text, not only a script or meta tag")
        home_links = [anchor for anchor in doc.anchors if urljoin(ORIGIN + "/404.html", anchor.get("href", "")) == ORIGIN + "/"]
        self.assertTrue(home_links, "404 page needs a visible link back to the home page")


if __name__ == "__main__":
    unittest.main()
