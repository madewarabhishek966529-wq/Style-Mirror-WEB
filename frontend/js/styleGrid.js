/**
 * StyleMirror Style Grid Component
 * Renders Hairstyles and Beards with tab switching, live filtering, and selection
 * Reference: stylemirror-docs/07_FRONTEND.md
 */

import { api } from "./api.js";
import { getState, setState } from "./state.js";

export class StyleGridController {
  constructor({ containerEl, tabHairBtn, tabBeardBtn, searchInputEl, onSelectionChange }) {
    this.containerEl = containerEl;
    this.tabHairBtn = tabHairBtn;
    this.tabBeardBtn = tabBeardBtn;
    this.searchInputEl = searchInputEl;
    this.onSelectionChange = onSelectionChange;

    this.currentTab = "hair"; // 'hair' | 'beard'
    this.allStyles = { hair: [], beard: [] };
    this.searchQuery = "";

    this.initEvents();
  }

  initEvents() {
    if (this.tabHairBtn) {
      this.tabHairBtn.addEventListener("click", () => this.switchTab("hair"));
    }
    if (this.tabBeardBtn) {
      this.tabBeardBtn.addEventListener("click", () => this.switchTab("beard"));
    }
    if (this.searchInputEl) {
      this.searchInputEl.addEventListener("input", (e) => {
        this.searchQuery = e.target.value.toLowerCase().trim();
        this.render();
      });
    }
  }

  async loadStyles() {
    try {
      const hairList = await api.styles("hair");
      const beardList = await api.styles("beard");
      this.allStyles.hair = hairList;
      this.allStyles.beard = beardList;
      this.render();
    } catch (err) {
      console.error("Failed to load style catalog:", err);
    }
  }

  switchTab(tab) {
    this.currentTab = tab;
    if (this.tabHairBtn) {
      this.tabHairBtn.classList.toggle("active", tab === "hair");
    }
    if (this.tabBeardBtn) {
      this.tabBeardBtn.classList.toggle("active", tab === "beard");
    }
    this.render();
  }

  render() {
    if (!this.containerEl) return;
    const styles = this.allStyles[this.currentTab] || [];
    const filtered = styles.filter((s) => {
      if (!this.searchQuery) return true;
      return (
        s.name.toLowerCase().includes(this.searchQuery) ||
        s.prompt_hint.toLowerCase().includes(this.searchQuery) ||
        s.id.toLowerCase().includes(this.searchQuery)
      );
    });

    const currentState = getState();
    const selectedId = this.currentTab === "hair" ? currentState.hairId : currentState.beardId;

    if (filtered.length === 0) {
      this.containerEl.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
          <p>No ${this.currentTab} styles found matching "${this.searchQuery}".</p>
        </div>
      `;
      return;
    }

    this.containerEl.innerHTML = filtered
      .map((item) => {
        const isSelected = item.id === selectedId;
        return `
        <div class="style-card ${isSelected ? "selected" : ""}" data-id="${item.id}" data-type="${item.type}">
          <div class="style-thumb-wrap">
            <img src="${item.thumb_url}" alt="${item.name}" loading="lazy" />
          </div>
          <div class="style-card-body">
            <span class="style-card-name">${item.name}</span>
            <span class="style-card-desc">${item.prompt_hint}</span>
          </div>
        </div>
      `;
      })
      .join("");

    // Attach click listeners to cards
    this.containerEl.querySelectorAll(".style-card").forEach((card) => {
      card.addEventListener("click", () => {
        const id = card.getAttribute("data-id");
        const type = card.getAttribute("data-type");
        this.handleCardClick(id, type);
      });
    });
  }

  handleCardClick(id, type) {
    const currentState = getState();
    const styleObj = (this.allStyles[type] || []).find((s) => s.id === id);
    if (!styleObj) return;

    if (type === "hair") {
      const isAlready = currentState.hairId === id;
      setState({
        hairId: isAlready ? null : id,
        hairName: isAlready ? null : styleObj.name,
      });
    } else {
      const isAlready = currentState.beardId === id;
      setState({
        beardId: isAlready ? null : id,
        beardName: isAlready ? null : styleObj.name,
      });
    }

    this.render();
    if (this.onSelectionChange) {
      this.onSelectionChange(getState());
    }
  }
}
