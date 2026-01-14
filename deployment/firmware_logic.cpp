#include <iostream>
// hardware libraries
#include "EdgeImpulse_Inferencing.h" 
#include "STM32_Power_Mgmt.h"

// Define System States for the MetCube
enum SystemState {
    IDLE_LOW_POWER,
    SENSE_ENVIRONMENT,
    DETECT_WILDLIFE,
    TRIGGER_DETERRENT
};

struct MetCubeSystem {
    SystemState currentState;
    bool birdDetected;
    float batteryVoltage;
};

// SIMULATION: Watchdog Timer (Crucial for remote autonomous systems)
void feedWatchdog() {
    // Reset hardware timer to prevent system hang
    // printf("Watchdog fed.\n");
}

void setup() {
    // Initialize sensors and load the TFLite model
    initCamera(RESOLUTION_640x640); // Matches dataset resolution 
    initPowerManagement();
    printf("Solar-Guardian System Initialized.\n");
}

void loop() {
    static MetCubeSystem system = {IDLE_LOW_POWER, false, 12.5};
    
    feedWatchdog(); // Always keep the system alive

    switch (system.currentState) {
        case IDLE_LOW_POWER:
            // Deep sleep logic to save solar battery
            if (motionSensorTriggered()) {
                system.currentState = SENSE_ENVIRONMENT;
            }
            break;

        case SENSE_ENVIRONMENT:
            // Wake up camera and grab a frame
            // Capture 640x640 frame for the quantized model
            Frame data = captureFrame(); 
            system.currentState = DETECT_WILDLIFE;
            break;

        case DETECT_WILDLIFE:
            // Run inference on the Quantized Model
            float prediction = runInference(data);
            
            // Threshold logic (tuned via PR Curves [cite: 184])
            if (prediction > 0.85) { 
                printf("Wildlife Detected! Probability: %.2f\n", prediction);
                system.currentState = TRIGGER_DETERRENT;
            } else {
                printf("Object is 'Nothing/Drone'. Return to sleep.\n");
                system.currentState = IDLE_LOW_POWER;
            }
            break;

        case TRIGGER_DETERRENT:
            // Activate audio/visual deterrents
            activatePiezo();
            logEvent("Bird Repelled");
            delay(2000); 
            system.currentState = IDLE_LOW_POWER;
            break;
    }
}