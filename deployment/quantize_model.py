import tensorflow as tf
import numpy as np
import os

def create_dummy_model():
    """Creates a simple MobileNetV3-style model for demonstration."""
    print("No .h5 model found. Creating a dummy MobileNetV3 model for demonstration...")
    # Create a simple model that mimics MobileNetV3 input shape
    inputs = tf.keras.Input(shape=(640, 640, 3))
    x = tf.keras.layers.Conv2D(16, (3, 3), strides=2, padding='same')(inputs)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.ReLU()(x)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    outputs = tf.keras.layers.Dense(2, activation='softmax')(x) # 2 classes: Wildlife vs Nothing
    
    model = tf.keras.Model(inputs, outputs)
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')
    
    # Save it so we can load it back (simulating a real workflow)
    model.save('solar_guardian_model.h5')
    print("Dummy model created and saved as 'solar_guardian_model.h5'.")
    return model

def main():
    model_path = 'solar_guardian_model.h5'
    
    # Check if model exists, if not, create a dummy one
    if not os.path.exists(model_path):
        model = create_dummy_model()
    else:
        model = tf.keras.models.load_model(model_path)

    # Initialize TFLite Converter
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    # OPTIMIZATION: Quantize for Edge Devices (STM32/ESP32)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    # Representative Dataset Generator (Mocking real data)
    def representative_data_gen():
        for _ in range(10):
            # Generate random noise to simulate image data
            # FIXED LINE BELOW:
            data = np.random.uniform(0, 1, size=(1, 640, 640, 3)).astype(np.float32)
            yield [data]

    converter.representative_dataset = representative_data_gen
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8

    print("Converting model to TFLite (Int8)...")
    tflite_model = converter.convert()

    # Save the quantized model
    output_path = 'deployment/solar_guardian_quantized.tflite'
    with open(output_path, 'wb') as f:
        f.write(tflite_model)

    # Calculate Compression
    original_size = os.path.getsize(model_path)
    quantized_size = len(tflite_model)
    reduction = (1 - (quantized_size / original_size)) * 100

    print("-" * 30)
    print(f"Original Model Size: {original_size / 1024:.2f} KB")
    print(f"Quantized Model Size: {quantized_size / 1024:.2f} KB")
    print(f"COMPRESSION SUCCESS: Reduced by {reduction:.2f}%")
    print("-" * 30)

if __name__ == "__main__":
    main()