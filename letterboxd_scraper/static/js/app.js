document.addEventListener("DOMContentLoaded", () => {
  /* ---------- State ---------- */
  const selectedUsers = new Set();
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
        return { status: "invalid", username: value };
      }

      selectedUsers.add(value);
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
      showFeedback(`Letterboxd user does not exist: ${result.username}`);
    } else if (result.status === "error") {
      showFeedback("Unable to validate username. Try again.");
    } else {
      clearFeedback();
    }
  }

  function renderUsers() {
    userTags.innerHTML = "";

    selectedUsers.forEach((user) => {
      const tag = document.createElement("span");
      tag.className = "user-tag";
      tag.textContent = user;

      const remove = document.createElement("button");
      remove.textContent = "×";
      remove.onclick = () => {
        selectedUsers.delete(user);
        renderUsers();
      };

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

    const names = text
      .split(/[\s,]+/)
      .map(normalize)
      .filter(Boolean);

    if (names.length > MAX_PASTE_USERS) {
      showFeedback(
        `You pasted ${names.length} usernames. Please paste up to ${MAX_PASTE_USERS}.`
      );
      return;
    }

    if (!names.length) return;

    const duplicates = [];
    const invalid = [];
    const errors = [];

    for (const name of names) {
      const result = await validateAndAddUser(name);

      if (result.status === "duplicate") duplicates.push(name);
      else if (result.status === "invalid") invalid.push(name);
      else if (result.status === "error") errors.push(name);
    }

    const messages = [];

    if (duplicates.length) {
      messages.push(`Already added: ${duplicates.join(", ")}`);
    }
    if (invalid.length) {
      messages.push(`Invalid Letterboxd users: ${invalid.join(", ")}`);
    }
    if (errors.length) {
      messages.push(`Could not validate: ${errors.join(", ")}`);
    }

    if (messages.length) {
      showFeedback(messages.join(" | "));
    }

    input.value = "";
    input.focus();
    updateAddButtonState();
  });

  clearUsersBtn.addEventListener("click", clearAll);

  /* ---------- Compare ---------- */
  compareBtn.addEventListener("click", async () => {
    if (selectedUsers.size < 2) return;

    // UI state
    resultsDiv.classList.add("hidden");
    loadingDiv.classList.remove("hidden");

    const steps = [
      "Validating usernames…",
      "Syncing watchlists…",
      "Comparing movies…",
    ];

    let stepIndex = 0;
    loadingStep.textContent = steps[stepIndex];
    const stepInterval = setInterval(() => {
      stepIndex = Math.min(stepIndex + 1, steps.length - 1);
      loadingStep.textContent = steps[stepIndex];
    }, 600);

    try {
      const params = [...selectedUsers]
        .map((u) => `usernames=${encodeURIComponent(u)}`)
        .join("&");

      const response = await fetch(`/compare/?${params}`);
      const data = await response.json();

      commonFilms = data.common_films || [];
      renderResults();
    } catch (err) {
      alert("Something went wrong while comparing watchlists.");
      console.error(err);
    } finally {
      clearInterval(stepInterval);
      loadingDiv.classList.add("hidden");
    }
  });

  /* ---------- Results ---------- */
  function renderResults() {
    moviesGrid.innerHTML = "";
    genreFilter.innerHTML = `<option value="all">All</option>`;

    const users = [...selectedUsers];
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
    const genres = new Set();
    commonFilms.forEach((film) => film.genres.forEach((g) => genres.add(g)));

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

  function renderMovies(films) {
    moviesGrid.innerHTML = "";

    films.forEach((film) => {
      const card = document.createElement("div");
      card.className = "movie-card";

      const img = document.createElement("img");
      img.src = film.poster_image;
      img.alt = film.title;

      const title = document.createElement("p");
      title.textContent = film.title;

      const genresDiv = document.createElement("div");
      genresDiv.className = "genres";

      film.genres.forEach((g) => {
        const badge = document.createElement("span");
        badge.textContent = g;
        genresDiv.appendChild(badge);
      });

      const link = document.createElement("a");
      link.href = film.link;
      link.target = "_blank";
      link.textContent = "View on Letterboxd";

      card.appendChild(img);
      card.appendChild(title);
      card.appendChild(genresDiv);
      card.appendChild(link);

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
