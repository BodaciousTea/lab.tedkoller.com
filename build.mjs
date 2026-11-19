// Publishing only: articles remain the source; visitors receive finished HTML.
import { readdirSync, readFileSync, writeFileSync, existsSync, mkdirSync, rmSync, cpSync } from "node:fs";
import { resolve, dirname, relative, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(process.argv[2] || dirname(fileURLToPath(import.meta.url)));
const articleRoot = join(root, "articles");
const out = join(root, "_site");
const origin = `https://${readFileSync(join(root, "CNAME"), "utf8").trim()}`;
const walk = (dir) => readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
  if (/^[._]/.test(entry.name) || entry.name === "node_modules") return [];
  const path = join(dir, entry.name);
  return entry.isDirectory() ? walk(path) : path.endsWith(".html") ? [path] : [];
});
const articles = walk(articleRoot).flatMap((path) => {
  const html = readFileSync(path, "utf8");
  if (!/<article\b[^>]*class="lab-article"/.test(html)) return [];
  const date = html.match(/<meta\s+name="article-date"\s+content="(\d{4}-\d{2}-\d{2})"/)?.[1];
  const title = html.match(/<h1\b[^>]*id="article-title"[^>]*>([\s\S]*?)<\/h1>/)?.[1].replace(/\s+/g, " ").trim();
  if (!date || !title || new Date(date).toISOString().slice(0, 10) !== date) throw Error(`Missing/invalid title or article-date: ${path}`);
  const file = relative(articleRoot, path).replaceAll("\\", "/");
  return [{ file, html, date, title, url: `/${file}`.replace(/index\.html$/, "") }];
}).sort((a, b) => b.date.localeCompare(a.date) || b.url.localeCompare(a.url));
if (!articles.length) throw Error("No articles found");
if (existsSync(out) && !existsSync(join(out, ".lab-build-output"))) throw Error("_site is not a generated build; move it first");
rmSync(out, { recursive: true, force: true });
mkdirSync(out);
writeFileSync(join(out, ".lab-build-output"), "");
writeFileSync(join(out, ".nojekyll"), "");
for (const name of readdirSync(root)) {
  if (/^[._]/.test(name) || ["articles", "build.mjs", "README.md", "AGENTS.md", "index.html", "node_modules"].includes(name)) continue;
  cpSync(join(root, name), join(out, name), { recursive: true });
}
for (const name of readdirSync(articleRoot)) {
  cpSync(join(articleRoot, name), join(out, name), { recursive: true });
}
for (const article of articles) {
  const rows = articles.map((item) => `<li><a href="${item === articles[0] ? "/" : item.url}"${item === article ? ' aria-current="page"' : ""}><span>${item.title}</span><time datetime="${item.date}">${item.date.slice(5, 7)}.${item.date.slice(8)}.${item.date.slice(0, 4)}</time></a></li>`).join("\n");
  let html = article.html.replace(/(<nav\b[^>]*data-article-menu[^>]*>)([\s\S]*?)(<\/nav>)/, (_, start, title, end) => `${start}<details><summary>${title.trim()}</summary><ul>${rows}</ul></details>${end}`);
  if (article === articles[0]) html = html.replaceAll(origin + article.url, origin + "/");
  writeFileSync(join(out, article.file), html);
  if (article !== articles[0]) continue;
  html = html.replace(/(\b(?:src|href|poster)\s*=\s*)(["'])(.*?)\2/g, (whole, attr, quote, value) => {
    if (!value || /^[/#?]|^[a-z][a-z\d+.-]*:/i.test(value)) return whole;
    const url = new URL(value, origin + article.url);
    return `${attr}${quote}${url.pathname}${url.search}${url.hash}${quote}`;
  });
  writeFileSync(join(out, "index.html"), html);
}
console.log(`Homepage: ${articles[0].file} (${articles[0].date})`);
