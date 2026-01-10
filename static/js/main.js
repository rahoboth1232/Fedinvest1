document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll(".erbtn").forEach(el => {
    el.addEventListener("click", e => {
      const href = el.getAttribute("href");

      if (href === "#") {
        e.preventDefault();
      showCustomAlert("Please Contact Your Case Representative ");

      }
    });
  });
  

  function showCustomAlert(message) {
    document.querySelector(".custom-alert")?.remove();
    document.querySelector(".alert-overlay")?.remove();

    const overlay = document.createElement("div");
    overlay.className = "alert-overlay show";

    const alertBox = document.createElement("div");
    alertBox.className = "custom-alert show";
    alertBox.innerHTML = `
      <div style="text-align:center;">
        <p style="margin-bottom:10px;">${message}</p>
        <button id="closeAlert" style="padding:6px 16px;cursor:pointer;">OK</button>
      </div>
    `;

    document.body.appendChild(overlay);
    document.body.appendChild(alertBox);

    document.getElementById("closeAlert").addEventListener("click", () => {
      alertBox.remove();
      overlay.remove();
    });
  }
});

