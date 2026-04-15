import os, image_system
from tkinter import Tk, filedialog
from PIL import Image

root = Tk()
root.withdraw()

folder_path = filedialog.askdirectory(title="Select a folder containing JPG images")
output_path = filedialog.askdirectory(title="Select a folder for the output images")

portrait_images = []
landscape_images = []

jpg_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(".jpg")])

for filename in jpg_files:
    file_path = os.path.join(folder_path, filename)
    with Image.open(file_path) as img:
        width, height = img.size
        if height > width:
            portrait_images.append(filename)
        else:
            landscape_images.append(filename)

# --- Process Portraits ---
print("\nProcessing Portraits...")
for i in range(0, len(portrait_images), 2):
    img1 = portrait_images[i]
    img2 = portrait_images[i+1] if (i + 1) < len(portrait_images) else None
    
    out_file = os.path.join(output_path, f"portrait_{i//2 + 1}.jpg")
    
    image_system.portrait.process_portrait(
        os.path.join(folder_path, img1),
        os.path.join(folder_path, img2) if img2 else None,
        out_file
    )

# --- Process Landscapes ---
print("\nProcessing Landscapes...")
for i in range(0, len(landscape_images), 2):
    img1 = landscape_images[i]
    img2 = landscape_images[i+1] if (i + 1) < len(landscape_images) else None
    
    out_file = os.path.join(output_path, f"landscape_{i//2 + 1}.jpg")
    
    image_system.landscape.process_landscape(
        os.path.join(folder_path, img1),
        os.path.join(folder_path, img2) if img2 else None,
        out_file
    )