# lab.tedkoller.com

Technical work, blogs, and essays by Ted Koller. Published at https://lab.tedkoller.com.

## Local preview

From the repository root, run:

```sh
python3 -m http.server 8001
```

Open http://localhost:8001. This is a static HTML and CSS site with no build step.

## Project structure

- `index.html`: article list and home page.
- `articles/`: individual articles and their supporting assets.
- `css/lab.css`: lab page styling.
- `css/articles.css`: article styling.
- `images/`: shared images and favicon.
- `CNAME`: custom domain configuration.

## Shared styles

Pages load the main stylesheet and footer stylesheet from https://tedkoller.com. A local preview needs an internet connection to load those shared styles and fonts.
