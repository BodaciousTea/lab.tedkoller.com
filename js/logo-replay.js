const logo = document.querySelector(".brand__lab");
if (logo) {
  const source = logo.getAttribute("src");
  const replay = () => { logo.src = `${source}?replay=${Date.now()}`; };
  window.addEventListener("pageshow", replay);
  document.querySelector(".brand--lab").addEventListener("click", replay);
}
