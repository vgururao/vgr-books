// book-nav.js — keyboard navigation for online books
// Arrow keys trigger the float-nav prev/next buttons.
// Pairs with book-nav.css.
(function () {
  document.addEventListener("keydown", function (e) {
    if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
    if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
    var a;
    if (e.key === "ArrowLeft")  a = document.querySelector(".float-nav-prev");
    else if (e.key === "ArrowRight") a = document.querySelector(".float-nav-next");
    if (a && !a.classList.contains("disabled")) { e.preventDefault(); a.click(); }
  });
})();
