document.getElementById("username-fields").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();

    const container = document.getElementById("username-fields");

    const newInput = document.createElement("input");
    newInput.type = "text";
    newInput.placeholder = "Username";
    newInput.className = "username-input";

    container.appendChild(newInput);
    newInput.focus();
  }
});

// --- Compare Button Logic ---
document.getElementById("compare-btn").addEventListener("click", async () => {
  const inputs = document.querySelectorAll(".username-input");
  const usernames = [...inputs].map((i) => i.value.trim()).filter(Boolean);

  if (usernames.length < 2) {
    alert("Enter at least two usernames");
    return;
  }

  const query = usernames
    .map((u) => `usernames=${encodeURIComponent(u)}`)
    .join("&");

  try {
    const res = await fetch(`/compare/?${query}`);
    const data = await res.json();
    displayResults(data);
  } catch (err) {
    console.error(err);
    document.getElementById(
      "results"
    ).innerHTML = `<p>Error connecting to server.</p>`;
  }
});

// --- Render Results ---
function displayResults(data) {
  const container = document.getElementById("results");
  container.innerHTML = "";

  // Invalid usernames
  if (data.invalid_usernames.length > 0) {
    container.innerHTML += `<p style="color:#ff4444">Invalid usernames: ${data.invalid_usernames.join(
      ", "
    )}</p>`;
  }

  // No common films
  if (data.common_films.length === 0) {
    container.innerHTML += `<p>No films in common.</p>`;
    return;
  }

  let html = `
        <h2 style="text-align:center;">Movies in Common</h2>
        <div class="film-grid">
    `;

  data.common_films.forEach((film) => {
    html += `
            <div class="film-card">
                <a href="${film.link}" target="_blank">
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
  container.innerHTML = html;
}
