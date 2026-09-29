/**
 * StyleMirror Main Application Controller
 * Wires stepper navigation, consent validation, photo upload,
 * style selection, background generation polling, and result viewer.
 */

import { api } from "./api.js";
import { getState, setState, resetState, subscribe } from "./state.js";
import { UploaderController } from "./uploader.js";
import { StyleGridController } from "./styleGrid.js";
import { ComparisonSlider } from "./slider.js";
import { waitForJob } from "./progress.js";

// Toast Notification Utility
export function showToast(message, type = "normal", duration = 4000) {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add("show"));
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// Map backend error codes to user-friendly actionable guidance
const ERROR_MESSAGES = {
  NO_FACE: "No face detected. Please face the camera directly in good lighting.",
  MULTIPLE_FACES: "Multiple faces detected. Please upload a portrait with only one person.",
  FACE_TOO_SMALL: "Face appears too small or distant. Please move closer to the camera.",
  TOO_BLURRY: "Image is too blurry. Hold the camera steady in a well-lit space.",
  TOO_DARK: "Image is too dark. Please take or upload a photo with front lighting.",
  FACE_NOT_FRONTAL: "Please look straight at the camera (tilt or side angles cannot be accurately styled).",
  FILE_TOO_LARGE: "File size exceeds the 8MB limit. Please choose a smaller image.",
  UNSUPPORTED_TYPE: "Unsupported file format. Please upload a standard JPG, PNG, or WEBP photo.",
  RATE_LIMITED: "Hourly limit reached. Please wait a few minutes before trying again.",
  AI_QUOTA_EXCEEDED: "AI service quota is momentarily busy. Please try again shortly.",
};

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const stepViews = {
    1: document.getElementById("step-1-view"),
    2: document.getElementById("step-2-view"),
    3: document.getElementById("step-3-view"),
  };

  const stepperItems = {
    1: document.getElementById("stepper-1"),
    2: document.getElementById("stepper-2"),
    3: document.getElementById("stepper-3"),
  };

  const consentOwn = document.getElementById("consent-own");
  const consentAgree = document.getElementById("consent-agree");

  const dropzoneEl = document.getElementById("dropzone");
  const fileInputEl = document.getElementById("file-input");
  const webcamContainerEl = document.getElementById("webcam-container");
  const videoEl = document.getElementById("webcam-video");
  const btnStartWebcam = document.getElementById("btn-start-webcam");
  const btnCapturePhoto = document.getElementById("btn-capture-photo");
  const btnCancelWebcam = document.getElementById("btn-cancel-webcam");

  const uploadPreviewWrap = document.getElementById("upload-preview-wrap");
  const previewImg = document.getElementById("preview-img");
  const btnRetake = document.getElementById("btn-retake");
  const btnProceedToStyles = document.getElementById("btn-proceed-styles");

  // Sticky Action Bar
  const stickyBar = document.getElementById("sticky-action-bar");
  const chosenHairSpan = document.getElementById("chosen-hair-name");
  const chosenBeardSpan = document.getElementById("chosen-beard-name");
  const btnGenerate = document.getElementById("btn-generate");

  // Progress Overlay
  const progressOverlay = document.getElementById("progress-overlay");
  const progressStageText = document.getElementById("progress-stage-text");

  // Result Section
  const sliderRange = document.getElementById("slider-range");
  const sliderAfterImg = document.getElementById("slider-img-after");
  const sliderHandleLine = document.getElementById("slider-handle-line");
  const sliderHandleBtn = document.getElementById("slider-handle-btn");
  const sliderContainer = document.getElementById("comparison-slider");
  const btnDownload = document.getElementById("btn-download");
  const btnTryAnother = document.getElementById("btn-try-another");
  const btnChangeHair = document.getElementById("btn-change-hair");
  const btnChangeBeard = document.getElementById("btn-change-beard");
  const btnDeletePhoto = document.getElementById("btn-delete-photo");
  const identityBadge = document.getElementById("identity-score-badge");

  // Initialize Comparison Slider
  let comparisonSlider = null;
  if (sliderContainer) {
    comparisonSlider = new ComparisonSlider({
      containerEl: sliderContainer,
      rangeInputEl: sliderRange,
      afterImgEl: sliderAfterImg,
      handleLineEl: sliderHandleLine,
      handleBtnEl: sliderHandleBtn,
    });
  }

  // Navigation Function
  function goToStep(stepNumber) {
    setState({ currentStep: stepNumber });
    Object.keys(stepViews).forEach((key) => {
      const num = parseInt(key, 10);
      if (stepViews[num]) {
        stepViews[num].classList.toggle("active", num === stepNumber);
      }
      if (stepperItems[num]) {
        stepperItems[num].classList.toggle("active", num === stepNumber);
        stepperItems[num].classList.toggle("completed", num < stepNumber);
      }
    });

    // Sticky bar only on step 2
    if (stickyBar) {
      stickyBar.classList.toggle("hidden", stepNumber !== 2);
    }

    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // Initialize Style Catalog Grid
  const styleGrid = new StyleGridController({
    containerEl: document.getElementById("style-grid"),
    tabHairBtn: document.getElementById("tab-hair"),
    tabBeardBtn: document.getElementById("tab-beard"),
    searchInputEl: document.getElementById("catalog-search"),
    onSelectionChange: (s) => updateStickyBar(s),
  });
  styleGrid.loadStyles();

  function updateStickyBar(s) {
    if (chosenHairSpan) chosenHairSpan.textContent = s.hairName || "None";
    if (chosenBeardSpan) chosenBeardSpan.textContent = s.beardName || "None";
    const hasSelection = !!(s.hairId || s.beardId);
    if (btnGenerate) btnGenerate.disabled = !hasSelection;
  }

  // Initialize Uploader Controller
  const uploader = new UploaderController({
    dropzoneEl,
    fileInputEl,
    webcamContainerEl,
    videoEl,
    onFileSelected: async (file) => {
      await processUploadedFile(file);
    },
  });

  // Check consent before photo processing
  function verifyConsent() {
    if (consentOwn && !consentOwn.checked) {
      showToast("Please confirm that this is your own photo.", "error");
      return false;
    }
    if (consentAgree && !consentAgree.checked) {
      showToast("Please agree to photo processing to continue.", "error");
      return false;
    }
    return true;
  }

  async function processUploadedFile(file) {
    if (!verifyConsent()) return;

    showToast("Analyzing face quality & alignment...", "normal", 2500);
    try {
      const res = await api.uploadPhoto(file);
      if (!res.ok) {
        const issue = res.issues && res.issues[0];
        const errorDesc = ERROR_MESSAGES[issue] || res.message || "Face validation failed.";
        showToast(errorDesc, "error", 5000);
        return;
      }

      // Successful upload
      const previewUrl = URL.createObjectURL(file);
      setState({
        photoId: res.photo_id,
        photoPreviewUrl: previewUrl,
      });

      if (previewImg) previewImg.src = previewUrl;
      if (dropzoneEl) dropzoneEl.style.display = "none";
      if (uploadPreviewWrap) uploadPreviewWrap.style.display = "flex";

      showToast("Face validated successfully! Choose your styles.", "success");
      setTimeout(() => goToStep(2), 500);
    } catch (err) {
      const code = err.code;
      const msg = ERROR_MESSAGES[code] || err.message || "Upload failed. Please try again.";
      showToast(msg, "error", 5000);
    }
  }

  // Webcam button handlers
  if (btnStartWebcam) {
    btnStartWebcam.addEventListener("click", async () => {
      if (!verifyConsent()) return;
      try {
        await uploader.startWebcam();
      } catch (err) {
        showToast(err.message, "error");
      }
    });
  }

  if (btnCapturePhoto) {
    btnCapturePhoto.addEventListener("click", async () => {
      const file = await uploader.captureWebcamSnapshot();
      if (file) {
        await processUploadedFile(file);
      }
    });
  }

  if (btnCancelWebcam) {
    btnCancelWebcam.addEventListener("click", () => {
      uploader.stopWebcam();
    });
  }

  if (btnRetake) {
    btnRetake.addEventListener("click", () => {
      if (dropzoneEl) dropzoneEl.style.display = "flex";
      if (uploadPreviewWrap) uploadPreviewWrap.style.display = "none";
      if (fileInputEl) fileInputEl.value = "";
    });
  }

  if (btnProceedToStyles) {
    btnProceedToStyles.addEventListener("click", () => {
      goToStep(2);
    });
  }

  // Generation Trigger
  if (btnGenerate) {
    btnGenerate.addEventListener("click", async () => {
      const s = getState();
      if (!s.photoId) {
        showToast("Please upload a photo first.", "error");
        goToStep(1);
        return;
      }
      if (!s.hairId && !s.beardId) {
        showToast("Please choose at least one hairstyle or beard style.", "error");
        return;
      }

      // Show progress overlay
      if (progressOverlay) progressOverlay.classList.add("active");
      if (progressStageText) progressStageText.textContent = "Analyzing face geometry...";

      try {
        const jobRes = await api.generate({
          photo_id: s.photoId,
          hair_style_id: s.hairId,
          beard_style_id: s.beardId,
          view: "front",
        });

        const completedJob = await waitForJob(jobRes.job_id, (statusInfo) => {
          if (progressStageText) progressStageText.textContent = statusInfo.message;
        });

        // Set result in state and update viewer
        setState({
          currentJobId: completedJob.id,
          resultUrl: completedJob.result_url,
          identityScore: completedJob.identity_score,
        });

        if (comparisonSlider && s.photoPreviewUrl && completedJob.result_url) {
          comparisonSlider.setImages(s.photoPreviewUrl, completedJob.result_url);
        }

        if (identityBadge && completedJob.identity_score) {
          identityBadge.textContent = `${Math.round(completedJob.identity_score * 100)}% Identity Preserved`;
        }

        if (progressOverlay) progressOverlay.classList.remove("active");
        showToast("Style transformation complete!", "success");
        goToStep(3);
      } catch (err) {
        if (progressOverlay) progressOverlay.classList.remove("active");
        const msg = ERROR_MESSAGES[err.code] || err.message || "Generation failed. Please try again.";
        showToast(msg, "error", 5000);
      }
    });
  }

  // Result actions
  if (btnDownload) {
    btnDownload.addEventListener("click", async () => {
      const s = getState();
      if (!s.resultUrl) return;
      try {
        const res = await fetch(s.resultUrl);
        const blob = await res.blob();
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `StyleMirror_${s.hairName || "Hair"}_${s.beardName || "Beard"}.jpg`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        showToast("Download started!", "success");
      } catch {
        window.open(s.resultUrl, "_blank");
      }
    });
  }

  if (btnTryAnother) {
    btnTryAnother.addEventListener("click", () => {
      goToStep(2);
    });
  }

  if (btnChangeHair) {
    btnChangeHair.addEventListener("click", () => {
      styleGrid.switchTab("hair");
      goToStep(2);
    });
  }

  if (btnChangeBeard) {
    btnChangeBeard.addEventListener("click", () => {
      styleGrid.switchTab("beard");
      goToStep(2);
    });
  }

  if (btnDeletePhoto) {
    btnDeletePhoto.addEventListener("click", async () => {
      const s = getState();
      if (!s.photoId) {
        resetState();
        goToStep(1);
        return;
      }
      if (confirm("Are you sure you want to delete your photo and all generated styles immediately?")) {
        try {
          await api.deletePhoto(s.photoId);
          showToast("Photo and all previews permanently deleted.", "success");
        } catch {
          // Continue cleanup on UI
        }
        resetState();
        if (dropzoneEl) dropzoneEl.style.display = "flex";
        if (uploadPreviewWrap) uploadPreviewWrap.style.display = "none";
        goToStep(1);
      }
    });
  }
});
