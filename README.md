# Ted Koller Lab

## Write an article

Keep each article in its own HTML file, such as `an-inquiry-into-film-sharpness/index.html`. Copy an existing article to start a new one, replace its content and title, and set its publication date in the head:

```html
<meta name="article-date" content="2026-11-18" />
```

Use the actual publication date, not the date you last edited it. The newest publication date becomes the homepage. Article pages need the existing `lab-article` element and the `article-title` heading. No central article list needs editing. If two articles have the same publication date, the path breaks the tie consistently.

## Preview

```sh
python3 scripts/build_site.py
python3 -m http.server 8765 --directory _site
```

Open http://localhost:8765. The generated `_site/` folder contains the finished website. Never edit its files or create a separate source `index.html`: the build always creates the homepage from the newest article. Relative images are adjusted for the homepage automatically.

The build also creates the article dropdown on every article page. The homepage and article switching work without browser JavaScript. The logo replays using native SVG animation. No browser JavaScript is used.

## Publish

The Pages workflow builds and deploys `_site/` on every push to `main`. Set the repository's **Settings → Pages → Build and deployment → Source** to **GitHub Actions** once when enabling this workflow. Do not publish the raw source folder with the previous branch-based Pages setup.
