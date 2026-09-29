/**
 * StyleMirror Progress Polling & Status Transition Manager
 * Reference: stylemirror-docs/07_FRONTEND.md
 */

import { api } from "./api.js";

const STAGE_MESSAGES = [
  "Analyzing facial geometry & skin tone...",
  "Applying precision hair & beard styling...",
  "Running identity consistency verification...",
  "Finalizing photorealistic render...",
];

export async function waitForJob(jobId, onProgress) {
  let stageIdx = 0;
  const stageTimer = setInterval(() => {
    stageIdx = (stageIdx + 1) % STAGE_MESSAGES.length;
    if (onProgress) {
      onProgress({ status: "running", message: STAGE_MESSAGES[stageIdx] });
    }
  }, 3000);

  try {
    while (true) {
      const job = await api.job(jobId);
      if (job.status === "done") {
        clearInterval(stageTimer);
        if (onProgress) {
          onProgress({ status: "done", message: "Render ready!", resultUrl: job.result_url, identityScore: job.identity_score });
        }
        return job;
      }
      if (job.status === "failed") {
        clearInterval(stageTimer);
        const errMsg = job.error || "Generation failed. Please try another photo or style.";
        throw new Error(errMsg);
      }
      // Status is queued or running
      if (onProgress) {
        onProgress({ status: job.status, message: STAGE_MESSAGES[stageIdx] });
      }
      await new Promise((r) => setTimeout(r, 1500));
    }
  } catch (err) {
    clearInterval(stageTimer);
    throw err;
  }
}
