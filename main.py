import os
from tkinter import Tk, Label, Button, Entry, Radiobutton, StringVar, Frame, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont

uploaded_file_path = ""

# ----------------------------- FUNCTIONS ----------------------------- #
def upload_image():
    global uploaded_file_path
    file_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.tiff")]
    )
    if file_path:
        uploaded_file_path = file_path
        # Extract and display just the file name instead of the absolute path
        file_name = os.path.basename(file_path)
        file_label.config(text=f"Selected: {file_name}", fg="#2e7d32")


def save_watermarked_image():
    global uploaded_file_path
    if not uploaded_file_path:
        messagebox.showwarning("Warning", "Please upload an image first!")
        return

    text_to_add = text_entry.get().strip().upper()
    if not text_to_add:
        messagebox.showwarning("Warning", "Please enter watermark text!")
        return

    try:
        # Open original image and convert to RGBA for transparency support
        base_image = Image.open(uploaded_file_path).convert("RGBA")

        # Create a blank, completely transparent overlay layer for the text
        txt_layer = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        # Dynamic Font Scaling: Scales the font size relative to image width
        image_width, image_height = base_image.size
        font_size = int(image_width / 15)

        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        # Determine color contrast based on user's selection (50% opacity)
        if color_mode.get() == "dark":
            text_color = (0, 0, 0, 128)
        else:
            text_color = (255, 255, 255, 128)

        # Position the text exactly in the center of the canvas
        text_bbox = draw.textbbox((0, 0), text_to_add, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        x_position = (image_width - text_width) // 2
        y_position = (image_height - text_height) // 2

        # Draw text onto the transparent overlay layer
        draw.text((x_position, y_position), text_to_add, fill=text_color, font=font)

        # Composite the layers together and drop the alpha channel for saving
        combined_image = Image.alpha_composite(base_image, txt_layer)
        final_image = combined_image.convert("RGB")

        # Extract original details to format the default save filename
        original_dir = os.path.dirname(uploaded_file_path)
        original_full_name = os.path.basename(uploaded_file_path)
        name_part, ext_part = os.path.splitext(original_full_name)

        suggested_filename = f"{name_part}_watermark{ext_part}"

        # Open the save dialogue pre-configured with our filename proposal
        save_path = filedialog.asksaveasfilename(
            initialdir=original_dir,
            initialfile=suggested_filename,
            defaultextension=ext_part,
            filetypes=[("PNG file", "*.png"), ("JPEG file", "*.jpg;*.jpeg"), ("All Files", "*.*")]
        )

        if save_path:
            final_image.save(save_path)
            messagebox.showinfo("Success", f"Image saved successfully!\nLocation: {os.path.basename(save_path)}")

            # Auto-reset after successful export
            uploaded_file_path = ""
            file_label.config(text="No file selected", fg="#86868b")
            text_entry.delete(0, "end")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while processing the image:\n{str(e)}")

# ---------------------------- UI SETUP ---------------------------- #
window = Tk()
window.title("Image Watermark Tool")
window.config(padx=40, pady=40, bg="#f5f5f7")
window.geometry("500x450")
window.resizable(False, False)

# Main Title
title_label = Label(text="Image Watermarking Tool", font=("Arial", 18, "bold"), bg="#f5f5f7", fg="#1d1d1f")
title_label.pack(pady=(0, 20))

# Upload Layout
upload_frame = Frame(window, bg="#f5f5f7")
upload_frame.pack(fill="x", pady=10)

upload_btn = Button(upload_frame, text="Choose Image", font=("Arial", 10), command=upload_image, width=15)
upload_btn.pack(side="left", padx=(0, 10))

file_label = Label(upload_frame, text="No file selected", font=("Arial", 10, "italic"), bg="#f5f5f7", fg="#86868b")
file_label.pack(side="left")

# Watermark Text Input
text_label = Label(window, text="Watermark Text (Will automatically uppercase):", font=("Arial", 10, "bold"),
                   bg="#f5f5f7", fg="#1d1d1f")
text_label.pack(anchor="w", pady=(15, 5))

text_entry = Entry(window, font=("Arial", 12), width=40)
text_entry.pack(ipady=4, pady=(0, 10))
text_entry.focus()

# Contrast Toggle Selection
toggle_label = Label(window, text="Image Background Context:", font=("Arial", 10, "bold"), bg="#f5f5f7", fg="#1d1d1f")
toggle_label.pack(anchor="w", pady=(10, 5))

color_mode = StringVar(value="dark")  # Default option

radio_light_bg = Radiobutton(
    window, text="Light Background (Applies Dark Text)",
    variable=color_mode, value="dark", bg="#f5f5f7", font=("Arial", 10)
)
radio_light_bg.pack(anchor="w", padx=10)

radio_dark_bg = Radiobutton(
    window, text="Dark Background (Applies Light Text)",
    variable=color_mode, value="light", bg="#f5f5f7", font=("Arial", 10)
)
radio_dark_bg.pack(anchor="w", padx=10, pady=(0, 20))

# Section 4: Process Action Layout
save_btn = Button(
    window, text="Apply Watermark & Save", font=("Arial", 12, "bold"),
    bg="#0071e3", fg="white", activebackground="#0077ed", activeforeground="white",
    command=save_watermarked_image, padx=10, pady=5
)
save_btn.pack(pady=20)

# -------------------------- MAIN EXECUTION --------------------------- #
window.mainloop()
