# Site copy

Public-safe. Commit as `docs/site-copy.md`. This is the wording for the website, in page order. Use it as written. If a number here does not match `bench/results.json`, the results file wins: fix this file and flag it.

Voice: plain words, short sentences, explain every term the first time it appears, Australian spelling, no hype. Write for someone with no AI background.

---

## Header

- Site name: edge-vision-lab
- Nav: Learn · Try it · Results · GitHub

## Hero

**Headline:** Teach a tiny camera to tell a bird from a drone

**Intro**

A step-by-step guide to putting a machine learning model onto a microcontroller: the small, low-power chip inside things like smart sensors, wearables and remote cameras. The guide focuses on STM32 microcontrollers, a popular family used in many embedded projects, and follows one real example from start to finish.

**Buttons:** Try the live demo · Read the lessons

## About this project

**What's the example?**
A camera looks at the sky and has to decide whether it's seeing a bird, a drone, or neither. People care about this near airports, where a stray drone is a safety risk, and in wildlife monitoring, where you want to count birds without false alarms.

**Why is it hard?**
A laptop could do this easily. A microcontroller has a tiny fraction of the memory and runs on very little power, often from a battery. So the model has to be small and fast, and the camera has to know when to stay asleep. Running machine learning directly on a device like this is called edge AI, or TinyML.

**What will I find here?**
Six short lessons that follow the project in order: gathering the data, splitting it fairly, training the model, testing it, shrinking it to fit a microcontroller, and writing the logic that decides when the camera wakes up. Each lesson has a drawing and something you can try in your browser.

**What's real, and what isn't yet?**
Every number on this site comes from code you can run yourself, and each one says how it was measured. The model looks at a cropped image and names what's in it. It doesn't find objects in a full frame yet. It has been tested on a laptop and is sized for STM32-class chips, but it hasn't been measured on a real board. Where results are weak, they're shown anyway.

## The pipeline

**Heading:** Six steps from video to chip

**Lead:** Here is the whole project on one line. Each step feeds the next, and each one has its own lesson below.

| Step | Title | One line |
| --- | --- | --- |
| 01 | Data | Short videos of birds, drones and sky, with a box drawn around each bird and drone. |
| 02 | Split | Whole scenes go to training or testing, never both, so the test is fair. |
| 03 | Train | A small network learns to sort cropped images into bird, drone or neither. |
| 04 | Evaluate | Check how often it is right for each class, not just overall. |
| 05 | Quantise | Shrink the model so it fits on a microcontroller, and measure what that costs. |
| 06 | Firmware | Write and test the logic that wakes the camera, runs the model and goes back to sleep. |

## Why the split is by scene

Frames from the same video look almost identical. If some of them go into training and the rest into testing, the model is sitting an exam it has already seen the answers to. The score looks great and means very little.

So this project keeps every scene together. The videos were grouped into scenes that share a location, and each scene goes entirely to training, validation or testing. It makes the score lower, and more honest.

Caption under the drawing: Each box is one scene. A random frame split (right) leaks the same scene into both sides.

## Anatomy of a vision board

**Heading:** What sits on the board

**Lead:** Before squeezing a model onto a chip, it helps to know what is on a typical microcontroller board with a camera. This is a simplified drawing, not a specific product.

| # | Part | What it does |
| --- | --- | --- |
| 1 | Camera connector | Where the image comes in from the camera module. |
| 2 | Microcontroller | The main chip. It runs the program and, if nothing else is available, the model too. |
| 3 | Neural accelerator | Extra hardware on some chips that runs model layers much faster than the main processor. |
| 4 | RAM | Short-term memory. It holds the current image and the model's working space while it runs. |
| 5 | Flash | Long-term storage for the program and the model's weights. |
| 6 | USB debug port | How you load new code onto the board and read its log messages. |
| 7 | Pin headers | Rows of pins for power and for connecting sensors or other add-ons. |

Caption: Simplified original drawing. Not a specific product. Not measured on hardware.

## Live demo

**Heading:** Try it with your own camera

You can point your webcam at the screen, the window or a photo, and see what a model makes of it. Everything runs inside your browser. No frames leave your device.

There are two models to compare:

- **This project's model** is small and was trained only on outdoor sky footage. It names the whole image: bird, drone or neither. It is not published yet while the dataset licence is confirmed.
- **General detector** is a model made by someone else and trained on everyday photos. It draws a box around each object it finds, including birds.

Fair warning: this project's model learned from outdoor footage, so your lounge room will probably confuse it. That's a useful lesson in itself. A model only knows the world it was shown.

Readouts: latency (ms, measured in your browser) · model size (KB) · input size (224 × 224)

## Lessons

**Heading:** Six short lessons

| # | Title | Blurb |
| --- | --- | --- |
| 01 | What edge AI is | Why running a model on a small chip is different from running it in the cloud, and what memory, power and speed have to do with it. |
| 02 | From data to chip | The whole pipeline in one picture, so the later lessons have somewhere to fit. |
| 03 | Fair splits | Why a random split of video frames gives a score you can't trust, and how grouping by scene fixes it. |
| 04 | Is it any good? | Precision, recall and the confusion matrix in plain words, with a slider to see what a stricter threshold changes. |
| 05 | Shrinking the model | What quantisation does to a model's size and accuracy, using this project's real numbers. |
| 06 | Putting it on a chip | How much memory everything needs, and the simple set of states that keeps the camera asleep most of the time. |

## Results

**Heading:** What the test showed, including the weak parts

**Lead:** These numbers come from the test scenes, which the model never saw during training.

1. **Drones are the weak spot.** The model caught about half of the drones in the test scenes (drone recall 0.465, measured on a laptop CPU). Recall means: of all the real drones, how many did it find.
2. **Only partly shrunk.** Converting every layer to 8-bit integers failed, so some layers still use full-size numbers. The site shows both model sizes.
3. **Not many drone locations.** Most drone videos were filmed in a few places, so the model has seen little variety, and the uncertainty ranges are wide.

**Next steps:** gather drone footage from more places, test on a separate set of everyday images, and measure the model on a real STM32 board.

## Footer

Code MIT. Dataset: Svanström et al., licence confirmation requested. STM32 is a trademark of STMicroelectronics. This project is not affiliated with any vendor.
