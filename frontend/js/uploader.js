/**
 * StyleMirror Photo Uploader & Camera Controller
 * Supports file picker, drag-and-drop, and live webcam stream
 * Compresses client-side to <= 1600px via HTML5 Canvas
 */

export async function compressImage(file, maxDimension = 1600) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = reject;
    reader.onload = (e) => {
      const img = new Image();
      img.onerror = reject;
      img.onload = () => {
        let { width, height } = img;
        if (width > maxDimension || height > maxDimension) {
          if (width > height) {
            height = Math.round((height * maxDimension) / width);
            width = maxDimension;
          } else {
            width = Math.round((width * maxDimension) / height);
            height = maxDimension;
          }
        }
        const canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, width, height);
        canvas.toBlob(
          (blob) => {
            if (blob) {
              const compressedFile = new File([blob], file.name.replace(/\.[^/.]+$/, ".jpg"), {
                type: "image/jpeg",
              });
              resolve(compressedFile);
            } else {
              resolve(file);
            }
          },
          "image/jpeg",
          0.92
        );
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
}

export class UploaderController {
  constructor({ dropzoneEl, fileInputEl, webcamContainerEl, videoEl, onFileSelected }) {
    this.dropzoneEl = dropzoneEl;
    this.fileInputEl = fileInputEl;
    this.webcamContainerEl = webcamContainerEl;
    this.videoEl = videoEl;
    this.onFileSelected = onFileSelected;
    this.webcamStream = null;

    this.initEvents();
  }

  initEvents() {
    if (this.dropzoneEl && this.fileInputEl) {
      this.dropzoneEl.addEventListener("click", () => this.fileInputEl.click());

      this.fileInputEl.addEventListener("change", (e) => {
        if (e.target.files && e.target.files[0]) {
          this.handleFile(e.target.files[0]);
        }
      });

      // Drag and drop
      ["dragenter", "dragover"].forEach((evt) => {
        this.dropzoneEl.addEventListener(evt, (e) => {
          e.preventDefault();
          e.stopPropagation();
          this.dropzoneEl.classList.add("dragover");
        });
      });

      ["dragleave", "drop"].forEach((evt) => {
        this.dropzoneEl.addEventListener(evt, (e) => {
          e.preventDefault();
          e.stopPropagation();
          this.dropzoneEl.classList.remove("dragover");
        });
      });

      this.dropzoneEl.addEventListener("drop", (e) => {
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
          this.handleFile(e.dataTransfer.files[0]);
        }
      });
    }
  }

  async handleFile(file) {
    if (!file.type.startsWith("image/")) {
      throw new Error("Please select an image file (JPG, PNG, or WEBP).");
    }
    const compressed = await compressImage(file, 1600);
    this.onFileSelected(compressed);
  }

  async startWebcam() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error("Webcam access is not supported in this browser.");
    }
    this.stopWebcam();
    try {
      this.webcamStream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 960 }, facingMode: "user" },
        audio: false,
      });
      if (this.videoEl) {
        this.videoEl.srcObject = this.webcamStream;
        await this.videoEl.play();
      }
      if (this.webcamContainerEl) {
        this.webcamContainerEl.style.display = "flex";
      }
      if (this.dropzoneEl) {
        this.dropzoneEl.style.display = "none";
      }
    } catch (err) {
      throw new Error("Could not access camera. Please allow camera permissions or upload a file.");
    }
  }

  stopWebcam() {
    if (this.webcamStream) {
      this.webcamStream.getTracks().forEach((track) => track.stop());
      this.webcamStream = null;
    }
    if (this.webcamContainerEl) {
      this.webcamContainerEl.style.display = "none";
    }
    if (this.dropzoneEl) {
      this.dropzoneEl.style.display = "flex";
    }
  }

  captureWebcamSnapshot() {
    if (!this.videoEl || !this.webcamStream) return null;
    const canvas = document.createElement("canvas");
    canvas.width = this.videoEl.videoWidth || 960;
    canvas.height = this.videoEl.videoHeight || 720;
    const ctx = canvas.getContext("2d");
    // Mirror horizontally for selfie
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(this.videoEl, 0, 0, canvas.width, canvas.height);
    this.stopWebcam();

    return new Promise((resolve) => {
      canvas.toBlob(
        (blob) => {
          const file = new File([blob], "selfie_capture.jpg", { type: "image/jpeg" });
          resolve(file);
        },
        "image/jpeg",
        0.92
      );
    });
  }
}
