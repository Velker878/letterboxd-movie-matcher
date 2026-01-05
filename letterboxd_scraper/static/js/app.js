document.addEventListener("DOMContentLoaded", () => {
  /* ---------- State ---------- */
  const selectedUsers = new Map();
  let commonFilms = [];

  /* ---------- Elements ---------- */
  const input = document.getElementById("username-input");
  const addBtn = document.getElementById("add-username-btn");
  addBtn.disabled = true;
  const selectedUsersDiv = document.getElementById("selected-users");
  const userTags = document.getElementById("user-tags");
  const clearUsersBtn = document.getElementById("clear-users-btn");
  const compareBtn = document.getElementById("compare-btn");
  const feedback = document.getElementById("username-feedback");

  const loadingDiv = document.getElementById("loading");
  const loadingStep = document.getElementById("loading-step");

  const resultsDiv = document.getElementById("results");
  const resultsTitle = document.getElementById("results-title");
  const resultsCount = document.getElementById("results-count");
  const moviesGrid = document.getElementById("movies-grid");

  const filtersDiv = document.getElementById("filters");
  const genreFilter = document.getElementById("genre-filter");

  /* ---------- Helpers ---------- */
  const MAX_PASTE_USERS = 10;

  const normalize = (v) => v.trim().toLowerCase();

  function showFeedback(message) {
    feedback.textContent = message;
    feedback.classList.remove("hidden");
  }

  function clearFeedback() {
    feedback.textContent = "";
    feedback.classList.add("hidden");
  }

  async function validateAndAddUser(name, options = {}) {
    const value = normalize(name);
    if (!value) return { status: "empty" };

    if (selectedUsers.has(value)) {
      return { status: "duplicate", username: value };
    }

    addBtn.disabled = true;

    try {
      const response = await fetch(
        `/validate-user/?username=${encodeURIComponent(value)}`
      );
      const data = await response.json();

      if (!data.valid) {
        return { status: "invalid", username: value, reason: data.reason };
      }

      selectedUsers.set(value, {
        pfp: data.pfp || null,
      });
      renderUsers();
      return { status: "added", username: value };
    } catch (err) {
      console.error(err);
      return { status: "error", username: value };
    } finally {
      updateAddButtonState();
    }
  }

  async function handleSingleAdd() {
    const result = await validateAndAddUser(input.value);

    input.value = "";
    input.focus();
    updateAddButtonState();

    if (result.status === "duplicate") {
      showFeedback(`Username already added: ${result.username}`);
    } else if (result.status === "invalid") {
      showFeedback(`${result.username}: ${result.reason}`);
    } else if (result.status === "error") {
      showFeedback("Unable to validate username. Try again.");
    } else {
      clearFeedback();
    }
  }

  function renderUsers() {
    userTags.innerHTML = "";

    selectedUsers.forEach((data, username) => {
      const tag = document.createElement("span");
      tag.className = "user-tag";

      // Avatar
      const img = document.createElement("img");
      img.className = "user-pfp";
      img.src = data.pfp || "/static/images/default-pfp.png";
      img.alt = username;

      // Username
      const name = document.createElement("span");
      name.textContent = username;

      // Remove button
      const remove = document.createElement("button");
      remove.textContent = "×";
      remove.onclick = () => {
        selectedUsers.delete(username);
        renderUsers();
      };

      tag.appendChild(img);
      tag.appendChild(name);
      tag.appendChild(remove);
      userTags.appendChild(tag);
    });

    const hasUsers = selectedUsers.size > 0;
    selectedUsersDiv.classList.toggle("hidden", !hasUsers);
    compareBtn.disabled = selectedUsers.size < 2;
  }

  function clearAll() {
    selectedUsers.clear();
    renderUsers();
    clearFeedback();
  }

  function updateAddButtonState() {
    addBtn.disabled = input.value.trim().length === 0;
  }

  const progressFill = document.getElementById("progress-fill");

  function setProgress(percent, text) {
    progressFill.style.width = `${percent}%`;
    loadingStep.textContent = text;
  }

  function smoothProgressTo(target, duration = 600) {
    return new Promise((resolve) => {
      const start = parseFloat(progressFill.style.width) || 0;
      const delta = target - start;
      const startTime = performance.now();

      function animate(now) {
        const elapsed = now - startTime;
        const linearProgress = Math.min(elapsed / duration, 1);
        const progress = 1 - Math.pow(1 - linearProgress, 3);
        const value = start + delta * progress;

        progressFill.style.width = `${value}%`;

        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          resolve();
        }
      }
      requestAnimationFrame(animate);
    });
  }

  function formatUserSentence(users) {
    if (users.length === 2) return `${users[0]} and ${users[1]}`;
    return `${users.slice(0, -1).join(", ")}, and ${users.at(-1)}`;
  }

  /* ---------- Input Events ---------- */
  addBtn.addEventListener("click", handleSingleAdd);

  input.addEventListener("input", () => {
    updateAddButtonState();
    clearFeedback();
  });

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSingleAdd();
    }
  });

  input.addEventListener("paste", async (e) => {
    e.preventDefault();
    clearFeedback();

    const text = e.clipboardData.getData("text");

    const names = [
      ...new Set(
        text
          .split(/[\s,]+/)
          .map(normalize)
          .filter(Boolean)
      ),
    ];

    if (names.length > MAX_PASTE_USERS) {
      showFeedback(`Too many usernames pasted. Max is ${MAX_PASTE_USERS}.`);
      return;
    }

    const issues = [];

    for (const name of names) {
      const result = await validateAndAddUser(name);
      if (result.status === "duplicate") issues.push(`${name}: Already added`);
      else if (result.status === "invalid")
        issues.push(`${name}: ${result.reason}`);
      else if (result.status === "error") issues.push(`${name}: Server error`);
    }

    if (issues.length) {
      showFeedback(`ERRORS: ${issues.join(" | ")}`);
    }

    input.value = "";
    updateAddButtonState();
  });

  clearUsersBtn.addEventListener("click", clearAll);

  /* ---------- Compare ---------- */
  compareBtn.addEventListener("click", async () => {
    console.log("DEBUG: Compare button clicked");

    if (selectedUsers.size < 2) return;

    resultsDiv.classList.add("hidden");
    loadingDiv.classList.remove("hidden");
    setProgress(0, "Preparing...");

    try {
      const params = [...selectedUsers.keys()]
        .map((u) => `usernames=${encodeURIComponent(u)}`)
        .join("&");

      console.log("DEBUG: Sending fetch request...");
      const fetchPromise = fetch(`/compare/?${params}`);

      loadingStep.textContent = "Validating usernames...";
      await smoothProgressTo(10, 400);

      loadingStep.textContent = "Syncing watchlists...";
      await smoothProgressTo(25, 2000);

      loadingStep.textContent = "Comparing watchlists...";
      await smoothProgressTo(50, 3500);

      const response = await fetchPromise;

      if (!response.ok) {
        const errorText = await response.text(); // Get text in case JSON fails
        console.error("DEBUG: Error details:", errorText);
        loadingDiv.classList.add("hidden");
        showFeedback("Server Error. Check Console.");
        return;
      }

      const data = await response.json();

      loadingStep.textContent = "Processing results...";
      await smoothProgressTo(100, 200);

      commonFilms = data.common_films || [];
      renderResults();

      setTimeout(() => {
        loadingDiv.classList.add("hidden");
      }, 400);
    } catch (err) {
      console.error(err);
      showFeedback("Error during comparison.");
      loadingDiv.classList.add("hidden");
    }
  });

  /* ---------- Results ---------- */
  function renderResults() {
    moviesGrid.innerHTML = "";
    genreFilter.innerHTML = `<option value="all">All</option>`;

    const users = [...selectedUsers.keys()];
    resultsTitle.textContent = `Movies in common between ${formatUserSentence(
      users
    )}`;

    if (commonFilms.length === 0) {
      resultsCount.textContent = "No movies in common";
      filtersDiv.classList.add("hidden");
      resultsDiv.classList.remove("hidden");
      return;
    }

    resultsCount.textContent = `${commonFilms.length} movies in common`;

    // Build genre filter
    const genresSet = new Set();
    commonFilms.forEach((film) => film.genres.forEach((g) => genresSet.add(g)));

    const genres = [...genresSet].sort((a, b) => a.localeCompare(b));

    genres.forEach((g) => {
      const option = document.createElement("option");
      option.value = g;
      option.textContent = g;
      genreFilter.appendChild(option);
    });

    filtersDiv.classList.remove("hidden");

    renderMovies(commonFilms);
    resultsDiv.classList.remove("hidden");
  }

  function renderMovies(movies) {
    moviesGrid.innerHTML = "";

    if (movies.length === 0) {
      moviesGrid.innerHTML = "<p>No common films found.</p>";
      return;
    }

    movies.forEach((film) => {
      const card = document.createElement("div");
      card.className = "movie-card";

      const posterWrapper = document.createElement("div");
      posterWrapper.className = "movie-poster";

      const img = document.createElement("img");
      img.src = film.poster_url;
      img.alt = film.title;
      img.loading = "lazy";

      posterWrapper.appendChild(img);

      const title = document.createElement("div");
      title.className = "movie-title";
      title.textContent = film.year
        ? `${film.title} (${film.year})`
        : film.title;

      card.appendChild(posterWrapper);
      card.appendChild(title);

      moviesGrid.appendChild(card);
    });
  }

  genreFilter.addEventListener("change", () => {
    const value = genreFilter.value;
    if (value === "all") {
      renderMovies(commonFilms);
    } else {
      renderMovies(commonFilms.filter((film) => film.genres.includes(value)));
    }
  });
});
