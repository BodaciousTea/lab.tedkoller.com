# Ted Koller Lab

This is a plain static site. Preview it with any local web server, such as `python3 -m http.server 8765`, then open http://localhost:8765.

## Article dropdown

Edit the `articles` list in `js/article-menu.js` to add, rename, reorder, or date articles. Every article page loads this shared dropdown at the article title in its original position. The current title and selected link are determined from the page's heading and canonical URL.

The dropdown works on desktop and mobile, uses native details/summary controls, and closes on Escape or clicking outside it. Its opaque panel keeps the links readable over the article. No build step or template processor is required.
