// Terms and sources. Moved unchanged from the earlier Glossary page; the fonts entry is new.
export const TERMS: [string, string][] = [
  ['Classification', 'Naming what one image shows. This project classifies small crops. It does not find objects in a larger scene (that is detection).'],
  ['Crop', 'A small square cut from a video frame around an object, or from a region with no object.'],
  ['Scene cluster', 'A group of videos whose frames look almost the same, usually because they were filmed from one spot. Clusters, not frames, are assigned to train, validation or test.'],
  ['Train, validation, test', 'Train data adjusts the model. Validation data picks settings such as the best epoch and the alert threshold. Test data is looked at once, at the end.'],
  ['Precision', 'Of the crops the model called "bird", the share that really were birds.'],
  ['Recall', 'Of the real birds, the share the model called "bird".'],
  ['F1', 'A single score that combines precision and recall. It is low if either is low.'],
  ['Confusion matrix', 'A table of true class against predicted class. The diagonal is correct answers.'],
  ['Bootstrap interval', 'A range made by re-drawing the test videos many times with replacement and recomputing the score. A wide range means the score is uncertain.'],
  ['Quantisation', 'Storing a model\'s numbers in fewer bits, here 8-bit integers instead of 32-bit floating point, to make it smaller. It can change accuracy.'],
  ['ONNX', 'An open file format for neural-network models, used here to move the model out of PyTorch and into the browser.'],
  ['Tensor arena', 'The block of working memory a small-device runtime uses for the intermediate values of a model while it runs.'],
  ['Watchdog', 'A timer that expects a regular "I am alive" signal. If the signal stops, it forces a restart.'],
  ['State machine', 'Logic written as a fixed set of states and the allowed moves between them.'],
  ['Hard negative', 'An example of "not the target" that looks a lot like the target, such as an airplane when you are looking for birds.'],
];

export const SOURCES: [string, string][] = [
  ['Dataset', 'Svanstrom F., Alonso-Fernandez F., Englund C. A dataset for multi-sensor drone detection. Data in Brief 39 (2021) 107521. Data: Zenodo DOI 10.5281/zenodo.5500576. Licence confirmation from the authors pending.'],
  ['Model architecture', 'Howard et al., Searching for MobileNetV3 (2019). Implementation: torchvision (BSD-3-Clause code). Starting weights: torchvision ImageNet weights, downloaded at training time, not redistributed, licence terms not verified.'],
  ['General detector (demo)', 'YOLOX-Nano, Megvii-BaseDetection/YOLOX release 0.1.1rc0, repository licence Apache-2.0, 3,659,407 bytes. Third-party pre-trained model, not trained by this project.'],
  ['Runtime', 'ONNX Runtime Web (MIT), running WebAssembly in your browser.'],
  ['Fonts', 'IBM Plex Sans and IBM Plex Mono, self-hosted from the @fontsource packages, SIL Open Font Licence 1.1 (licence texts in the site under licenses/).'],
  ['Full list', 'docs/sources.md in the repository.'],
];

