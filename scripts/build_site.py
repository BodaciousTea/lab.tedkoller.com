#!/usr/bin/env python3
"""Build the static lab site from independently editable article HTML files."""

import argparse
from dataclasses import dataclass
from datetime import date
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
from urllib.parse import urljoin


class ArticleInfo(HTMLParser):
    def __init__(self):
        super().__init__()
        self.is_article = False
        self.published = None
        self.title_parts = []
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article" and "lab-article" in attrs.get("class", "").split():
            self.is_article = True
        if tag == "meta" and attrs.get("name") == "article-date":
            self.published = attrs.get("content")
        if tag == "h1" and attrs.get("id") == "article-title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == "h1":
            self.in_title = False

    def handle_data(self, value):
        if self.in_title:
            self.title_parts.append(value)


@dataclass
class Article:
    path: Path
    url: str
    title: str
    published: date
    html: str


MENU = re.compile(
    r'(<nav\b(?=[^>]*\bdata-article-menu\b)[^>]*>)(.*?)(</nav>)', re.S
)


def find_articles(source):
    articles = []
    for path in sorted(source.rglob("*.html")):
        relative = path.relative_to(source)
        if any(part.startswith((".", "_")) for part in relative.parts):
            continue
        text = path.read_text()
        info = ArticleInfo()
        info.feed(text)
        if not info.is_article:
            continue
        title = " ".join("".join(info.title_parts).split())
        if not title or not info.published:
            raise ValueError(f"{relative}: an article-title and article-date are required")
        published = date.fromisoformat(info.published)
        url = "/" + relative.as_posix()
        if url.endswith("/index.html"):
            url = url.removesuffix("index.html")
        articles.append(Article(relative, url, title, published, text))
    if not articles:
        raise ValueError("No article HTML files found")
    return sorted(articles, key=lambda item: (item.published, item.url), reverse=True)


def render_article(article, articles, origin, homepage=False, logo_svg=None):
    newest = articles[0]
    rows = []
    for item in articles:
        href = "/" if item.path == newest.path else item.url
        selected = ' aria-current="page"' if item.path == article.path else ""
        rows.append(
            f'<li><a href="{escape(href, quote=True)}"{selected}>'
            f'<span>{escape(item.title)}</span>'
            f'<time datetime="{item.published.isoformat()}">'
            f'{item.published:%m.%d.%Y}</time></a></li>'
        )

    def menu(match):
        return (
            match[1] + "\n<details>\n<summary>" + match[2].strip()
            + "</summary>\n<ul>\n" + "\n".join(rows)
            + "\n</ul>\n</details>\n" + match[3]
        )

    output, count = MENU.subn(menu, article.html)
    if count != 1:
        raise ValueError(f"{article.path}: expected one article dropdown container")
    if logo_svg:
        inner_logo = logo_svg.replace(
            '<svg ', '<svg x="0" y="2.3046875" width="44.28125" height="20.6953125" ', 1
        )
        wordmark = (
            '<span class="brand brand--lab">'
            '<svg class="brand__wordmark" viewBox="0 0 181.3359375 27.6015625" '
            'xmlns="http://www.w3.org/2000/svg" aria-label="LAB. TEDKOLLER">'
            '<a href="#lab-start" aria-label="Replay LAB. TEDKOLLER animation">'
            '<rect width="181.3359375" height="27.6015625" fill="transparent" />'
            + inner_logo +
            '<text x="45.79925" y="23" class="brand__svg-period">.</text>'
            '<text x="51.3046875" y="23" class="brand__svg-name">TEDKOLLER</text>'
            '</a></svg></span>'
        )
        output = re.sub(
            r'<button\b(?=[^>]*class="brand brand--lab")[^>]*>.*?</button>',
            lambda _: wordmark, output, flags=re.S
        )
    if article.path == newest.path:
        output = output.replace(origin + article.url, origin + "/")
    if homepage:
        # A relative image in an article's directory must still resolve at '/'.
        def rebase(match):
            value = match[3]
            if not value or value.startswith(("/", "#", "?")):
                return match[0]
            return match[1] + match[2] + urljoin(article.url, value) + match[2]
        output = re.sub(r'(\b(?:src|href|poster|action)\s*=\s*)([\"\'])(.*?)\2', rebase, output)
    return output


def build(source):
    source = Path(source).resolve()
    articles = find_articles(source)
    destination = source / "_site"
    marker = destination / ".lab-build-output"
    if destination.exists():
        if not marker.is_file():
            raise ValueError("_site exists but is not a generated lab build; move it before building")
        shutil.rmtree(destination)
    destination.mkdir()
    marker.touch()
    excluded = {"scripts", "README.md", "AGENTS.md", "index.html", "tedkoller-animation-preview.html"}
    for path in source.iterdir():
        if path.name.startswith((".", "_")) or path.name in excluded:
            continue
        target = destination / path.name
        if path.is_dir():
            shutil.copytree(path, target, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"))
        elif path.is_file():
            shutil.copy2(path, target)
    (destination / ".nojekyll").touch()
    origin = "https://" + (source / "CNAME").read_text().strip()
    logo_path = source / "images/lab-pump-triline-animated.svg"
    logo_svg = logo_path.read_text() if logo_path.exists() else None
    for article in articles:
        target = destination / article.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_article(article, articles, origin, logo_svg=logo_svg))
    (destination / "index.html").write_text(
        render_article(articles[0], articles, origin, homepage=True, logo_svg=logo_svg)
    )
    print(f"Built {len(articles)} articles. Homepage: {articles[0].path} ({articles[0].published})")
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    build(parser.parse_args().source)
