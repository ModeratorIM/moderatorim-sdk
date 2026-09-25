// ModeratorIM night-mode switcher. Toggles body.light/body.dark, drives Beer CSS's own
// ui("mode", ...) so its components re-theme, and persists the choice in localStorage.
//
// The wizard swaps the whole <body> via htmx when navigating between steps, which destroys the
// old toggle button and its listener AND resets the body class. So: (1) the click is DELEGATED
// on document (survives swaps), and (2) the saved mode is RE-APPLIED after every htmx swap and
// on load, so the theme persists across navigation.
(function () {
  "use strict";
  var KEY = "mim-theme";

  function saved() {
    var v = localStorage.getItem(KEY);
    return v === "light" || v === "dark" ? v : null;
  }

  function current() {
    return saved() || (document.body.classList.contains("dark") ? "dark" : "light");
  }

  function apply(mode) {
    var body = document.body;
    body.classList.remove("light", "dark");
    body.classList.add(mode);
    if (typeof window.ui === "function") {
      try {
        window.ui("mode", mode);
      } catch (e) {
        /* Beer CSS not ready; the body class alone still themes our surfaces. */
      }
    }
    var icon = document.querySelector("[data-mim-theme-icon]");
    if (icon) icon.textContent = mode === "dark" ? "light_mode" : "dark_mode";
  }

  // Delegated toggle: works no matter when the button entered the DOM.
  document.addEventListener("click", function (e) {
    var btn = e.target.closest ? e.target.closest("[data-mim-theme-toggle]") : null;
    if (!btn) return;
    var next = current() === "dark" ? "light" : "dark";
    localStorage.setItem(KEY, next);
    apply(next);
  });

  // Re-apply the saved mode after every htmx swap (a step navigation replaces the body) and once
  // on initial load — otherwise a swap resets the class and the icon.
  function reapply() {
    apply(current());
  }
  document.addEventListener("htmx:afterSettle", reapply);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", reapply);
  } else {
    reapply();
  }
})();
