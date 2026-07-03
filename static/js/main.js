/* =========================================================
   Amar Krishi - Main JavaScript
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {
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

  // --- AI Assistant demo chat ---
  const chatForm = document.getElementById("aiChatForm");
  if (chatForm) {
    chatForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const input = document.getElementById("aiChatInput");
      const log = document.getElementById("aiChatLog");
      if (!input.value.trim()) return;

      const userMsg = document.createElement("div");
      userMsg.className = "chat-msg user";
      userMsg.textContent = input.value;
      log.appendChild(userMsg);

      const reply = document.createElement("div");
      reply.className = "chat-msg bot";
      reply.textContent = "This is a demo AI assistant response. Connect a real model to get live farming advice.";
      setTimeout(() => log.appendChild(reply), 500);

      input.value = "";
      log.scrollTop = log.scrollHeight;
    });
  }
});
