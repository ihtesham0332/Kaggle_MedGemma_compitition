import numpy as np
from PIL import Image
import pydicom

def apply_window(image: np.ndarray, center: float, width: float) -> np.ndarray:
    """
    Applies a standard CT windowing to a 2D image.
    
    Args:
        image (np.ndarray): The raw CT image data (Hounsfield Units).
        center (float): The window center (level).
        width (float): The window width.
        
    Returns:
        np.ndarray: The windowed image, normalized to 0-255.
    """
    min_value = center - width // 2
    max_value = center + width // 2
    
    windowed = np.clip(image, min_value, max_value)
    windowed = (windowed - min_value) / (max_value - min_value)
    return windowed

def process_ct_slice(dicom_path: str, output_size: tuple = (896, 896)) -> Image.Image:
    """
    Reads a DICOM file and converts it to a 3-channel RGB image
    optimized for MedGemma 1.5.
    
    Channels:
    - Red: Wide Window (Lung/Bone focus) - W: 1500, L: -600 (Lung) or W:2000, L:0 (General Wide)
           Let's use a Wide range: Center=0, Width=2000
    - Green: Soft Tissue Window - W: 400, L: 50
    - Blue: Bone Window - W: 1800, L: 400
    
    Args:
        dicom_path (str): Path to the DICOM file.
        output_size (tuple): Target size for the output image (width, height).
        
    Returns:
        PIL.Image.Image: The processed RGB image.
    """
    try:
        dcm = pydicom.dcmread(dicom_path)
        # Convert to Hounsfield Units (HU)
        image = dcm.pixel_array.astype(np.float32)
        image = image * dcm.RescaleSlope + dcm.RescaleIntercept
    except Exception as e:
        print(f"Error reading DICOM {dicom_path}: {e}")
        # Return a black image in case of error, or raise
        return Image.new("RGB", output_size, (0, 0, 0))

    # 1. Red Channel: Wide Window (Captures overall structure)
    # Using W:2000, L:0 typically covers a lot. 
    # Or specific "Lung" W:1500, L:-600. 
    # The prompt asked for "Red: Wide". Let's go with W:2000, L:0 which is a good "wide" view.
    r_channel = apply_window(image, center=0, width=2000)

    # 2. Green Channel: Soft Tissue (Standard abdominal)
    # W: 400, L: 50
    g_channel = apply_window(image, center=50, width=400)

    # 3. Blue Channel: Brain/Bone (High density)
    # Bone W: 1800, L: 400
    b_channel = apply_window(image, center=400, width=1800)

    # Stack into RGB
    rgb = np.dstack((r_channel, g_channel, b_channel))
    
    # Convert to 8-bit [0, 255]
    rgb = (rgb * 255).astype(np.uint8)
    
    # Create PIL Image
    pil_img = Image.fromarray(rgb)
    
    # Resize
    if pil_img.size != output_size:
        pil_img = pil_img.resize(output_size, Image.Resampling.LANCZOS)
        
    return pil_img

if __name__ == "__main__":
    # Example usage
    import sys
    import os
    
    if len(sys.argv) > 1:
        dcm_file = sys.argv[1]
        if os.path.exists(dcm_file):
            img = process_ct_slice(dcm_file)
            img.save("processed_ct.png")
            print("Saved processed_ct.png")
        else:
            print(f"File not found: {dcm_file}")
    else:
        print("Usage: python preprocess.py <path_to_dicom_file>")
