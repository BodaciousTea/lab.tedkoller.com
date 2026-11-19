from pathlib import Path
import tempfile
import unittest

from build_site import build


class HomepageBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name)
        (self.source / "CNAME").write_text("lab.tedkoller.com")

    def article(self, slug, published, body=""):
        path = self.source / slug / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f'<html><head><meta name="article-date" content="{published}">'
            f'<link rel="canonical" href="https://lab.tedkoller.com/{slug}/">'
            '</head><body><article class="lab-article">'
            f'<nav data-article-menu><h1 id="article-title">{slug}</h1></nav>'
            f'{body}</article></body></html>'
        )
        return path

    def test_new_article_automatically_replaces_homepage_without_changing_sources(self):
        first = self.article("first", "2026-11-01", "First article")
        original = first.read_text()
        output = build(self.source)
        self.assertIn("First article", (output / "index.html").read_text())
        self.article("second", "2026-11-02", "Second article")
        output = build(self.source)
        homepage = (output / "index.html").read_text()
        self.assertIn("Second article", homepage)
        self.assertNotIn("First article", homepage)
        self.assertEqual(first.read_text(), original)
        self.assertFalse((self.source / "index.html").exists())

    def test_editing_old_article_does_not_make_it_the_newest_publication(self):
        self.article("newer", "2026-11-02", "Newest published article")
        self.article("older", "2026-11-01", "An edit made afterwards")
        output = build(self.source)
        self.assertIn("Newest published article", (output / "index.html").read_text())

    def test_relative_assets_and_fragment_links_work_at_root(self):
        self.article("article", "2026-11-02", '<img src="graph.svg"><a href="#section">Section</a>')
        output = build(self.source)
        homepage = (output / "index.html").read_text()
        self.assertIn('src="/article/graph.svg"', homepage)
        self.assertIn('href="#section"', homepage)
        self.assertIn('href="https://lab.tedkoller.com/"', homepage)

    def test_menus_are_plain_html_and_newest_article_links_to_root(self):
        self.article("older", "2026-11-01")
        self.article("latest", "2026-11-12")
        output = build(self.source)
        older = (output / "older/index.html").read_text()
        self.assertIn('<details>', older)
        self.assertIn('<a href="/">', older)
        self.assertIn('11.12.2026</time>', older)
        self.assertIn('<a href="/older/" aria-current="page">', older)
        self.assertNotIn('<script', older)

    def test_missing_date_fails_instead_of_silently_publishing_wrong_article(self):
        path = self.article("undated", "2026-11-02")
        path.write_text(path.read_text().replace('name="article-date"', 'name="other"'))
        with self.assertRaisesRegex(ValueError, "article-date"):
            build(self.source)

    def test_logo_is_an_inline_native_animation_link(self):
        path = self.article("article", "2026-11-02")
        path.write_text(path.read_text().replace(
            '<body>',
            '<body><button class="brand brand--lab"><img class="brand__lab"></button>'
        ))
        images = self.source / "images"
        images.mkdir()
        (images / "lab-pump-triline-animated.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"><animate id="lab-start" '
            'attributeName="opacity" from="0" to="1" dur="1s" begin="0s;indefinite"/></svg>'
        )
        output = build(self.source)
        homepage = (output / "index.html").read_text()
        self.assertIn('<a href="#lab-start"', homepage)
        self.assertIn('id="lab-start"', homepage)
        self.assertNotIn('<script', homepage)
        self.assertNotIn('<img class="brand__lab"', homepage)


if __name__ == "__main__":
    unittest.main()
