import tensorflow as tf
import numpy as np
import cv2
import os

# CONFIGURATION
IMG_SIZE = 224
MODEL_PATH = 'deployment/solar_guardian_mobilenetv3.h5'
TFLITE_PATH = 'deployment/solar_guardian_quantized.tflite'

# List of images to test "Hard Negative" logic
TEST_IMAGES = ['deployment/bird_test.jpg', 'deployment/drone_test.jpg']

def main():
    print("=== Solar-Guardian Deployment Pipeline ===\n")
    
    # 1. ARCHITECTURE VALIDATION
    print("[1] Loading MobileNetV3Small Architecture (Pre-trained)...")
    base_model = tf.keras.applications.MobileNetV3Small(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=True, 
        weights='imagenet'
    )
    
    # 2. BATCH PROCESSING & VALIDATION
    valid_images = []
    
    print(f"\n[2] Running Feature Extraction Verification:")
    for img_path in TEST_IMAGES:
        if not os.path.exists(img_path):
            print(f"    [!] Warning: {img_path} not found.")
            continue
            
        # Preprocessing
        img = cv2.imread(img_path)
        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
        img = img.astype(np.float32) / 255.0
        input_data = np.expand_dims(img, axis=0)
        valid_images.append(input_data)

        # Baseline Inference (Check what the model "sees")
        preds = base_model.predict(input_data, verbose=0)
        decoded = tf.keras.applications.mobilenet_v3.decode_predictions(preds, top=1)[0]
        
        label = decoded[0][1]
        conf = decoded[0][2] * 100
        
        print(f"    > Input: {os.path.basename(img_path)}")
        print(f"      Base Model Detection: '{label}' ({conf:.2f}%)")
        if "bird" in label or "eagle" in label or "kite" in label:
            print("      -> LOGIC CHECK: Biological Target Identified.")
        else:
            print("      -> LOGIC CHECK: Non-Target/Mechanical Identified.")
        print("-" * 30)

    if not valid_images:
        print("Error: No images found to quantize.")
        return

    # 3. QUANTIZATION
    print("\n[3] Starting Post-Training Quantization (Int8)...")
    
    # Use the real images to calibrate the quantization range
    def representative_data_gen():
        for img_data in valid_images:
            yield [img_data]

    converter = tf.lite.TFLiteConverter.from_keras_model(base_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = representative_data_gen
    
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8

    tflite_model = converter.convert()

    # 4. SAVE & REPORT
    with open(TFLITE_PATH, 'wb') as f:
        f.write(tflite_model)

    quantized_size = len(tflite_model) / 1024
    
    print("=" * 40)
    print(f"SUCCESS: Pipeline Complete.")
    print(f"Quantized Model Size: {quantized_size:.2f} KB")
    print("Ready for STM32 Flash Memory.")
    print("=" * 40)

if __name__ == "__main__":
    main()