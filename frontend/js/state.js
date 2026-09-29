/**
 * StyleMirror Reactive Application State
 * Reference: stylemirror-docs/07_FRONTEND.md
 */

const state = {
  currentStep: 1, // 1: Upload, 2: Style, 3: Result
  photoId: null,
  photoPreviewUrl: null,
  hairId: null,
  hairName: null,
  beardId: null,
  beardName: null,
  currentJobId: null,
  resultUrl: null,
  identityScore: null,
};

const listeners = new Set();

export function getState() {
  return state;
}

export function setState(updates) {
  Object.assign(state, updates);
  listeners.forEach((fn) => fn(state));
}

export function subscribe(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export function resetState() {
  setState({
    currentStep: 1,
    photoId: null,
    photoPreviewUrl: null,
    hairId: null,
    hairName: null,
    beardId: null,
    beardName: null,
    currentJobId: null,
    resultUrl: null,
    identityScore: null,
  });
}
