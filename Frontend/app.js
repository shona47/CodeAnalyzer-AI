window.currentLang = "python";

document.addEventListener("click", async function (e) {

  // -------------------------------
  // LANGUAGE SWITCH
  // -------------------------------
  if (e.target.closest(".language-toggle button")) {

    const btn = e.target.closest("button");
    const buttons = document.querySelectorAll(".language-toggle button");
    const header = document.querySelector(".file-name");

    buttons.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    const lang = btn.dataset.lang.toLowerCase();
    window.currentLang = lang;

    if (header) {
      header.textContent = lang === "c" ? "main.c" : "script.py";
    }
  }

  // -------------------------------
  // ANALYZE BUTTON
  // -------------------------------
  if (e.target.classList.contains("analyze-btn")) {

    const codeArea = document.querySelector("#codeArea");
    const inputArea = document.querySelector("#userInput");
    const result = document.querySelector(".result");

    if (!codeArea.value.trim()) {
      result.innerHTML = "❌ Please enter code first.";
      return;
    }

    try {

      const response = await fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          language: window.currentLang,
          code: codeArea.value,
          input: inputArea ? inputArea.value : ""
        })
      });

      const data = await response.json();

      const cleanOutput =
        data.output && data.output.trim() !== ""
          ? data.output
          : "No output";

      let html = "";

      // SUCCESS
      if (data.success) {
        html += `
          <div class="success-card">
            ✅ Execution Successful
          </div>
        `;
      }

      // ERRORS
      if (data.errors && data.errors.length > 0) {
        data.errors.forEach(err => {
          html += `
            <div class="error-card">
              <div class="error-header">⚠ ${err.type}</div>
              <div class="error-message">${err.message}</div>
            </div>
          `;
        });
      }

      // OUTPUT
      html += `
        <div class="output-card">
          <strong>Program Output:</strong>
          <pre>${cleanOutput}</pre>
        </div>
      `;

      // STATS
      html += `
        <div class="stats-card">
          ⏱ Runtime: ${data.runtime || 0} ms <br>
          💾 Memory: ${data.memory || 0} KB
        </div>
      `;

      result.innerHTML = html;

    } catch (error) {
      result.innerHTML = "⚠ Backend not running!";
      console.error(error);
    }
  }

});
