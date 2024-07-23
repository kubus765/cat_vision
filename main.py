import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import colorsys
from threading import Timer
import json
import os

class App:
    def __init__(self, master):
        self.master = master
        master.title("Human to Feline Vision Converter")
        
        self.open_button = tk.Button(master, text="Open Image", command=self.open_image)
        self.open_button.pack()

        # Sliders for color transformations
        self.yellow_start = tk.DoubleVar(value=0.0)
        self.yellow_end = tk.DoubleVar(value=116.0)

        self.desaturation_strength = tk.DoubleVar(value=0.0)
        self.desaturation_center = tk.DoubleVar(value=0.0)
        self.desaturation_width = tk.DoubleVar(value=0.1)
        self.desaturation_shift = tk.DoubleVar(value=0.0)

        self.desaturation2_strength = tk.DoubleVar(value=0.0)
        self.desaturation2_center = tk.DoubleVar(value=0.0)
        self.desaturation2_width = tk.DoubleVar(value=0.1)
        self.desaturation2_shift = tk.DoubleVar(value=0.0)

        self.overall_saturation = tk.DoubleVar(value=1.0)

        # Slider widgets
        self.yellow_start_slider = tk.Scale(master, from_=0.0, to=360.0, resolution=1.0, orient=tk.HORIZONTAL, label="Yellow Start (Hue Angle)", variable=self.yellow_start)
        self.yellow_start_slider.pack()

        self.yellow_end_slider = tk.Scale(master, from_=0.0, to=360.0, resolution=1.0, orient=tk.HORIZONTAL, label="Yellow End (Hue Angle)", variable=self.yellow_end)
        self.yellow_end_slider.pack()

        self.desaturation_strength_slider = tk.Scale(master, from_=0.0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, label="Desaturation 1 Strength", variable=self.desaturation_strength)
        self.desaturation_strength_slider.pack()

        self.desaturation_center_slider = tk.Scale(master, from_=0.0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, label="Desaturation 1 Center", variable=self.desaturation_center)
        self.desaturation_center_slider.pack()

        self.desaturation_width_slider = tk.Scale(master, from_=0.0, to=0.5, resolution=0.01, orient=tk.HORIZONTAL, label="Desaturation 1 Width", variable=self.desaturation_width)
        self.desaturation_width_slider.pack()

        self.desaturation_shift_slider = tk.Scale(master, from_=-0.5, to=0.5, resolution=0.01, orient=tk.HORIZONTAL, label="Desaturation 1 Shift", variable=self.desaturation_shift)
        self.desaturation_shift_slider.pack()

        self.desaturation2_strength_slider = tk.Scale(master, from_=0.0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, label="Desaturation 2 Strength", variable=self.desaturation2_strength)
        self.desaturation2_strength_slider.pack()

        self.desaturation2_center_slider = tk.Scale(master, from_=0.0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, label="Desaturation 2 Center", variable=self.desaturation2_center)
        self.desaturation2_center_slider.pack()

        self.desaturation2_width_slider = tk.Scale(master, from_=0.0, to=0.5, resolution=0.01, orient=tk.HORIZONTAL, label="Desaturation 2 Width", variable=self.desaturation2_width)
        self.desaturation2_width_slider.pack()

        self.desaturation2_shift_slider = tk.Scale(master, from_=-0.5, to=0.5, resolution=0.01, orient=tk.HORIZONTAL, label="Desaturation 2 Shift", variable=self.desaturation2_shift)
        self.desaturation2_shift_slider.pack()

        self.overall_saturation_slider = tk.Scale(master, from_=0.0, to=2.0, resolution=0.01, orient=tk.HORIZONTAL, label="Overall Saturation", variable=self.overall_saturation)
        self.overall_saturation_slider.pack()

        self.apply_button = tk.Button(master, text="Apply Transformation", command=self.apply_transformation, state=tk.DISABLED)
        self.apply_button.pack()

        self.export_button = tk.Button(master, text="Export Image", command=self.export_image, state=tk.DISABLED)
        self.export_button.pack()

        self.save_settings_button = tk.Button(master, text="Save Settings", command=self.save_settings)
        self.save_settings_button.pack()

        self.canvas = tk.Canvas(master, width=400, height=400)
        self.canvas.pack()

        self.image = None
        self.transformed_image = None

        # Delayed update variables
        self.update_timer = None
        self.update_delay = 0.5  # seconds

        # Bind sliders to update method with delay
        for slider in [self.yellow_start_slider, self.yellow_end_slider, 
                       self.desaturation_strength_slider, self.desaturation_center_slider, 
                       self.desaturation_width_slider, self.desaturation_shift_slider,
                       self.desaturation2_strength_slider, self.desaturation2_center_slider, 
                       self.desaturation2_width_slider, self.desaturation2_shift_slider,
                       self.overall_saturation_slider]:
            slider.bind("<ButtonRelease-1>", self.start_delayed_update)

        # Load settings if they exist
        self.load_settings()

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
        if file_path:
            self.image = Image.open(file_path)
            self.display_image(self.image)
            self.apply_button['state'] = tk.NORMAL

    def start_delayed_update(self, event=None):
        if self.update_timer is not None:
            self.update_timer.cancel()
        self.update_timer = Timer(self.update_delay, self.update_image)
        self.update_timer.start()

    def apply_transformation(self):
        if self.image:
            yellow_start = self.yellow_start.get()
            yellow_end = self.yellow_end.get()
            desaturation_strength = self.desaturation_strength.get()
            desaturation_center = self.desaturation_center.get()
            desaturation_width = self.desaturation_width.get()
            desaturation_shift = self.desaturation_shift.get()
            desaturation2_strength = self.desaturation2_strength.get()
            desaturation2_center = self.desaturation2_center.get()
            desaturation2_width = self.desaturation2_width.get()
            desaturation2_shift = self.desaturation2_shift.get()
            overall_saturation = self.overall_saturation.get()

            self.transformed_image = transform_image(self.image, yellow_start, yellow_end, 
                                                     desaturation_strength, desaturation_center, desaturation_width, desaturation_shift, 
                                                     desaturation2_strength, desaturation2_center, desaturation2_width, desaturation2_shift, 
                                                     overall_saturation)
            self.display_image(self.transformed_image)
            self.export_button['state'] = tk.NORMAL

    def update_image(self):
        if self.image:
            self.apply_transformation()

    def export_image(self):
        if self.image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
            if file_path:
                yellow_start = self.yellow_start.get()
                yellow_end = self.yellow_end.get()
                desaturation_strength = self.desaturation_strength.get()
                desaturation_center = self.desaturation_center.get()
                desaturation_width = self.desaturation_width.get()
                desaturation_shift = self.desaturation_shift.get()
                desaturation2_strength = self.desaturation2_strength.get()
                desaturation2_center = self.desaturation2_center.get()
                desaturation2_width = self.desaturation2_width.get()
                desaturation2_shift = self.desaturation2_shift.get()
                overall_saturation = self.overall_saturation.get()

                transformed_original = transform_image(self.image, yellow_start, yellow_end, 
                                                       desaturation_strength, desaturation_center, desaturation_width, desaturation_shift, 
                                                       desaturation2_strength, desaturation2_center, desaturation2_width, desaturation2_shift, 
                                                       overall_saturation)
                transformed_original.save(file_path)

    def display_image(self, img):
        max_size = (4000, 4000)
        img.thumbnail(max_size, Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        self.canvas.config(width=photo.width(), height=photo.height())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo

    def save_settings(self):
        settings = {
            'yellow_start': self.yellow_start.get(),
            'yellow_end': self.yellow_end.get(),
            'desaturation_strength': self.desaturation_strength.get(),
            'desaturation_center': self.desaturation_center.get(),
            'desaturation_width': self.desaturation_width.get(),
            'desaturation_shift': self.desaturation_shift.get(),
            'desaturation2_strength': self.desaturation2_strength.get(),
            'desaturation2_center': self.desaturation2_center.get(),
            'desaturation2_width': self.desaturation2_width.get(),
            'desaturation2_shift': self.desaturation2_shift.get(),
            'overall_saturation': self.overall_saturation.get()
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)

    def load_settings(self):
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                settings = json.load(f)
            self.yellow_start.set(settings['yellow_start'])
            self.yellow_end.set(settings['yellow_end'])
            self.desaturation_strength.set(settings['desaturation_strength'])
            self.desaturation_center.set(settings['desaturation_center'])
            self.desaturation_width.set(settings['desaturation_width'])
            self.desaturation_shift.set(settings['desaturation_shift'])
            self.desaturation2_strength.set(settings['desaturation2_strength'])
            self.desaturation2_center.set(settings['desaturation2_center'])
            self.desaturation2_width.set(settings['desaturation2_width'])
            self.desaturation2_shift.set(settings['desaturation2_shift'])
            self.overall_saturation.set(settings['overall_saturation'])

def transform_image(img, yellow_start, yellow_end, 
                    desaturation_strength, desaturation_center, desaturation_width, desaturation_shift,
                    desaturation2_strength, desaturation2_center, desaturation2_width, desaturation2_shift,
                    overall_saturation):
    img = img.convert('RGB')
    img_array = np.array(img)

    hsv_img = np.array([colorsys.rgb_to_hsv(*pixel/255.0) for pixel in img_array.reshape(-1, 3)]).reshape(img_array.shape)
    
    yellow_start = yellow_start / 360.0
    yellow_end = yellow_end / 360.0
    
    if yellow_start > yellow_end:
        yellow_end += 1.0

    hue_img = hsv_img[..., 0]
    
    expansion_range = (yellow_end - yellow_start) / 2.0
    expansion_center = (yellow_start + yellow_end) / 2.0
    
    smooth_expansion = np.clip((1.0 - np.abs(hue_img - expansion_center) / expansion_range), 0, 1)
    
    expanded_hue = np.where(
        (hue_img >= yellow_start) & (hue_img <= yellow_end),
        np.clip(hue_img + (0.12 - hue_img) * smooth_expansion, 0, 1),
        hue_img
    )
    
    def apply_desaturation(hsv_img, strength, center, width, shift):
        center = (center + shift) % 1.0
        transition_width = width / 2

        distance_from_center = np.abs(hsv_img[..., 0] - center)
        distance_from_center = np.minimum(distance_from_center, 1 - distance_from_center)

        mask_center = distance_from_center < (width / 2)
        mask_transition = (distance_from_center >= (width / 2 - transition_width)) & (distance_from_center < (width / 2))

        transition_factor_transition = (distance_from_center[mask_transition] - (width / 2 - transition_width)) / transition_width

        hsv_img[mask_center, 1] = hsv_img[mask_center, 1] * (1 - strength)
        hsv_img[mask_transition, 1] = hsv_img[mask_transition, 1] * (1 - strength * (1 - transition_factor_transition))

        return hsv_img

    hsv_img = apply_desaturation(hsv_img, desaturation_strength, desaturation_center, desaturation_width, desaturation_shift)
    hsv_img = apply_desaturation(hsv_img, desaturation2_strength, desaturation2_center, desaturation2_width, desaturation2_shift)

    hsv_img[..., 0] = expanded_hue
    hsv_img[..., 1] = np.clip(hsv_img[..., 1] * overall_saturation, 0, 1)

    img_array = np.array([colorsys.hsv_to_rgb(*pixel) for pixel in hsv_img.reshape(-1, 3)]).reshape(img_array.shape) * 255.0
    img_array = np.clip(img_array, 0, 255).astype('uint8')
    
    return Image.fromarray(img_array)

root = tk.Tk()
app = App(root)
root.mainloop()
