import os, image_system
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps, ImageTk

# ── Folder selection ───────────────────────────────────────────────────────────
root = Tk()
root.withdraw()
folder_path = filedialog.askdirectory(title="Select folder with JPG images")
output_path = filedialog.askdirectory(title="Select output folder")
root.destroy()

if not folder_path or not output_path:
    raise SystemExit("No folder selected.")

jpg_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(".jpg")])

portrait_files, landscape_files = [], []
for f in jpg_files:
    with Image.open(os.path.join(folder_path, f)) as img:
        w, h = img.size
        (portrait_files if h > w else landscape_files).append(f)


# ── Preview helpers ────────────────────────────────────────────────────────────
PREVIEW_W, PREVIEW_H = 324, 405   # half of 1080x1350

def simulate_portrait_2pic(path1, path2):
    im1 = Image.open(path1)
    im2 = Image.open(path2)
    slot = (500, 680)
    im1 = ImageOps.cover(im1, slot)
    im2 = ImageOps.cover(im2, slot)
    border_im = Image.new("RGB", (505, 685), (255, 255, 255))
    border_im.paste(im2, (5, 5))
    canvas = Image.new("RGB", (920, 1150), (255, 255, 255))
    canvas.paste(im1, (0, 0))
    canvas.paste(border_im, (920 - border_im.width, 1150 - border_im.height))
    final = Image.new("RGB", (1080, 1350), (255, 255, 255))
    final.paste(canvas, ((1080 - canvas.width) // 2, (1350 - canvas.height) // 2))
    return final

def simulate_portrait_1pic(path1):
    im1 = Image.open(path1)
    im1 = ImageOps.contain(im1, (1020, 1200))
    final = Image.new("RGB", (1080, 1350), (255, 255, 255))
    final.paste(im1, ((1080 - im1.width) // 2, (1350 - im1.height) // 2))
    return final

def simulate_landscape_2pic(path1, path2):
    im1 = Image.open(path1)
    im2 = Image.open(path2)
    if im1.size != im2.size:
        if im1.size[1] < im2.size[1] or im1.size[0] < im2.size[0]:
            im2 = ImageOps.cover(im2, im1.size)
        else:
            im1 = ImageOps.cover(im1, im2.size)
    h = im1.size[1] + im2.size[1]
    pad = int(0.05 * 0.5 * h)
    w = max(im1.size[0], im2.size[0])
    merged = Image.new("RGB", (w, h + pad), (255, 255, 255))
    merged.paste(im2, (0, 0))
    merged.paste(im1, (0, im2.size[1] + pad))
    merged = ImageOps.cover(merged, (920, 1050))
    final = Image.new("RGB", (1080, 1350), (255, 255, 255))
    final.paste(merged, ((1080 - merged.width) // 2, (1350 - merged.height) // 2))
    return final

def simulate_landscape_1pic(path1):
    im1 = Image.open(path1)
    im1 = ImageOps.contain(im1, (920, 1050))
    final = Image.new("RGB", (1080, 1350), (255, 255, 255))
    final.paste(im1, ((1080 - im1.width) // 2, (1350 - im1.height) // 2))
    return final

def make_preview_tk(pil_img):
    thumb = pil_img.copy()
    thumb.thumbnail((PREVIEW_W, PREVIEW_H), Image.LANCZOS)
    return ImageTk.PhotoImage(thumb)

def thumb_from_path(path, max_w, max_h):
    img = Image.open(path)
    img.thumbnail((max_w, max_h), Image.LANCZOS)
    return ImageTk.PhotoImage(img)


# ── Assignment UI ──────────────────────────────────────────────────────────────
class AssignmentApp:
    def __init__(self, root, files, orientation, folder):
        self.root = root
        self.files = files
        self.orientation = orientation
        self.folder = folder
        self.assignments = []
        self.unassigned = list(files)
        self._tk_refs = []   # keep PhotoImage refs alive

        root.title(f"Assign {orientation.capitalize()} Images")
        root.geometry("1100x620")
        root.resizable(True, True)

        # ── left: pool ────────────────────────────────────────────────────────
        left = Frame(root, width=220)
        left.pack(side=LEFT, fill=Y, padx=(10, 0), pady=10)
        left.pack_propagate(False)

        Label(left, text="Unassigned images", font=("", 11, "bold")).pack(anchor=W)
        pool_frame = Frame(left)
        pool_frame.pack(fill=BOTH, expand=True, pady=(4, 0))

        pool_scroll = Scrollbar(pool_frame)
        pool_scroll.pack(side=RIGHT, fill=Y)
        self.pool_box = Listbox(pool_frame, selectmode=EXTENDED,
                                yscrollcommand=pool_scroll.set, width=26)
        self.pool_box.pack(side=LEFT, fill=BOTH, expand=True)
        pool_scroll.config(command=self.pool_box.yview)
        self.pool_box.bind("<<ListboxSelect>>", self._on_pool_select)

        for f in self.unassigned:
            self.pool_box.insert(END, f)

        # ── middle: buttons ───────────────────────────────────────────────────
        mid = Frame(root, width=110)
        mid.pack(side=LEFT, fill=Y, padx=8, pady=10)
        mid.pack_propagate(False)

        Label(mid, text="").pack(pady=12)
        Button(mid, text="Solo →", width=10, command=self.assign_solo).pack(pady=4)
        Button(mid, text="Pair →", width=10, command=self.assign_pair).pack(pady=4)
        Button(mid, text="← Remove", width=10, command=self.remove_assignment).pack(pady=4)
        Button(mid, text="✔ Done", width=10, bg="#4CAF50", fg="white",
               command=self.finish).pack(pady=20)

        # ── right: assignments ────────────────────────────────────────────────
        right = Frame(root, width=240)
        right.pack(side=LEFT, fill=Y, padx=(0, 8), pady=10)
        right.pack_propagate(False)

        Label(right, text="Assignments", font=("", 11, "bold")).pack(anchor=W)
        assign_frame = Frame(right)
        assign_frame.pack(fill=BOTH, expand=True, pady=(4, 0))

        assign_scroll = Scrollbar(assign_frame)
        assign_scroll.pack(side=RIGHT, fill=Y)
        self.assign_box = Listbox(assign_frame, yscrollcommand=assign_scroll.set, width=30)
        self.assign_box.pack(side=LEFT, fill=BOTH, expand=True)
        assign_scroll.config(command=self.assign_box.yview)
        self.assign_box.bind("<<ListboxSelect>>", self._on_assign_select)

        # ── far right: preview ────────────────────────────────────────────────
        prev_outer = Frame(root)
        prev_outer.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10), pady=10)

        Label(prev_outer, text="Output preview", font=("", 11, "bold")).pack(anchor=W)

        # thumbnail strip (pool selection)
        self.strip_frame = Frame(prev_outer, height=120)
        self.strip_frame.pack(fill=X, pady=(4, 0))
        self.strip_frame.pack_propagate(False)
        self.strip_labels = []

        # simulated output
        self.preview_label = Label(prev_outer, text="Select an assignment\nto preview output",
                                   bg="#e8e8e8", width=PREVIEW_W, height=20,
                                   relief=FLAT)
        self.preview_label.pack(fill=BOTH, expand=True, pady=(8, 0))

    # ── pool thumbnail strip ───────────────────────────────────────────────────
    def _on_pool_select(self, event):
        for lbl in self.strip_labels:
            lbl.destroy()
        self.strip_labels.clear()

        sel = self._selected_pool()
        for fname in sel[:2]:
            path = os.path.join(self.folder, fname)
            try:
                tk_img = thumb_from_path(path, 110, 110)
                self._tk_refs.append(tk_img)
                lbl = Label(self.strip_frame, image=tk_img, text=fname,
                            compound=TOP, font=("", 8),
                            wraplength=115, justify=CENTER)
                lbl.pack(side=LEFT, padx=6, pady=4)
                self.strip_labels.append(lbl)
            except Exception:
                pass

    # ── assignment preview ─────────────────────────────────────────────────────
    def _on_assign_select(self, event):
        idx = self.assign_box.curselection()
        if not idx:
            return
        entry = self.assignments[idx[0]]
        self._show_preview(entry)

    def _show_preview(self, entry):
        try:
            p1 = os.path.join(self.folder, entry[1])
            if entry[0] == "solo":
                if self.orientation == "portrait":
                    result = simulate_portrait_1pic(p1)
                else:
                    result = simulate_landscape_1pic(p1)
            else:
                p2 = os.path.join(self.folder, entry[2])
                if self.orientation == "portrait":
                    result = simulate_portrait_2pic(p1, p2)
                else:
                    result = simulate_landscape_2pic(p1, p2)

            tk_img = make_preview_tk(result)
            self._tk_refs.append(tk_img)
            self.preview_label.config(image=tk_img, text="", bg="white")
            self.preview_label.image = tk_img
        except Exception as e:
            self.preview_label.config(image="", text=f"Preview error:\n{e}", bg="#fee")

    # ── pool helpers ───────────────────────────────────────────────────────────
    def _selected_pool(self):
        return [self.pool_box.get(i) for i in self.pool_box.curselection()]

    def assign_solo(self):
        sel = self._selected_pool()
        if len(sel) != 1:
            messagebox.showwarning("Solo", "Select exactly 1 image for solo.")
            return
        entry = ("solo", sel[0])
        self.assignments.append(entry)
        self.unassigned.remove(sel[0])
        self._refresh()
        self._show_preview(entry)

    def assign_pair(self):
        sel = self._selected_pool()
        if len(sel) != 2:
            messagebox.showwarning("Pair", "Select exactly 2 images to pair.")
            return
        entry = ("pair", sel[0], sel[1])
        self.assignments.append(entry)
        for f in sel:
            self.unassigned.remove(f)
        self._refresh()
        self._show_preview(entry)

    def remove_assignment(self):
        idx = self.assign_box.curselection()
        if not idx:
            return
        removed = self.assignments.pop(idx[0])
        for f in removed[1:]:
            self.unassigned.append(f)
        self.unassigned.sort()
        self.preview_label.config(image="", text="Select an assignment\nto preview output",
                                  bg="#e8e8e8")
        self._refresh()

    def _refresh(self):
        self.pool_box.delete(0, END)
        for f in self.unassigned:
            self.pool_box.insert(END, f)
        self.assign_box.delete(0, END)
        for a in self.assignments:
            if a[0] == "solo":
                self.assign_box.insert(END, f"[SOLO]  {a[1]}")
            else:
                self.assign_box.insert(END, f"[PAIR]  {a[1]}  +  {a[2]}")

    def finish(self):
        remaining = list(self.unassigned)
        for i in range(0, len(remaining), 2):
            f1 = remaining[i]
            f2 = remaining[i + 1] if i + 1 < len(remaining) else None
            if f2:
                self.assignments.append(("pair", f1, f2))
            else:
                self.assignments.append(("solo", f1))
        self.root.quit()
        self.root.destroy()


def run_assignment_ui(files, orientation):
    if not files:
        return []
    win = Tk()
    app = AssignmentApp(win, files, orientation, folder_path)
    win.mainloop()
    return app.assignments


# ── Run UI ─────────────────────────────────────────────────────────────────────
portrait_assignments  = run_assignment_ui(portrait_files,  "portrait")
landscape_assignments = run_assignment_ui(landscape_files, "landscape")


# ── Process ────────────────────────────────────────────────────────────────────
def process(assignments, orientation, folder, output):
    process_fn = (image_system.portrait.process_portrait
                  if orientation == "portrait"
                  else image_system.landscape.process_landscape)
    for i, entry in enumerate(assignments, 1):
        out = os.path.join(output, f"{orientation}_{i}.jpg")
        f1 = os.path.join(folder, entry[1])
        f2 = os.path.join(folder, entry[2]) if entry[0] == "pair" else None
        process_fn(f1, f2, out)

process(portrait_assignments, "portrait", folder_path, output_path)
process(landscape_assignments, "landscape", folder_path, output_path)
