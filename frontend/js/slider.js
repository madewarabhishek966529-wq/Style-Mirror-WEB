/**
 * StyleMirror Before/After Interactive Comparison Slider
 * Reference: stylemirror-docs/07_FRONTEND.md
 */

export class ComparisonSlider {
  constructor({ containerEl, rangeInputEl, afterImgEl, handleLineEl, handleBtnEl }) {
    this.containerEl = containerEl;
    this.rangeInputEl = rangeInputEl;
    this.afterImgEl = afterImgEl;
    this.handleLineEl = handleLineEl;
    this.handleBtnEl = handleBtnEl;

    this.initEvents();
    this.setPosition(50);
  }

  initEvents() {
    if (!this.rangeInputEl) return;

    this.rangeInputEl.addEventListener("input", (e) => {
      this.setPosition(parseFloat(e.target.value));
    });

    // Touch / Mouse dragging directly on container
    let isDragging = false;

    const onPointerMove = (e) => {
      if (!isDragging || !this.containerEl) return;
      const rect = this.containerEl.getBoundingClientRect();
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const x = clientX - rect.left;
      const pct = Math.max(0, Math.min(100, (x / rect.width) * 100));
      this.setPosition(pct);
      if (this.rangeInputEl) this.rangeInputEl.value = pct;
    };

    const stopDragging = () => {
      isDragging = false;
      window.removeEventListener("mousemove", onPointerMove);
      window.removeEventListener("mouseup", stopDragging);
      window.removeEventListener("touchmove", onPointerMove);
      window.removeEventListener("touchend", stopDragging);
    };

    if (this.containerEl) {
      this.containerEl.addEventListener("mousedown", (e) => {
        isDragging = true;
        window.addEventListener("mousemove", onPointerMove);
        window.addEventListener("mouseup", stopDragging);
        onPointerMove(e);
      });

      this.containerEl.addEventListener("touchstart", (e) => {
        isDragging = true;
        window.addEventListener("touchmove", onPointerMove);
        window.addEventListener("touchend", stopDragging);
        onPointerMove(e);
      }, { passive: true });
    }
  }

  setPosition(percentage) {
    const p = Math.max(0, Math.min(100, percentage));
    const rightInset = 100 - p;
    if (this.afterImgEl) {
      this.afterImgEl.style.clipPath = `inset(0 ${rightInset}% 0 0)`;
      this.afterImgEl.style.webkitClipPath = `inset(0 ${rightInset}% 0 0)`;
    }
    if (this.handleLineEl) {
      this.handleLineEl.style.left = `${p}%`;
    }
    if (this.handleBtnEl) {
      this.handleBtnEl.style.left = `${p}%`;
    }
  }

  setImages(beforeUrl, afterUrl) {
    const beforeImg = this.containerEl.querySelector(".slider-img-before");
    if (beforeImg) beforeImg.src = beforeUrl;
    if (this.afterImgEl) this.afterImgEl.src = afterUrl;
    this.setPosition(50);
    if (this.rangeInputEl) this.rangeInputEl.value = 50;
  }
}
