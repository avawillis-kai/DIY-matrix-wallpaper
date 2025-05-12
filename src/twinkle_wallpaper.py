import tkinter as tk
from tkinter import messagebox
from tkcolorpicker import askcolor
from PIL import Image, ImageDraw
import random
import math

# Global variables
root = None
selected_colors = []
selected_shape = None  # Set it to None initially

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def add_color():
    if len(selected_colors) >= 4:
        messagebox.showwarning("Limit Reached", "You can only select a maximum of 4 colors.", icon='warning')
        return

    color_code = askcolor(title="Choose a Star Color")
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

def draw_star(draw, x, y, colors, brightness=1.0, size=16, is_large=True):
    thickness = 3
    star_size = size if is_large else size // 4
    center_size = star_size // 3  # Making the center shape larger for prominence
    border_size = center_size + 2  # Adding a slight border for the center

    def get_blended_color(ratio):
        if len(colors) == 1:
            return colors[0]
        elif len(colors) == 2:
            return blend_colors(colors[0], colors[1], ratio)
        elif len(colors) == 3:
            return blend_colors(
                blend_colors(colors[0], colors[1], ratio),
                colors[2],
                ratio
            )
        else:  # 4 colors
            if ratio < 1/3:
                return blend_colors(colors[0], colors[1], ratio * 3)
            elif ratio < 2/3:
                return blend_colors(colors[1], colors[2], (ratio - 1/3) * 3)
            else:
                return blend_colors(colors[2], colors[3], (ratio - 2/3) * 3)

    # Drawing the twinkling star arms
    for i in range(-star_size * 2, star_size * 2 + 1):
        ratio = abs(i) / (star_size * 2)
        blended_color = get_blended_color(ratio)
        bright_color = tuple(min(255, int(c * brightness)) for c in blended_color)

        for j in range(-thickness, thickness + 1):
            draw.point((x + i, y + j), fill=bright_color)
            draw.point((x + j, y + i), fill=bright_color)

    # Now drawing the center shape with enhanced prominence
    center_color = tuple(min(255, int(c * brightness)) for c in colors[0])
    left_up = (x - center_size, y - center_size)
    right_down = (x + center_size, y + center_size)

    # Optional: Add a border effect for the center shape
    border_color = (255, 255, 255)  # White border (you can change to any color)

    shape = selected_shape.get()
    if shape == "Circle":
        # Draw border first, then the center circle
        draw.ellipse([left_up, right_down], outline=border_color, width=2)  # Border effect
        draw.ellipse([left_up, right_down], fill=center_color)
    elif shape == "Square":
        # Draw border first, then the center square
        draw.rectangle([left_up, right_down], outline=border_color, width=2)  # Border effect
        draw.rectangle([left_up, right_down], fill=center_color)
    elif shape == "Star":
        # Draw the "X" shape for the center of the star
        draw.line((x - center_size, y - center_size, x + center_size, y + center_size), fill=border_color, width=2)
        draw.line((x + center_size, y - center_size, x - center_size, y + center_size), fill=border_color, width=2)
        draw.line((x - center_size, y - center_size, x + center_size, y + center_size), fill=center_color, width=2)
        draw.line((x + center_size, y - center_size, x - center_size, y + center_size), fill=center_color, width=2)

def generate_star_gif(width=1920, height=1080, num_large_stars=100, num_small_stars=350, output_file="twinkling_stars.gif"):
    if len(selected_colors) < 1 or len(selected_colors) > 4:
        messagebox.showerror("Error", "Please select between 1 and 4 colors.", icon='error')
        return

    colors = selected_colors
    size = 16
    min_edge_margin = 40
    min_star_spacing = 80
    min_large_small_distance = 60
    frames = []
    num_frames = 100

    placed_large_positions = []
    placed_small_positions = []

    for _ in range(num_large_stars):
        x = random.randint(min_edge_margin, width - min_edge_margin)
        y = random.randint(min_edge_margin, height - min_edge_margin)
        too_close = any(((x - px)**2 + (y - py)**2)**0.5 < min_star_spacing for px, py in placed_large_positions)
        if not too_close:
            placed_large_positions.append([x, y])

    for _ in range(num_small_stars):
        x = random.randint(min_edge_margin, width - min_edge_margin)
        y = random.randint(min_edge_margin, height - min_edge_margin)
        too_close = any(((x - px)**2 + (y - py)**2)**0.5 < min_star_spacing / 2 for px, py in placed_small_positions) or \
                    any(((x - lx)**2 + (y - ly)**2)**0.5 < min_large_small_distance for lx, ly in placed_large_positions)
        if not too_close:
            placed_small_positions.append([x, y])

    for frame_num in range(num_frames):
        image = Image.new("RGB", (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        brightness_factor = 0.5 + 0.5 * math.sin((2 * math.pi * frame_num) / (num_frames // 2))
        move_large = width / num_frames
        move_small = move_large * 1.2

        for star in placed_large_positions:
            x, y = star
            brightness = random.uniform(0.4, 1.0) * brightness_factor
            draw_star(draw, x, y, colors, brightness, size, is_large=True)
            star[0] += move_large
            if star[0] > width + size:
                star[0] = -size

        for star in placed_small_positions:
            x, y = star
            brightness = random.uniform(0.2, 0.8) * brightness_factor
            draw_star(draw, x, y, colors, brightness, size, is_large=False)
            star[0] += move_small
            if star[0] > width + size:
                star[0] = -size

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
    global root, selected_shape
    root = tk.Tk()
    root.tk_setPalette(background='#2E2E2E')
    root.title("Twinkling Star GIF Generator")
    root.geometry("360x460")

    selected_shape = tk.StringVar(value="Star")  # Moved here to after root window creation

    label = tk.Label(root, text="Choose 1 to 4 colors (center to outer arms):", fg="white", bg="#2E2E2E")
    label.pack(pady=10)

    btn_add = tk.Button(root, text="Add Color", command=add_color, bg="#555555", fg="white")
    btn_add.pack()

    global color_listbox
    color_listbox = tk.Listbox(root, width=30, height=5, bg="#3A3A3A", fg="white")
    color_listbox.pack(pady=10)

    btn_clear = tk.Button(root, text="Clear Colors", command=clear_colors, bg="#555555", fg="white")
    btn_clear.pack()

    shape_label = tk.Label(root, text="Choose center shape:", fg="white", bg="#2E2E2E")
    shape_label.pack(pady=10)

    shape_frame = tk.Frame(root, bg="#2E2E2E")
    shape_frame.pack()

    tk.Radiobutton(shape_frame, text="Star", variable=selected_shape, value="Star", bg="#2E2E2E", fg="white", selectcolor="#2E2E2E").pack(side=tk.LEFT)
    tk.Radiobutton(shape_frame, text="Circle", variable=selected_shape, value="Circle", bg="#2E2E2E", fg="white", selectcolor="#2E2E2E").pack(side=tk.LEFT)
    tk.Radiobutton(shape_frame, text="Square", variable=selected_shape, value="Square", bg="#2E2E2E", fg="white", selectcolor="#2E2E2E").pack(side=tk.LEFT)

    btn_generate = tk.Button(root, text="Generate Twinkling GIF", command=generate_star_gif, bg="#333333", fg="white")
    btn_generate.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()