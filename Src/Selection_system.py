import os, image_system
from tkinter import Tk, filedialog
from PIL import Image

root = Tk()
root.withdraw()

folder_path = filedialog.askdirectory(title="Select a folder containing JPG images")
output_path = filedialog.askdirectory(title="Select a folder for the output images")

portrait_images = []
landscape_images = []

jpg_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".jpg")]

jpg_files.sort()

for filename in jpg_files:
    file_path = os.path.join(folder_path, filename)
    
    with Image.open(file_path) as img:
        width, height = img.size
        
        if height > width:
            portrait_images.append(filename)
        else:
            landscape_images.append(filename)

portrait_pairs = []
landscape_pairs = []

for i in range(0, len(portrait_images), 2):
    pair = portrait_images[i:i+2]
    if len(pair) == 2:
        portrait_pairs.append((pair[0], pair[1]))

for i in range(0, len(landscape_images), 2):
    pair = landscape_images[i:i+2]
    if len(pair) == 2:
        landscape_pairs.append((pair[0], pair[1]))

print("Portrait Images:", portrait_images)
print("Landscape Images:", landscape_images)

print("\nPortrait Pairs:")
for idx, (img1, img2) in enumerate(portrait_pairs, start=1):
    print(f"portrait_{idx}_a = '{img1}'")
    print(f"portrait_{idx}_b = '{img2}'")
    image_system.portrait.process_portrait(os.path.join(folder_path, img1),
                              os.path.join(folder_path, img2),
                              os.path.join(output_path, f"portrait_{idx}.jpg") )

print("\nLandscape Pairs:")
for idx, (img1, img2) in enumerate(landscape_pairs, start=1):
    print(f"landscape_{idx}_a = '{img1}'")
    print(f"landscape_{idx}_b = '{img2}'")
    image_system.landscape.process_landscape(os.path.join(folder_path, img1),
                              os.path.join(folder_path, img2),
                              os.path.join(output_path, f"landscape_{idx}.jpg") )