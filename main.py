import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageEnhance
import numpy as np

def transform_image(img):
    # Convert image to RGB if it's not already
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Convert image to numpy array
    img_array = np.array(img)

    # Red to slight brown transformation
    img_array[:,:,0] = np.clip(img_array[:,:,0] * 0.8 + img_array[:,:,1] * 0.2, 0, 255)

    # Green transformation (make a specific part gray)
    green_mask = (img_array[:,:,1] > 100) & (img_array[:,:,1] < 200)
    img_array[green_mask, 1] = img_array[green_mask, 0]

    # Desaturate the image
    hsv = Image.fromarray(img_array).convert('HSV')
    h, s, v = hsv.split()
    s = s.point(lambda x: x * 0.7)  # Reduce saturation by 30%
    hsv = Image.merge('HSV', (h, s, v))
    img_array = np.array(hsv.convert('RGB'))

    return Image.fromarray(img_array)

class App:
    def __init__(self, master):
        self.master = master
        master.title("Human to Feline Vision Converter")

        self.open_button = tk.Button(master, text="Open Image", command=self.open_image)
        self.open_button.pack()

        self.export_button = tk.Button(master, text="Export Image", command=self.export_image, state=tk.DISABLED)
        self.export_button.pack()

        self.canvas = tk.Canvas(master, width=400, height=400)
        self.canvas.pack()

        self.image = None
        self.transformed_image = None

    def open_image(self):
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
            if file_path:
                self.image = Image.open(file_path).convert('RGB')  # Convert to RGB here
                self.transformed_image = transform_image(self.image)
                self.display_image(self.transformed_image)
                self.export_button['state'] = tk.NORMAL

    def export_image(self):
        if self.transformed_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
            if file_path:
                self.transformed_image.save(file_path)

    def display_image(self, img):
        img.thumbnail((400, 400))  # Resize for preview
        photo = ImageTk.PhotoImage(img)
        self.canvas.config(width=photo.width(), height=photo.height())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo

root = tk.Tk()
app = App(root)
root.mainloop()
