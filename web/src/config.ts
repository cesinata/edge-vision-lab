// The project's own classifier is not published until the dataset authors confirm
// the data licence in writing. Flip this only after that, via scripts/publish_model.sh.
export const MODEL_PUBLISHED = false;
export const MODEL_UNPUBLISHED_REASON =
  'The model was trained on a dataset whose licence has not yet been confirmed in writing by its authors, so the weights are not released.';
export const PROJECT_MODEL_URL = 'models/guardian_int8.onnx';
export const DETECTOR_URL = 'models/yolox_nano.onnx';
