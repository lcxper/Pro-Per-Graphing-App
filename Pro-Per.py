import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
import sympy as sp
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import rcParams
import webbrowser


class ModernFunctionVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pro-Per Graphing App")
        self.root.geometry("1100x800")
        self.root.minsize(900, 700)

        self.bg_color = "#2b2b2b"
        self.card_color = "#363636"
        self.accent_color = "#4fc3f7"
        self.secondary_accent = "#81c784"
        self.text_color = "#e0e0e0"
        self.error_color = "#ff5252"

        self.ui_font = ("Roboto", 10)
        self.title_font = ("Roboto Medium", 12)
        self.code_font = ("Fira Code", 10)
        self.button_font = ("Roboto Medium", 9)

        self.icons = {}

        self.root.configure(bg=self.bg_color)

        plt.style.use('dark_background')
        rcParams['axes.edgecolor'] = '#4f4f4f'
        rcParams['axes.titlecolor'] = self.text_color
        rcParams['axes.labelcolor'] = self.text_color
        rcParams['xtick.color'] = '#8d8d8d'
        rcParams['ytick.color'] = '#8d8d8d'
        rcParams['grid.color'] = '#3a3a3a'

        self.create_menu()
        self.create_widgets()
        self.create_toolbar()

    def create_menu(self):
        menubar = tk.Menu(self.root, bg=self.card_color, fg=self.text_color,
                          activebackground="#454545", activeforeground=self.text_color,
                          bd=0, font=self.ui_font)

        file_menu = tk.Menu(menubar, tearoff=0, bg=self.card_color, fg=self.text_color,
                            activebackground="#454545", activeforeground=self.accent_color)
        file_menu.add_command(label="New", command=self.clear_plot, accelerator="Ctrl+N")
        file_menu.add_command(label="Save Plot", command=self.save_plot, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Preferences", command=self.show_preferences)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")
        menubar.add_cascade(label="File", menu=file_menu)


        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.card_color, fg=self.text_color,
                            activebackground="#454545", activeforeground=self.accent_color)
        edit_menu.add_command(label="Copy Plot", command=self.copy_plot, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste Function", command=self.paste_function, accelerator="Ctrl+V")
        menubar.add_cascade(label="Edit", menu=edit_menu)


        view_menu = tk.Menu(menubar, tearoff=0, bg=self.card_color, fg=self.text_color,
                            activebackground="#454545", activeforeground=self.accent_color)
        view_menu.add_command(label="Zoom In", command=lambda: self.adjust_font_size(1))
        view_menu.add_command(label="Zoom Out", command=lambda: self.adjust_font_size(-1))
        menubar.add_cascade(label="View", menu=view_menu)


        help_menu = tk.Menu(menubar, tearoff=0, bg=self.card_color, fg=self.text_color,
                            activebackground="#454545", activeforeground=self.accent_color)
        help_menu.add_command(label="Documentation", command=self.open_docs)
        help_menu.add_command(label="Examples", command=self.show_examples)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)


        self.root.bind("<Control-n>", lambda e: self.clear_plot())
        self.root.bind("<Control-s>", lambda e: self.save_plot())
        self.root.bind("<Control-c>", lambda e: self.copy_plot())
        self.root.bind("<Control-plus>", lambda e: self.adjust_font_size(1))
        self.root.bind("<Control-minus>", lambda e: self.adjust_font_size(-1))

    def create_toolbar(self):
        toolbar = ttk.Frame(self.root, height=40)
        toolbar.pack(fill=tk.X, padx=5, pady=(5, 0))


        buttons = [
            ('Plot', self.plot_function),
            ('Save', self.save_plot),
            ('Clear', self.clear_plot),
            ('Help', self.show_help)
        ]

        for text, cmd in buttons:
            btn = ttk.Button(toolbar, text=text, command=cmd)
            btn.pack(side=tk.LEFT, padx=2)


        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side=tk.RIGHT, padx=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.insert(0, "sin(x), cos(x), etc...")
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.delete(0, tk.END))

    def create_widgets(self):

        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        # Left panel - Controls
        control_frame = ttk.Frame(main_container, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        control_frame.pack_propagate(False)

        # Function input card
        input_card = ttk.LabelFrame(control_frame, text="Function Input", padding=10)
        input_card.pack(fill=tk.X, pady=(0, 10))

        input_row = ttk.Frame(input_card)
        input_row.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(input_row, text="f(x) =").pack(side=tk.LEFT)
        self.function_entry = ttk.Entry(input_row, font=self.code_font)
        self.function_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.function_entry.insert(0, "x**2 * sin(x)")

        # Quick function buttons
        button_grid = ttk.Frame(input_card)
        button_grid.pack(fill=tk.X, pady=(5, 0))

        buttons = [
            ('x²', 'x**2'), ('√x', 'sqrt(x)'), ('eˣ', 'exp(x)'), ('ln(x)', 'log(x)'),
            ('sin', 'sin(x)'), ('cos', 'cos(x)'), ('tan', 'tan(x)'), ('π', 'pi'),
            ('+', '+'), ('-', '-'), ('*', '*'), ('/', '/'),
            ('(', '('), (')', ')'), ('^', '**'), ('abs', 'abs(x)')
        ]

        for i, (text, val) in enumerate(buttons):
            btn = ttk.Button(button_grid, text=text, width=3,
                             command=lambda v=val: self.insert_at_cursor(v))
            btn.grid(row=i // 4, column=i % 4, padx=2, pady=2, sticky='nsew')
            button_grid.columnconfigure(i % 4, weight=1)


        range_card = ttk.LabelFrame(control_frame, text="Plot Range", padding=10)
        range_card.pack(fill=tk.X, pady=(0, 10))

        self.xmin_entry = self.create_slider_entry(range_card, "X Min:", "-5")
        self.xmax_entry = self.create_slider_entry(range_card, "X Max:", "5")

        points_frame = ttk.Frame(range_card)
        points_frame.pack(fill=tk.X, pady=2)

        ttk.Label(points_frame, text="Points:", width=8).pack(side=tk.LEFT)
        self.points_entry = ttk.Entry(points_frame, width=10, font=self.code_font)
        self.points_entry.pack(side=tk.LEFT, padx=5)
        self.points_entry.insert(0, "500")


        options_card = ttk.LabelFrame(control_frame, text="Visualization", padding=10)
        options_card.pack(fill=tk.X)

        self.show_derivative = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_card, text="First Derivative", variable=self.show_derivative).pack(anchor=tk.W, pady=2)

        self.show_second_derivative = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_card, text="Second Derivative", variable=self.show_second_derivative).pack(anchor=tk.W,
                                                                                                           pady=2)

        self.show_integral = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_card, text="Integral", variable=self.show_integral).pack(anchor=tk.W, pady=2)

        self.show_symbolic = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_card, text="Symbolic Results", variable=self.show_symbolic).pack(anchor=tk.W, pady=2)


        plot_info_frame = ttk.Frame(main_container)
        plot_info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)


        plot_card = ttk.LabelFrame(plot_info_frame, text="Function Visualization", padding=5)
        plot_card.pack(fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.fig.patch.set_facecolor(self.card_color)
        self.ax.set_facecolor(self.card_color)

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_card)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


        info_card = ttk.LabelFrame(plot_info_frame, text="Analysis Results", padding=5, height=150)
        info_card.pack(fill=tk.X, pady=(10, 0))
        info_card.pack_propagate(False)

        self.info_text = tk.Text(info_card, bg=self.card_color, fg=self.text_color,
                                 font=self.code_font, wrap=tk.WORD, padx=5, pady=5,
                                 insertbackground=self.accent_color, selectbackground=self.accent_color,
                                 borderwidth=0, highlightthickness=0)

        scrollbar = ttk.Scrollbar(info_card, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.pack(fill=tk.BOTH, expand=True)


        self.status_bar = ttk.Frame(self.root, height=25)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)

        ttk.Label(self.status_bar, text="Python + Matplotlib").pack(side=tk.RIGHT, padx=5)


        self.info_text.tag_configure("function", foreground="#4fc3f7")
        self.info_text.tag_configure("derivative", foreground="#81c784")
        self.info_text.tag_configure("second_derivative", foreground="#ffb74d")
        self.info_text.tag_configure("integral", foreground="#ba68c8")
        self.info_text.tag_configure("symbol", foreground="#e57373")

    def create_slider_entry(self, parent, label, default):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)

        ttk.Label(frame, text=label, width=8).pack(side=tk.LEFT)
        entry = ttk.Entry(frame, width=10, font=self.code_font)
        entry.pack(side=tk.LEFT, padx=5)
        entry.insert(0, default)

        scale = ttk.Scale(frame, from_=-10, to=10, orient=tk.HORIZONTAL, length=100)
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scale.set(float(default))

        scale['command'] = lambda v: entry.delete(0, tk.END) or entry.insert(0, f"{float(v):.1f}")
        entry.bind('<Return>', lambda e: scale.set(float(entry.get())))

        return entry

    def insert_at_cursor(self, text):
        self.function_entry.insert(tk.INSERT, text)
        self.function_entry.focus()

    def finite_difference(self, f, x, h=1e-5):
        """Compute the derivative using central finite differences."""
        return (f(x + h) - f(x - h)) / (2 * h)

    def second_derivative(self, f, x, h=1e-5):
        """Compute the second derivative using finite differences."""
        return (f(x + h) - 2 * f(x) + f(x - h)) / (h ** 2)

    def parse_function(self, func_str):
        """Parse the function string into a callable function."""
        x = sp.symbols('x')
        try:
            expr = sp.sympify(func_str)
            f = sp.lambdify(x, expr, modules=['numpy', {'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                                                        'exp': np.exp, 'log': np.log, 'sqrt': np.sqrt,
                                                        'pi': np.pi, 'abs': np.abs}])
            return f, expr
        except (sp.SympifyError, SyntaxError) as e:
            messagebox.showerror("Error", f"Invalid function expression: {e}")
            self.status_label.config(text=f"Error: Invalid function expression", foreground=self.error_color)
            return None, None

    def compute_derivative(self, f, x_values):
        """Compute the numerical derivative of the function."""
        try:
            dfdx = [self.finite_difference(f, x) for x in x_values]
            return np.array(dfdx)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compute derivative: {e}")
            self.status_label.config(text=f"Error computing derivative", foreground=self.error_color)
            return None

    def compute_second_derivative(self, f, x_values):
        """Compute the second derivative of the function."""
        try:
            d2fdx2 = [self.second_derivative(f, x) for x in x_values]
            return np.array(d2fdx2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compute second derivative: {e}")
            self.status_label.config(text=f"Error computing second derivative", foreground=self.error_color)
            return None

    def compute_integral(self, f, x_values):
        """Compute the numerical integral of the function."""
        try:
            integral_values = []
            for x in x_values:
                integral, _ = quad(f, float(x_values[0]), x)
                integral_values.append(integral)
            return np.array(integral_values)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compute integral: {e}")
            self.status_label.config(text=f"Error computing integral", foreground=self.error_color)
            return None

    def plot_function(self):
        """Plot the function with selected options."""
        func_str = self.function_entry.get()
        try:
            xmin = float(self.xmin_entry.get())
            xmax = float(self.xmax_entry.get())
            points = int(self.points_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid range or points value")
            self.status_label.config(text="Error: Invalid range or points value", foreground=self.error_color)
            return

        f, expr = self.parse_function(func_str)
        if f is None:
            return

        x_values = np.linspace(xmin, xmax, points)
        y_values = f(x_values)

        self.ax.clear()


        line, = self.ax.plot(x_values, y_values, label=f'f(x) = {expr}',
                             linewidth=2.5, color=self.accent_color, zorder=3)

        info_text = [f"⎧ Original function: f(x) = {expr}"]


        if self.show_derivative.get():
            dfdx_values = self.compute_derivative(f, x_values)
            if dfdx_values is not None:
                line, = self.ax.plot(x_values, dfdx_values, '--',
                                     label="f'(x) (1st derivative)",
                                     linewidth=2, color=self.secondary_accent, zorder=2)

                if self.show_symbolic.get():
                    x_sym = sp.symbols('x')
                    dfdx_expr = sp.diff(expr, x_sym)
                    info_text.append(f"⎪ First derivative: f'(x) = {dfdx_expr}")


        if self.show_second_derivative.get():
            d2fdx2_values = self.compute_second_derivative(f, x_values)
            if d2fdx2_values is not None:
                line, = self.ax.plot(x_values, d2fdx2_values, ':',
                                     label="f''(x) (2nd derivative)",
                                     linewidth=2, color="#ffb74d", zorder=1)

                if self.show_symbolic.get():
                    x_sym = sp.symbols('x')
                    d2fdx2_expr = sp.diff(expr, x_sym, 2)
                    info_text.append(f"⎪ Second derivative: f''(x) = {d2fdx2_expr}")


        if self.show_integral.get():
            integral_values = self.compute_integral(f, x_values)
            if integral_values is not None:
                line, = self.ax.plot(x_values, integral_values, '-.',
                                     label="∫f(x)dx (integral)",
                                     linewidth=2, color="#ba68c8", zorder=2)

                if self.show_symbolic.get():
                    x_sym = sp.symbols('x')
                    integral_expr = sp.integrate(expr, x_sym)
                    info_text.append(f"⎪ Integral: ∫f(x)dx = {integral_expr} + C")

        info_text.append("⎩")


        self.ax.set_xlabel('x', fontsize=10)
        self.ax.set_ylabel('y', fontsize=10)
        self.ax.set_title('Function Analysis', fontsize=12, pad=20)
        self.ax.legend(loc='upper right', framealpha=0.2, facecolor=self.card_color)
        self.ax.grid(True, color='#3a3a3a', linestyle='--', alpha=0.5)


        self.ax.set_facecolor(self.card_color)
        self.fig.set_facecolor(self.bg_color)


        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "\n".join(info_text))


        self.highlight_text()


        self.canvas.draw()
        self.status_label.config(text="Plot generated successfully", foreground=self.secondary_accent)

    def highlight_text(self):
        """Apply syntax highlighting to the info text."""
        text = self.info_text.get(1.0, tk.END)


        for i, line in enumerate(text.split('\n')):
            if "Original function" in line:
                self.info_text.tag_add("function", f"{i + 1}.0", f"{i + 1}.end")
            elif "First derivative" in line:
                self.info_text.tag_add("derivative", f"{i + 1}.0", f"{i + 1}.end")
            elif "Second derivative" in line:
                self.info_text.tag_add("second_derivative", f"{i + 1}.0", f"{i + 1}.end")
            elif "Integral" in line:
                self.info_text.tag_add("integral", f"{i + 1}.0", f"{i + 1}.end")
            elif any(c in line for c in ['⎧', '⎪', '⎩']):
                self.info_text.tag_add("symbol", f"{i + 1}.0", f"{i + 1}.end")

    def save_plot(self):
        """Save the current plot to an image file."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"),
                           ("SVG files", "*.svg"), ("All files", "*.*")],
                title="Save Plot As"
            )
            if filename:
                self.fig.savefig(filename, dpi=300, facecolor=self.bg_color, edgecolor='none')
                self.status_label.config(text=f"Plot saved to {filename}", foreground=self.secondary_accent)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save plot: {e}")
            self.status_label.config(text="Error saving plot", foreground=self.error_color)

    def copy_plot(self):
        """Copy the plot to clipboard."""
        try:
            import io
            buf = io.BytesIO()
            self.fig.savefig(buf, format='png', dpi=100, facecolor=self.bg_color)
            buf.seek(0)


            try:
                from PIL import Image
                img = Image.open(buf)
                import pyperclip
                pyperclip.copy(img)
                self.status_label.config(text="Plot copied to clipboard", foreground=self.secondary_accent)
            except ImportError:
                self.root.clipboard_clear()
                self.root.clipboard_append(buf.getvalue())
                self.status_label.config(text="Plot copied to clipboard (as raw data)",
                                         foreground=self.secondary_accent)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy plot: {e}")
            self.status_label.config(text="Error copying plot", foreground=self.error_color)

    def paste_function(self):
        """Paste function from clipboard."""
        try:
            clipboard_text = self.root.clipboard_get()
            self.function_entry.delete(0, tk.END)
            self.function_entry.insert(0, clipboard_text)
            self.status_label.config(text="Function pasted from clipboard", foreground=self.secondary_accent)
        except tk.TclError:
            self.status_label.config(text="Clipboard doesn't contain text", foreground=self.error_color)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste: {e}")
            self.status_label.config(text="Error pasting function", foreground=self.error_color)

    def clear_plot(self):
        """Clear the current plot."""
        self.ax.clear()
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_title('Function Analysis')
        self.ax.grid(True, color='#3a3a3a', linestyle='--', alpha=0.5)
        self.ax.set_facecolor(self.card_color)
        self.fig.set_facecolor(self.bg_color)
        self.canvas.draw()
        self.info_text.delete(1.0, tk.END)
        self.status_label.config(text="Plot cleared", foreground=self.text_color)

    def show_help(self):
        """Show help information."""
        help_text = """Function Visualizer Pro - Help

1. Enter a function of x in the input field (e.g., "sin(x)*exp(-x/5)")
2. Set the plot range and number of points
3. Select visualization options
4. Click "Plot Function" to generate the graph

Features:
- First and second derivatives
- Integral calculation
- Symbolic math expressions
- Modern dark mode interface
- Syntax highlighting

Keyboard Shortcuts:
Ctrl+N: New plot
Ctrl+S: Save plot
Ctrl+C: Copy plot
Ctrl+V: Paste function
Ctrl++: Zoom in
Ctrl+-: Zoom out"""
        messagebox.showinfo("Help", help_text)

    def show_about(self):
        """Show about information."""
        about_text = """Pro-Per Graphing App
Created by Per Virgil B. Wabe
Version 1.0

A modern function visualization tool with:
- Advanced mathematical analysis
- Sleek dark mode interface
- Professional visualization features

Created with Python, NumPy, SciPy, SymPy, and Matplotlib"""
        messagebox.showinfo("About", about_text)

    def show_preferences(self):
        """Show preferences dialog (placeholder)."""
        messagebox.showinfo("Preferences", "Preferences dialog will be implemented in a future version")

    def show_examples(self):
        """Show example functions."""
        examples = """Example Functions:

Basic Polynomial:
x**2 + 3*x - 5

Trigonometric:
sin(x) * cos(2*x)

Exponential:
exp(-x/5) * sin(x)

Logarithmic:
log(x**2 + 1)

Combined:
sqrt(x**2 + 1) * sin(x)"""
        messagebox.showinfo("Example Functions", examples)

    def open_docs(self):
        """Open online documentation."""
        webbrowser.open("https://example.com/function-visualizer-docs")

    def adjust_font_size(self, delta):
        """Adjust font size for better readability."""
        try:
            current_size = self.ui_font[1]
            new_size = max(8, min(14, current_size + delta))

            # Update all fonts
            self.ui_font = (self.ui_font[0], new_size)
            self.code_font = (self.code_font[0], new_size)
            self.button_font = (self.button_font[0], new_size)
            self.title_font = (self.title_font[0], new_size + 2)

            # Update widget fonts
            for widget in self.root.winfo_children():
                if isinstance(widget, (ttk.Label, ttk.Button, ttk.Checkbutton)):
                    widget.configure(font=self.ui_font)
                elif isinstance(widget, ttk.Entry):
                    widget.configure(font=self.code_font)

            self.info_text.configure(font=self.code_font)
            self.status_label.configure(font=self.ui_font)

            self.status_label.config(text=f"Font size adjusted to {new_size}pt", foreground=self.accent_color)
        except Exception as e:
            self.status_label.config(text=f"Error adjusting font size: {str(e)}", foreground=self.error_color)


def main():
    root = tk.Tk()

    # Set window icon (placeholder - in real app use proper icon)
    try:
        root.iconbitmap('function_icon.ico')
    except:
        pass

    app = ModernFunctionVisualizer(root)

    window_width = 1100
    window_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    root.mainloop()


if __name__ == "__main__":
    main()