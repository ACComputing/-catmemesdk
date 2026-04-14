"""
CatMemeGen 3.0
Flux 1 / Flux 2 / Turbo engine switcher - Threaded generation
Negative prompts - Seed lock - Aspect presets - Accurate meme mode
Python 3.14 / Tcl 9 compatible
"""

import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
import requests
from io import BytesIO
from urllib.parse import quote
import random
import threading
import os

# ===== Theme =====
BG_BLACK  = "#000000"
PANEL_BG  = "#0a0a0a"
SUB_BG    = "#050505"
ENTRY_BG  = "#111111"
BTN_BG    = "#000000"
BTN_FG    = "#4aa3ff"
ACCENT    = "#4aa3ff"
ACCENT_HI = "#ff00aa"
WHITE     = "#FFFFFF"
MUTED     = "#666666"
OK_GREEN  = "#00ff88"

# ===== Engine registry =====
ENGINES = {
    "Flux 2 (best quality)":   {"model": "flux",          "endpoint": "pollinations"},
    "Flux 1 Schnell (fast)":   {"model": "turbo",         "endpoint": "pollinations"},
    "Flux Realism":            {"model": "flux-realism",  "endpoint": "pollinations"},
    "Flux Anime":              {"model": "flux-anime",    "endpoint": "pollinations"},
    "Flux 3D":                 {"model": "flux-3d",       "endpoint": "pollinations"},
    "Stable Diffusion XL":     {"model": "sdxl",          "endpoint": "pollinations"},
}

ASPECTS = {
    "Square 1:1 (1024x1024)":    (1024, 1024),
    "Portrait 3:4 (768x1024)":   (768, 1024),
    "Landscape 4:3 (1024x768)":  (1024, 768),
    "Wide 16:9 (1280x720)":      (1280, 720),
    "Tall 9:16 (720x1280)":      (720, 1280),
}

DEFAULT_NEGATIVE = (
    "blurry, low quality, distorted text, garbled letters, watermark, "
    "signature, jpeg artifacts, extra limbs, deformed, ugly, cropped"
)


class CatMemeGen:
    def __init__(self, root):
        self.root = root
        self.root.title("AC's Meme Generator 0.1")  # ✅ CHANGED HERE
        self.root.geometry("1280x820")
        self.root.minsize(1000, 680)
        self.root.configure(bg=BG_BLACK)

        self.image = None
        self.preview_img = None
        self.tk_img = None
        self.dragging = None
        self.generating = False
        self._img_offset = (0, 0)

        self.text_color = WHITE
        self.stroke_color = "#000000"
        self.font_size = 56
        self.stroke_width = 5

        self.top_text = tk.StringVar(value="TOP TEXT")
        self.bottom_text = tk.StringVar(value="BOTTOM TEXT")

        self.top_pos = [0.5, 0.08]
        self.bottom_pos = [0.5, 0.82]

        self.neg_prompt = tk.StringVar(value=DEFAULT_NEGATIVE)
        self.engine_name = tk.StringVar(value="Flux 2 (best quality)")
        self.aspect_name = tk.StringVar(value="Square 1:1 (1024x1024)")
        self.seed_var = tk.StringVar(value="")
        self.accurate_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Ready.")

        self.templates = {
            "Drake": "https://i.imgflip.com/30b1gx.jpg",
            "Distracted Boyfriend": "https://i.imgflip.com/1ur9b0.jpg",
            "Two Buttons": "https://i.imgflip.com/1g8my4.jpg",
            "Woman Cat": "https://i.imgflip.com/345v97.jpg",
            "Expanding Brain": "https://i.imgflip.com/1jwhww.jpg",
            "Change My Mind": "https://i.imgflip.com/24y43o.jpg",
        }

        self.build_ui()

    # (rest of your code stays EXACTLY the same)
    # I did not modify any logic, only the window title line.

if __name__ == "__main__":
    root = tk.Tk()
    app = CatMemeGen(root)
    root.mainloop()
