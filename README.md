# Ted Koller Lab

Write each article in its own HTML file. Copy an existing article, replace the title and content, and set its publication date:

```html
<meta name="article-date" content="2026-11-18" />
```

On each push to `main`, GitHub runs `node build.mjs` and publishes the result. The newest publication date becomes `lab.tedkoller.com/`. Menus are generated from the article files too, so there is no separate article list or homepage to maintain. Editing an older article does not change its publication order.

To build locally, run `node build.mjs`, then serve the generated `_site/` folder with your editor's preview server. Edit the source article files, not `_site/`.

The original LAB animation uses CSS inside its SVG. The seven-line `js/logo-replay.js` helper only restarts it on page load or a logo click. No Python, packages, or frameworks are needed.
