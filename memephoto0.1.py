"""
CatMemeGen 2.1 - BLACK MODE BLUE UI 🐱
Live Meme Editor + AI Image Generator (Photoshop-style)
Python 3.14 / Tcl 9 compatible • All buttons: black bg, blue text
"""

import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
import requests
from io import BytesIO
from urllib.parse import quote
import random

# ===== Theme =====
BG_BLACK  = "#000000"
PANEL_BG  = "#0a0a0a"
ENTRY_BG  = "#111111"
BTN_BG    = "#000000"   # all buttons black
BTN_FG    = "#4aa3ff"   # all button text blue
ACCENT    = "#4aa3ff"
ACCENT_HI = "#ff00aa"
WHITE     = "#FFFFFF"
MUTED     = "#666666"


class CatMemeGen:
    def __init__(self, root):
        self.root = root
        self.root.title("🐱 CatMemeGen 2.1 - AI Edition")
        self.root.geometry("1150x720")
        self.root.minsize(900, 600)
        self.root.configure(bg=BG_BLACK)

        self.image = None
        self.preview_img = None
        self.tk_img = None
        self.dragging = None

        self.text_color = WHITE
        self.font_size = 48

        self.top_text = tk.StringVar(value="TOP TEXT")
        self.bottom_text = tk.StringVar(value="BOTTOM TEXT")

        self.top_pos = [0.5, 0.15]
        self.bottom_pos = [0.5, 0.85]

        self.ai_prompt = tk.StringVar(value="a cool cat wearing sunglasses riding a rocket ship")

        self.templates = {
            "Drake": "https://i.imgflip.com/30b1gx.jpg",
            "Distracted Boyfriend": "https://i.imgflip.com/1ur9b0.jpg",
            "Two Buttons": "https://i.imgflip.com/1g8my4.jpg",
            "Woman Cat": "https://i.imgflip.com/345v97.jpg",
        }

        self.build_ui()

    # ================= Button helper =================
    def _btn(self, parent, text, command, bold=False, accent=False):
        """Uniform button: black bg, blue text."""
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=BTN_BG,
            fg=ACCENT_HI if accent else BTN_FG,
            activebackground="#1a1a1a",
            activeforeground=BTN_FG,
            font=("Segoe UI", 11, "bold" if bold else "normal"),
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground=BTN_FG,
            highlightcolor=BTN_FG,
            cursor="hand2",
        )

    # ================= UI =================
    def build_ui(self):
        main = tk.Frame(self.root, bg=BG_BLACK)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(main, bg=BG_BLACK, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)

        panel = tk.Frame(main, bg=PANEL_BG, width=300)
        panel.pack(side=tk.RIGHT, fill=tk.Y)
        panel.pack_propagate(False)

        tk.Label(
            panel,
            text="🐱 CATMEMEGEN 2.1",
            bg=PANEL_BG,
            fg=ACCENT,
            font=("Segoe UI", 18, "bold"),
        ).pack(pady=15)

        # ---- AI section ----
        ai_frame = tk.LabelFrame(
            panel, text="🧠 AI Meme Generator",
            bg=PANEL_BG, fg=ACCENT_HI,
            font=("Segoe UI", 13, "bold"),
            labelanchor="n",
        )
        ai_frame.pack(fill=tk.X, padx=12, pady=8)

        tk.Label(ai_frame, text="Describe your meme idea",
                 bg=PANEL_BG, fg=WHITE, font=("Segoe UI", 10)
                 ).pack(anchor="w", padx=8, pady=(8, 2))

        tk.Entry(
            ai_frame,
            textvariable=self.ai_prompt,
            bg=ENTRY_BG, fg=WHITE,
            insertbackground=WHITE,
            relief=tk.FLAT,
            font=("Segoe UI", 11),
        ).pack(fill=tk.X, padx=8, pady=4)

        self._btn(ai_frame, "✨ Generate AI Image",
                  self.generate_ai_meme, bold=True, accent=True
                  ).pack(fill=tk.X, padx=8, pady=8)

        tk.Label(ai_frame, text="→ Powered by Flux (cloud) • No downloads",
                 bg=PANEL_BG, fg=MUTED, font=("Segoe UI", 8)).pack()

        # ---- Classic templates ----
        tk.Label(panel, text="📌 Classic Templates",
                 bg=PANEL_BG, fg=ACCENT, font=("Segoe UI", 13, "bold")
                 ).pack(anchor="w", padx=12, pady=(15, 5))

        self.selected_template = tk.StringVar(value=list(self.templates.keys())[0])

        om = tk.OptionMenu(panel, self.selected_template, *self.templates.keys())
        om.configure(
            bg=BTN_BG, fg=BTN_FG, activebackground="#1a1a1a",
            activeforeground=BTN_FG, relief=tk.FLAT, bd=0,
            highlightthickness=1, highlightbackground=BTN_FG,
            font=("Segoe UI", 10),
        )
        om["menu"].configure(bg=BTN_BG, fg=BTN_FG,
                             activebackground="#1a1a1a", activeforeground=BTN_FG)
        om.pack(fill=tk.X, padx=12, pady=5)

        self._btn(panel, "Load Classic Meme", self.load_template
                  ).pack(fill=tk.X, padx=12, pady=5)

        # ---- Text controls ----
        tk.Label(panel, text="Top Text", bg=PANEL_BG, fg=WHITE).pack(anchor="w", padx=12)
        tk.Entry(
            panel, textvariable=self.top_text,
            bg=ENTRY_BG, fg=WHITE, insertbackground=WHITE,
            relief=tk.FLAT, font=("Segoe UI", 11),
        ).pack(fill=tk.X, padx=12, pady=2)
        self.top_text.trace_add("write", lambda *a: self.render())

        tk.Label(panel, text="Bottom Text", bg=PANEL_BG, fg=WHITE).pack(anchor="w", padx=12)
        tk.Entry(
            panel, textvariable=self.bottom_text,
            bg=ENTRY_BG, fg=WHITE, insertbackground=WHITE,
            relief=tk.FLAT, font=("Segoe UI", 11),
        ).pack(fill=tk.X, padx=12, pady=2)
        self.bottom_text.trace_add("write", lambda *a: self.render())

        self._btn(panel, "Text Color", self.pick_color).pack(fill=tk.X, padx=12, pady=8)

        self.slider = tk.Scale(
            panel, from_=20, to=120, orient=tk.HORIZONTAL,
            bg=PANEL_BG, fg=ACCENT, troughcolor=ENTRY_BG,
            highlightthickness=0, activebackground=ACCENT,
            command=self.update_size,
        )
        self.slider.set(48)
        self.slider.pack(fill=tk.X, padx=12)

        self._btn(panel, "Render Preview", self.render).pack(fill=tk.X, padx=12, pady=8)
        self._btn(panel, "Export PNG", self.export).pack(fill=tk.X, padx=12)

    # ================= FONT =================
    def get_font(self):
        candidates = [
            "Impact", "Arial Bold", "Helvetica-Bold",
            "arialbd.ttf", "Impact.ttf",
            "DejaVuSans-Bold.ttf", "Arial-Bold.ttf",
        ]
        for name in candidates:
            try:
                return ImageFont.truetype(name, self.font_size)
            except Exception:
                continue
        return ImageFont.load_default()

    # ================= AI =================
    def generate_ai_meme(self):
        prompt = self.ai_prompt.get().strip()
        if not prompt:
            messagebox.showwarning("Empty Prompt", "Describe your meme idea first! 🐱")
            return

        meme_prompt = (
            f"{prompt}, funny internet meme style, bold white text space at top and bottom, "
            f"high contrast, viral, classic meme format, dramatic lighting, meme aesthetic"
        )

        try:
            encoded = quote(meme_prompt)
            url = (
                f"https://image.pollinations.ai/prompt?prompt={encoded}"
                f"&width=1024&height=1024&model=flux&seed={random.randint(1, 999999)}"
            )
            response = requests.get(url, timeout=45)
            response.raise_for_status()
            self.image = Image.open(BytesIO(response.content)).convert("RGB")
            self.render()
            messagebox.showinfo(
                "AI Magic Complete 🐱",
                "Image generated!\nNow type your top/bottom text and drag them around.",
            )
        except Exception as e:
            messagebox.showerror("AI Generation Failed",
                                 f"Could not generate image:\n{e}")

    # ================= CLASSIC =================
    def load_template(self):
        try:
            url = self.templates[self.selected_template.get()]
            response = requests.get(url, timeout=12)
            response.raise_for_status()
            self.image = Image.open(BytesIO(response.content)).convert("RGB")
            self.render()
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load meme:\n{e}")

    # ================= COLOR =================
    def pick_color(self):
        c = colorchooser.askcolor(title="Choose Text Color")[1]
        if c:
            self.text_color = c
            self.render()

    # ================= SIZE =================
    def update_size(self, val):
        try:
            self.font_size = int(float(val))
        except (TypeError, ValueError):
            return
        self.render()

    # ================= RENDER =================
    def render(self):
        if not self.image:
            self.canvas.delete("all")
            self.canvas.update_idletasks()
            cw = self.canvas.winfo_width() or 800
            ch = self.canvas.winfo_height() or 600
            self.canvas.create_text(
                cw // 2, ch // 2,
                text="Load a template or\nGenerate with AI 🐱",
                fill="#444",
                font=("Arial", 16),
                justify="center",
            )
            return

        img = self.image.copy()
        draw = ImageDraw.Draw(img)
        font = self.get_font()
        w, h = img.size

        def draw_text(text, cx_frac, y_frac):
            text = text.upper().strip()
            if not text:
                return
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            x = int(w * cx_frac) - tw // 2
            y = int(h * y_frac)
            for dx in range(-5, 6):
                for dy in range(-5, 6):
                    if dx == 0 and dy == 0:
                        continue
                    draw.text((x + dx, y + dy), text, fill="black", font=font)
            draw.text((x, y), text, fill=self.text_color, font=font)

        draw_text(self.top_text.get(), self.top_pos[0], self.top_pos[1])
        draw_text(self.bottom_text.get(), self.bottom_pos[0], self.bottom_pos[1])

        self.preview_img = img

        show = img.copy()
        show.thumbnail((950, 680), Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(show)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

    # ================= EXPORT =================
    def export(self):
        if not self.preview_img:
            messagebox.showwarning("Nothing to export", "Generate or load a meme first 🐱")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
        )
        if path:
            self.preview_img.save(path)
            messagebox.showinfo("Saved!", "Meme exported successfully 🐱")

    # ================= DRAG =================
    def start_drag(self, event):
        if not self.tk_img:
            return
        dw = self.tk_img.width()
        dh = self.tk_img.height()
        tx, ty = self.top_pos[0] * dw, self.top_pos[1] * dh
        bx, by = self.bottom_pos[0] * dw, self.bottom_pos[1] * dh
        dt = ((tx - event.x) ** 2 + (ty - event.y) ** 2) ** 0.5
        db = ((bx - event.x) ** 2 + (by - event.y) ** 2) ** 0.5
        if dt < db and dt < 110:
            self.dragging = "top"
        elif db < 110:
            self.dragging = "bottom"
        else:
            self.dragging = None

    def drag(self, event):
        if self.dragging is None or not self.tk_img:
            return
        dw = self.tk_img.width()
        dh = self.tk_img.height()
        nx = max(0.08, min(0.92, event.x / dw))
        ny = max(0.08, min(0.92, event.y / dh))
        if self.dragging == "top":
            self.top_pos = [nx, ny]
        else:
            self.bottom_pos = [nx, ny]
        self.render()

    def stop_drag(self, event):
        self.dragging = None


if __name__ == "__main__":
    root = tk.Tk()
    app = CatMemeGen(root)
    root.mainloop()
