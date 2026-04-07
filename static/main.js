// ── Delete confirmation ──────────────────────────
function confirmDelete(btn) {
  if (confirm("Are you sure you want to delete this student? This cannot be undone.")) {
    btn.closest("form").submit();
  }
}

// ── Auto-hide flash messages after 4 seconds ────
document.addEventListener("DOMContentLoaded", () => {
  const flashes = document.querySelectorAll(".flash");
  flashes.forEach(flash => {
    setTimeout(() => {
      flash.style.transition = "opacity 0.5s, transform 0.5s";
      flash.style.opacity = "0";
      flash.style.transform = "translateY(-6px)";
      setTimeout(() => flash.remove(), 500);
    }, 4000);
  });
});
