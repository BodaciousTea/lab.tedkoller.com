(() => {
  const brand = document.querySelector(".brand--lab");
  const logo = brand?.querySelector(".brand__lab");
  if (logo) {
    const source = logo.getAttribute("src");
    let replay = 0;
    brand.setAttribute("aria-label", "LAB. TEDKOLLER — replay animation");
    brand.addEventListener("click", (event) => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      const url = new URL(source, window.location.href);
      url.searchParams.set("replay", ++replay);
      logo.src = url.href;
    });
  }

  // Maintain the article selection here once for every page.
  const articles = [
    { title: "An Inquiry into Film Sharpness", url: "/an-inquiry-into-film-sharpness/", date: "2026-11-12" },
    { title: "Dolor sit amet", url: "/dolor-sit-amet/", date: "2026-11-12" },
    { title: "Consectetur adipiscing", url: "/consectetur-adipiscing/", date: "2026-11-12" },
  ];

  const container = document.querySelector("[data-article-menu]");
  if (!container) return;

  const canonical = document.querySelector('link[rel="canonical"]');
  const currentPath = canonical ? new URL(canonical.href).pathname : window.location.pathname;
  const current = articles.find((article) => article.url === currentPath);
  const details = document.createElement("details");
  const summary = document.createElement("summary");
  const articleTitle = document.getElementById("article-title");
  if (articleTitle) {
    summary.append(articleTitle);
  } else {
    summary.textContent = current?.title || "Articles";
  }

  const list = document.createElement("ul");
  articles.forEach((article) => {
    const item = document.createElement("li");
    const link = document.createElement("a");
    link.href = article.url;
    if (article.url === currentPath) link.setAttribute("aria-current", "page");

    const title = document.createElement("span");
    title.textContent = article.title;
    const date = document.createElement("time");
    date.dateTime = article.date;
    const [year, month, day] = article.date.split("-");
    date.textContent = `${month}.${day}.${year}`;
    link.setAttribute("aria-label", `${article.title}, ${date.textContent}`);
    link.append(title, date);
    item.append(link);
    list.append(item);
  });

  details.append(summary, list);
  container.replaceChildren(details);

  document.addEventListener("click", (event) => {
    if (!container.contains(event.target)) details.open = false;
  });
  details.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && details.open) {
      details.open = false;
      summary.focus();
      event.preventDefault();
    }
  });
})();
