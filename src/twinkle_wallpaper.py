import tkinter as tk
from tkinter import messagebox
from tkcolorpicker import askcolor  # Correct import
from PIL import Image, ImageDraw
import random

# Global variables
root = None
selected_colors = []

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def add_color():
    if len(selected_colors) >= 3:
        messagebox.showwarning("Limit Reached", "Only 3 colors are allowed.", icon='warning')
        return

    # Show color wheel picker
    color_code = askcolor(title="Choose a Star Color")  # Use askcolor here
    if color_code[1]:
        selected_colors.append(hex_to_rgb(color_code[1]))
        color_listbox.insert(tk.END, color_code[1])

def clear_colors():
    selected_colors.clear()
    color_listbox.delete(0, tk.END)

def blend_colors(color1, color2, ratio):
    return tuple(
        int(c1 * (1 - ratio) + c2 * ratio)
        for c1, c2 in zip(color1, color2)
    )

def draw_star(draw, x, y, color1, color2, color3, brightness=1.0, size=20, is_large=True):
    thickness = 3  # Decreased thickness to make stars thinner

    # Star size adjustments
    star_size = size if is_large else size // 4  # Adjust for small stars (small stars are now 1/4 the size)
    center_size = star_size // 4  # Smaller center particle for small stars
    
    # Draw arms of the star with extended sides
    for i in range(-star_size * 2, star_size * 2 + 1):  # Extended the range for arms
        ratio = abs(i) / (star_size * 2)  # Adjusted for longer arms
        blended_color = blend_colors(color2, color3, ratio)
        bright_color = tuple(min(255, int(c * brightness)) for c in blended_color)

        for j in range(-thickness, thickness + 1):  # Thinner lines
            draw.point((x + i, y + j), fill=bright_color)
            draw.point((x + j, y + i), fill=bright_color)

    # Smaller center circle (middle particle reduced in size)
    center_color = tuple(min(255, int(c * brightness)) for c in color1)
    left_up = (x - center_size, y - center_size)
    right_down = (x + center_size, y + center_size)
    draw.ellipse([left_up, right_down], fill=center_color)

def generate_star_gif(width=1920, height=1080, num_large_stars=50, num_small_stars=100, output_file="twinkling_stars.gif"):
    if len(selected_colors) != 3:
        messagebox.showerror("Error", "Please select exactly 3 colors.", icon='error')
        return

    color1, color2, color3 = selected_colors
    size = 20  # Size for large stars (half their original size)
    min_spacing = 200  # Increased spacing between stars for more scatter
    frames = []
    num_frames = 4

    # Generate fixed star positions ensuring stars stay within the wallpaper
    placed_large_positions = []
    placed_small_positions = []

    attempts = 0
    while len(placed_large_positions) < num_large_stars and attempts < 5000:
        x = random.randint(size + min_spacing, width - size - min_spacing)
        y = random.randint(size + min_spacing, height - size - min_spacing)
        
        too_close = any(
            abs(x - px) < min_spacing and abs(y - py) < min_spacing
            for px, py in placed_large_positions
        )
        
        if not too_close:
            placed_large_positions.append((x, y))
        
        attempts += 1

    # Generate positions for smaller stars (size matches the small particle size)
    attempts = 0
    while len(placed_small_positions) < num_small_stars and attempts < 5000:
        x = random.randint(size // 4 + min_spacing, width - size // 4 - min_spacing)  # Small stars are size // 4
        y = random.randint(size // 4 + min_spacing, height - size // 4 - min_spacing)
        
        too_close = any(
            abs(x - px) < min_spacing and abs(y - py) < min_spacing
            for px, py in placed_small_positions
        )
        
        if not too_close:
            placed_small_positions.append((x, y))
        
        attempts += 1

    # Generate 4 frames with variance in star size and particle flicker
    for _ in range(num_frames):
        image = Image.new("RGB", (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw large stars
        for x, y in placed_large_positions:
            brightness = random.uniform(0.4, 1.0)  # Flicker effect
            draw_star(draw, x, y, color1, color2, color3, brightness, size, is_large=True)

        # Draw small stars
        for x, y in placed_small_positions:
            brightness = random.uniform(0.2, 0.8)  # Slightly dimmer brightness for particles
            draw_star(draw, x, y, color1, color2, color3, brightness, size, is_large=False)

        frames.append(image)

    frames[0].save(
        output_file,
        save_all=True,
        append_images=frames[1:],
        duration=300,
        loop=0
    )

    messagebox.showinfo("Done", f"GIF saved as '{output_file}'", icon='info')
    root.destroy()

def create_gui():
    global root
    root = tk.Tk()
    root.tk_setPalette(background='#2E2E2E')  # Set the background color to dark gray
    root.title("Twinkling Star GIF Generator")
    root.geometry("320x400")

    # Styling labels and buttons for dark mode
    label = tk.Label(root, text="Choose exactly 3 colors (center to outer arms):", fg="white", bg="#2E2E2E")
    label.pack(pady=10)

    btn_add = tk.Button(root, text="Add Color", command=add_color, bg="#555555", fg="white")
    btn_add.pack()

    global color_listbox
    color_listbox = tk.Listbox(root, width=30, height=5, bg="#3A3A3A", fg="white")
    color_listbox.pack(pady=10)

    btn_clear = tk.Button(root, text="Clear Colors", command=clear_colors, bg="#555555", fg="white")
    btn_clear.pack()

    btn_generate = tk.Button(root, text="Generate Twinkling GIF", command=generate_star_gif, bg="#333333", fg="white")
    btn_generate.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
    