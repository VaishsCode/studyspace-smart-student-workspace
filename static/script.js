// --- Dark Mode Toggle ---
const toggleBtn = document.getElementById("dark-mode-toggle");
const savedTheme = localStorage.getItem("theme") || "light";
document.documentElement.setAttribute("data-theme", savedTheme);

if (toggleBtn) {
  toggleBtn.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const targetTheme = currentTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", targetTheme);
    localStorage.setItem("theme", targetTheme);
  });
}

// --- Resource Management & Category Filtering ---
const addResourceButton = document.getElementById("add-resource-btn");
const resourceForm = document.getElementById("resource-form");
const resourceList = document.getElementById("resource-list");
const emptyStateContainer = document.getElementById("empty-state-container");

const resourceTitle = document.getElementById("resource-title");
const resourceUrl = document.getElementById("resource-url");
const resourceCategory = document.getElementById("resource-category");

if (addResourceButton && resourceForm) {
  addResourceButton.addEventListener("click", function () {
    resourceForm.hidden = !resourceForm.hidden;
  });
}

function displayResource(resource) {
  const card = document.createElement("article");
  card.className = "resource-card";
  card.setAttribute("data-category", resource.category);

  const heading = document.createElement("h3");
  heading.textContent = resource.title;

  const categoryText = document.createElement("p");
  categoryText.textContent = "Category: " + resource.category;

  const link = document.createElement("a");
  link.textContent = "Open resource →";
  link.href = resource.url;
  link.target = "_blank";
  link.rel = "noopener noreferrer";

  card.append(heading, categoryText, link);
  resourceList.append(card);
}

async function loadResources() {
  try {
    const response = await fetch("/api/resources");
    if (!response.ok) return;
    const resources = await response.json();

    if (resources.length > 0 && emptyStateContainer) {
      emptyStateContainer.style.display = "none";
    } else if (emptyStateContainer) {
      emptyStateContainer.style.display = "block";
    }

    resourceList.replaceChildren();
    resources.forEach(function (resource) {
      displayResource(resource);
    });
  } catch (error) {
    console.error("Could not load resources", error);
  }
}

if (resourceForm) {
  resourceForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const resource = {
      title: resourceTitle.value.trim(),
      url: resourceUrl.value.trim(),
      category: resourceCategory.value,
    };

    try {
      const response = await fetch("/api/resources", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(resource),
      });

      if (!response.ok) {
        alert("Could not save the resource.");
        return;
      }

      const savedResource = await response.json();
      if (emptyStateContainer) {
        emptyStateContainer.style.display = "none";
      }

      displayResource(savedResource);
      resourceForm.reset();
      resourceForm.hidden = true;
    } catch (error) {
      alert("Could not connect to the server.");
      console.error(error);
    }
  });
}

// Category Card Clicking Filter
const categoryCards = document.querySelectorAll(".category-card");
categoryCards.forEach(card => {
  card.addEventListener("click", () => {
    const targetCategory = card.getAttribute("data-category");
    const resourceCards = resourceList.getElementsByClassName("resource-card");

    Array.from(resourceCards).forEach(rCard => {
      const cardCategory = rCard.getAttribute("data-category");
      if (cardCategory === targetCategory) {
        rCard.style.display = "";
      } else {
        rCard.style.display = "none";
      }
    });

    document.getElementById("resources").scrollIntoView({ behavior: "smooth" });
  });
});

// --- Show All Resources Filter Reset ---
const showAllBtn = document.getElementById("show-all-btn");
if (showAllBtn) {
  showAllBtn.addEventListener("click", () => {
    const resourceCards = resourceList.getElementsByClassName("resource-card");
    Array.from(resourceCards).forEach(rCard => {
      rCard.style.display = "";
    });
  });
}

// --- Search Display Logic (Directly below search bar) ---
const searchInput = document.getElementById("resource-search");
const searchResultsContainer = document.getElementById("search-results-container");
const searchResultsList = document.getElementById("search-results-list");
const clearSearchBtn = document.getElementById("clear-search-btn");

if (searchInput) {
  searchInput.addEventListener("input", function () {
    const query = searchInput.value.toLowerCase().trim();
    searchResultsList.replaceChildren();

    if (query === "") {
      searchResultsContainer.style.display = "none";
      return;
    }

    const allCards = resourceList.getElementsByClassName("resource-card");
    let matchCount = 0;

    Array.from(allCards).forEach(function (card) {
      if (card.textContent.toLowerCase().includes(query)) {
        const clone = card.cloneNode(true);
        searchResultsList.append(clone);
        matchCount++;
      }
    });

    if (matchCount > 0) {
      searchResultsContainer.style.display = "block";
    } else {
      searchResultsContainer.style.display = "block";
      searchResultsList.innerHTML = `<p style="color: var(--muted); font-size: 13px;">No resources matching "${query}".</p>`;
    }
  });
}

if (clearSearchBtn) {
  clearSearchBtn.addEventListener("click", () => {
    searchInput.value = "";
    searchResultsContainer.style.display = "none";
  });
}

loadResources();

// --- Quick Notes Logic with Emoji & Title ---
const noteForm = document.getElementById("note-form");
const noteEmojiInput = document.getElementById("note-emoji");
const noteTitleInput = document.getElementById("note-title");
const noteContentInput = document.getElementById("note-content");
const notesList = document.getElementById("notes-list");

function displayNote(note) {
  const noteCard = document.createElement("div");
  noteCard.style.cssText = "background: var(--surface); padding: 16px; border-radius: 12px; border: 1px solid var(--border); display: flex; justify-content: space-between; align-items: flex-start;";

  const bodyDiv = document.createElement("div");
  bodyDiv.style.cssText = "flex: 1;";

  const header = document.createElement("h4");
  header.style.cssText = "font-size: 14px; margin-bottom: 4px; display: flex; align-items: center; gap: 8px;";
  header.innerHTML = `<span>${note.emoji || '💡'}</span> <span>${note.title || 'Quick Note'}</span>`;

  const text = document.createElement("p");
  text.textContent = note.content;
  text.style.cssText = "font-size: 13px; color: var(--muted); white-space: pre-wrap; word-break: break-word;";

  bodyDiv.append(header, text);

  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = "🗑️";
  deleteBtn.style.cssText = "background: transparent; border: none; cursor: pointer; font-size: 14px; margin-left: 10px;";
  deleteBtn.addEventListener("click", async () => {
    const res = await fetch(`/api/notes/${note.id}`, { method: "DELETE" });
    if (res.ok) {
      noteCard.remove();
    }
  });

  noteCard.append(bodyDiv, deleteBtn);
  notesList.prepend(noteCard);
}

async function loadNotes() {
  try {
    const response = await fetch("/api/notes");
    if (!response.ok) return;
    const notes = await response.json();

    notesList.replaceChildren();
    notes.forEach(note => {
      displayNote(note);
    });
  } catch (error) {
    console.error("Could not load notes", error);
  }
}

if (noteForm) {
  noteForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const emoji = noteEmojiInput.value;
    const title = noteTitleInput.value.trim();
    const content = noteContentInput.value.trim();

    if (!content) return;

    try {
      const response = await fetch("/api/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ emoji, title, content })
      });

      if (response.ok) {
        const newNote = await response.json();
        displayNote(newNote);
        noteTitleInput.value = "";
        noteContentInput.value = "";
      }
    } catch (error) {
      console.error("Could not save note", error);
    }
  });
}

loadNotes();