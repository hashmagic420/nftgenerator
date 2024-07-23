import tkinter as tk
from tkinter.colorchooser import askcolor
from tkinter import simpledialog

class PixelArtEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Neuromorphic Pixel Art Editor")
        self.root.configure(bg='#b04e0f')

        self.canvas_size = (34, 23)
        self.current_color = "#000000"
        self.current_tool = "draw"
        self.custom_stamps = {}

        self.setup_ui()

    def setup_ui(self):
        toolbar_frame = tk.Frame(self.root, bg='#333')
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)

        tools = ["New", "Draw", "Erase", "Fill", "Color Picker", "Stamp", "Create"]
        for tool in tools:
            button = tk.Button(toolbar_frame, text=tool, bg='#555', fg='#f0f0f0', command=lambda t=tool: self.select_tool(t))
            button.pack(side=tk.LEFT, padx=5, pady=5)

        self.pixel_grid = tk.Frame(self.root, bg='#333')
        self.pixel_grid.pack(pady=20)
        self.create_grid()

        properties_frame = tk.Frame(self.root, bg='#333')
        properties_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)

        self.color_label = tk.Label(properties_frame, text="Color: ", bg='#333', fg='#f0f0f0')
        self.color_label.pack(side=tk.LEFT, padx=5)
        self.color_display = tk.Label(properties_frame, bg=self.current_color, width=2, height=1)
        self.color_display.pack(side=tk.LEFT, padx=5)

        self.canvas_size_label = tk.Label(properties_frame, text="Canvas Size: 34x23", bg='#333', fg='#f0f0f0', cursor="hand2")
        self.canvas_size_label.pack(side=tk.LEFT, padx=5)
        self.canvas_size_label.bind("<Button-1>", self.change_canvas_size)

        export_button = tk.Button(properties_frame, text="Export", bg='#555', fg='#f0f0f0', command=self.export_art)
        export_button.pack(side=tk.RIGHT, padx=5)

        color_picker_frame = tk.Frame(properties_frame, bg='#333')
        color_picker_frame.pack(side=tk.RIGHT, padx=5)

        colors = [
            '#000000', '#FFFFFF', '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF',
            '#800000', '#808000', '#008000', '#800080', '#808080', '#C0C0C0', '#FFA500', '#A52A2A',
            '#8B0000', '#A9A9A9', '#2F4F4F', '#00CED1', '#ADFF2F', '#DAA520', '#F0E68C', '#DDA0DD',
            '#F5DEB3', '#D2691E', '#8A2BE2', '#5F9EA0', '#7FFF00', '#D2691E', '#FF7F50', '#6495ED',
            '#DC143C', '#00FFFF', '#00008B', '#008B8B', '#B8860B', '#A9A9A9', '#006400', '#BDB76B'
        ]

        for color in colors:
            color_button = tk.Button(color_picker_frame, bg=color, width=2, height=1, command=lambda c=color: self.select_color(c))
            color_button.pack(side=tk.LEFT, padx=2)

    def create_grid(self):
        for row in range(self.canvas_size[1]):
            for col in range(self.canvas_size[0]):
                pixel = tk.Label(self.pixel_grid, bg='#888', width=2, height=1, borderwidth=1, relief="raised", cursor="hand2")
                pixel.grid(row=row, column=col, padx=1, pady=1)
                pixel.bind("<Button-1>", self.handle_pixel_click)

    def handle_pixel_click(self, event):
        pixel = event.widget
        if self.current_tool == "draw":
            pixel.configure(bg=self.current_color)
        elif self.current_tool == "erase":
            pixel.configure(bg='#888')

    def select_tool(self, tool):
        self.current_tool = tool.lower()
        if self.current_tool == "color picker":
            self.pick_color()

    def select_color(self, color):
        self.current_color = color
        self.color_display.configure(bg=self.current_color)

    def pick_color(self):
        color_code = askcolor(title="Choose color")[1]
        if color_code:
            self.select_color(color_code)

    def change_canvas_size(self, event):
        new_width = simpledialog.askinteger("Input", "Enter new width:", minvalue=1, maxvalue=100, initialvalue=self.canvas_size[0])
        new_height = simpledialog.askinteger("Input", "Enter new height:", minvalue=1, maxvalue=100, initialvalue=self.canvas_size[1])

        if new_width and new_height:
            self.canvas_size = (new_width, new_height)
            self.canvas_size_label.configure(text=f"Canvas Size: {new_width}x{new_height}")
            for widget in self.pixel_grid.winfo_children():
                widget.destroy()
            self.create_grid()

    def export_art(self):
        export_window = tk.Toplevel(self.root)
        export_window.title("Export Art")
        canvas = tk.Canvas(export_window, width=self.canvas_size[0]*22, height=self.canvas_size[1]*22)
        canvas.pack()

        for row in range(self.canvas_size[1]):
            for col in range(self.canvas_size[0]):
                pixel = self.pixel_grid.grid_slaves(row=row, column=col)[0]
                color = pixel.cget("bg")
                canvas.create_rectangle(col*22, row*22, (col+1)*22, (row+1)*22, fill=color, outline=color)

        export_button = tk.Button(export_window, text="Save as PNG", command=lambda: self.save_canvas_as_png(canvas))
        export_button.pack(pady=10)

    def save_canvas_as_png(self, canvas):
        canvas.postscript(file="pixel_art.eps")
        from PIL import Image
        img = Image.open("pixel_art.eps")
        img.save("pixel_art.png")
        img.show()

if __name__ == "__main__":
    root = tk.Tk()
    editor = PixelArtEditor(root)
    root.mainloop()
