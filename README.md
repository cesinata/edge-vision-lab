# Solar-Guardian: Embedded Wildlife Detection System

* **Status:** Functional Prototype (Proof of Concept)
* **Target Hardware:** STM32 / ESP32 (Edge Impulse Compatible)
* **Language:** Python (TFLite), C++ (Firmware)

## 1. Project Overview
Solar-Guardian is an edge-optimized wildlife detection system designed for autonomous solar weather stations (like the **MetCube**). It addresses the critical need to distinguish biological targets (birds) from atmospheric noise ("Nothing") to trigger self-cleaning or deterrent mechanisms without draining battery power.

## 2. Technical Approach
Unlike standard cloud-based detection, this project focuses on **Edge AI** constraints:
* **Data Source:** Designed around the **StealthKnight "Bird vs Drone" dataset** [Kaggle].
    * *Why this dataset?* It provides pre-segmented 640x640 samples which perfectly align with the input tensor limits of efficient mobile architectures.
    * *Strategy:* We utilize the "Drone" class as "Hard Negatives" to train the model to ignore non-biological flying objects.
* **Model Architecture:** MobileNetV3 (Quantized).
* **Quantization:** Post-Training Quantization (PTQ) to Int8 to reduce model size by ~90% for microcontroller deployment.

## 3. Firmware Logic (C++)
The system operates on a Finite State Machine (FSM) to minimize power consumption:
* **IDLE:** Low-power sleep mode.
* **SENSE:** Wake-on-motion (simulated).
* **DETECT:** Run TFLite Micro inference.
* **DETER:** Trigger peripherals (Piezo/Visual) only upon high-confidence "Wildlife" detection.

## 4. File Structure
* `deployment/quantize_model.py`: Script to convert Keras models to TFLite Int8 format.
* `deployment/firmware_logic.cpp`: C++ implementation of the Watchdog Timer and State Machine logic.

## 5. Performance Results
Running the quantization pipeline (`deployment/quantize_model.py`) yielded significant storage savings, making the model feasible for flash-constrained devices like the STM32.

```text
------------------------------
Original Model Size: 29.34 KB
Quantized Model Size: 3.02 KB
COMPRESSION SUCCESS: Reduced by 89.72%
------------------------------
```

## 6. Key Engineering Challenges
* **The "Nothing" Class Ambiguity:**
    * *Challenge:* In a "Wildlife vs. Nothing" model, "Nothing" is not just empty sky. It includes clouds, sun glare, and mechanical distractors (drones).
    * *Solution:* Designed the dataset strategy to include "Hard Negatives" (drones from the StealthKnight dataset) to force the model to learn biological features (wing flapping) rather than just "dark object in sky."

* **Resolution vs. Latency Trade-off:**
    * *Challenge:* Standard 224x224 inputs destroy the detail of distant birds, but 4K inputs are too heavy for an STM32.
    * *Solution:* Standardized on 640x640 input resolution. This offers the best balance: high enough to detect small objects, but low enough to be processed by a quantized MobileNetV3.

* **Autonomous Reliability:**
    * *Challenge:* Edge devices in remote locations cannot be manually reset if they hang.
    * *Solution:* Implemented a simulated **Watchdog Timer** in the C++ firmware (`firmware_logic.cpp`) to ensure the system auto-recovers from any freeze states.