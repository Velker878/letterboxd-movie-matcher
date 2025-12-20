/* document.addEventListener("DOMContentLoaded", () => {
  const usernameContainer = document.getElementById("username-fields");
  const compareBtn = document.getElementById("compare-btn");
  const clearBtn = document.getElementById("clear-btn");
  const results = document.getElementById("results");
  const loading = document.getElementById("loading");

  if (!usernameContainer || !compareBtn || !clearBtn || !results || !loading) {
    console.error("[app.js] Missing required DOM elements");
    return;
  }

  // Add new input on ENTER
  usernameContainer.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();

      const newInput = document.createElement("input");
      newInput.type = "text";
      newInput.placeholder = "Username";
      newInput.className = "username-input";

      usernameContainer.appendChild(newInput);
      newInput.focus();
    }
  });

  // Clear inputs + results
  clearBtn.addEventListener("click", () => {
    usernameContainer.innerHTML = `
      <input type="text" placeholder="Username" class="username-input" />
    `;
    results.innerHTML = "";
  });

  // Compare watchlists
  compareBtn.addEventListener("click", async () => {
    const inputs = document.querySelectorAll(".username-input");
    const usernames = [...inputs].map((i) => i.value.trim()).filter(Boolean);

    if (usernames.length < 2) {
      alert("Enter at least two usernames");
      return;
    }

    // Show loading
    loading.classList.remove("hidden");
    results.innerHTML = "";

    const query = usernames
      .map((u) => `usernames=${encodeURIComponent(u)}`)
      .join("&");

    try {
      const res = await fetch(`/compare/?${query}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      displayResults(data);
    } catch (err) {
      console.error(err);
      results.innerHTML = `<p style="color:#ff4444">Error fetching data.</p>`;
    } finally {
      loading.classList.add("hidden");
    }
  });

  function displayResults(data) {
    if (data.invalid_usernames?.length) {
      results.innerHTML += `
        <p style="color:#ff4444">
          Invalid usernames: ${data.invalid_usernames.join(", ")}
        </p>
      `;
    }

    if (!data.common_films || data.common_films.length === 0) {
      results.innerHTML += `<p>No films in common.</p>`;
      return;
    }

    let html = `
      <h2 style="text-align:center;">Movies in Common</h2>
      <div class="film-grid">
    `;

    data.common_films.forEach((film) => {
      html += `
        <div class="film-card">
          <a href="${film.link}" target="_blank" rel="noopener">
            <img src="${film.poster_image}" alt="${film.title}">
          </a>
          <p>${film.title}</p>
          <div class="genres">
            ${film.genres
              .map((g) => `<span class="badge">${g}</span>`)
              .join("")}
          </div>
        </div>
      `;
    });

    html += "</div>";
    results.innerHTML += html;
  }
});

*/
