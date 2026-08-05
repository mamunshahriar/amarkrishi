/* =========================================================
   Amar Krishi - Main JavaScript
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {
  // --- Dark mode toggle (persisted in localStorage, restored on every page) ---
  const THEME_KEY = "amarkrishi-theme";
  const themeToggleBtn = document.getElementById("themeToggle");

  function applyThemeIcon() {
    if (!themeToggleBtn) return;
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    const icon = themeToggleBtn.querySelector("i");
    if (icon) icon.className = isDark ? "fa-solid fa-sun" : "fa-solid fa-moon";
  }

  applyThemeIcon(); // base.html's inline script already applied the saved theme pre-paint

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
      const isDark = document.documentElement.getAttribute("data-theme") === "dark";
      if (isDark) {
        document.documentElement.removeAttribute("data-theme");
        localStorage.setItem(THEME_KEY, "light");
      } else {
        document.documentElement.setAttribute("data-theme", "dark");
        localStorage.setItem(THEME_KEY, "dark");
      }
      applyThemeIcon();
      const settingsCheckbox = document.getElementById("darkModeCheckbox");
      if (settingsCheckbox) settingsCheckbox.checked = !isDark;
    });
  }

  // Settings page checkbox (if present) mirrors the same toggle
  const settingsCheckbox = document.getElementById("darkModeCheckbox");
  if (settingsCheckbox) {
    settingsCheckbox.checked = document.documentElement.getAttribute("data-theme") === "dark";
    settingsCheckbox.addEventListener("change", () => {
      if (settingsCheckbox.checked) {
        document.documentElement.setAttribute("data-theme", "dark");
        localStorage.setItem(THEME_KEY, "dark");
      } else {
        document.documentElement.removeAttribute("data-theme");
        localStorage.setItem(THEME_KEY, "light");
      }
      applyThemeIcon();
    });
  }

  // --- Mobile sidebar toggle ---
  const toggleBtn = document.querySelector(".mobile-toggle");
  const sidebar = document.querySelector(".sidebar");
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", () => sidebar.classList.toggle("open"));
  }

  // --- Auto-dismiss alerts ---
  document.querySelectorAll(".alert").forEach((alertBox) => {
    setTimeout(() => {
      alertBox.style.transition = "opacity 0.4s ease";
      alertBox.style.opacity = "0";
      setTimeout(() => alertBox.remove(), 400);
    }, 4000);
  });

  // --- Income vs Expense chart ---
  const ieCanvas = document.getElementById("incomeExpenseChart");
  if (ieCanvas && window.Chart) {
    new Chart(ieCanvas, {
      type: "doughnut",
      data: {
        labels: [ieCanvas.dataset.incomeLabel, ieCanvas.dataset.expenseLabel],
        datasets: [{
          data: [parseFloat(ieCanvas.dataset.income), parseFloat(ieCanvas.dataset.expense)],
          backgroundColor: ["#1b7a3d", "#f2b705"],
          borderWidth: 0,
        }],
      },
      options: { plugins: { legend: { position: "bottom" } }, cutout: "65%" },
    });
  }

  // --- Market price trend chart (loaded on market page) ---
  document.querySelectorAll("[data-trend-crop]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const cropId = btn.dataset.trendCrop;
      fetch(`/api/market-trend/${cropId}`)
        .then((res) => res.json())
        .then((data) => {
          const canvas = document.getElementById("trendChart");
          if (!canvas) return;
          if (window.trendChartInstance) window.trendChartInstance.destroy();
          window.trendChartInstance = new Chart(canvas, {
            type: "line",
            data: {
              labels: data.labels,
              datasets: [{
                label: "Price (৳/kg)",
                data: data.prices,
                borderColor: "#1b7a3d",
                backgroundColor: "rgba(27,122,61,0.08)",
                tension: 0.35,
                fill: true,
              }],
            },
            options: { plugins: { legend: { display: false } } },
          });
        });
    });
  });

  // --- Crop progress bar animation ---
  document.querySelectorAll(".progress-fill").forEach((el) => {
    const target = el.dataset.value || 0;
    requestAnimationFrame(() => { el.style.width = target + "%"; });
  });

  // NOTE: the AI Assistant chat form is wired directly in templates/ai_assistant.html
  // (it needs page-specific translated strings), not here.
});
