document.addEventListener("DOMContentLoaded", function () {
  // Copy-to-clipboard buttons: any element with data-copy-target pointing to an element id
  document.querySelectorAll("[data-copy-target]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const targetId = btn.getAttribute("data-copy-target");
      const el = document.getElementById(targetId);
      if (!el) return;
      const text = el.innerText || el.value || "";
      navigator.clipboard.writeText(text).then(function () {
        const original = btn.innerHTML;
        btn.innerHTML = '<i class="bi bi-check2"></i> Copied';
        setTimeout(function () { btn.innerHTML = original; }, 1500);
      });
    });
  });

  // Innovation score badge: reads data-score attribute, sets CSS variable
  document.querySelectorAll("[data-score]").forEach(function (el) {
    const score = parseFloat(el.getAttribute("data-score")) || 0;
    el.style.setProperty("--score", score);
  });
});
