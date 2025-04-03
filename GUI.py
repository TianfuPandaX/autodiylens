# optimized_lensUI.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from lensopt.optimizer import OpticalSystemOptimizer
from lensopt.api import PythonStandaloneApplication1
from lensopt.dataloader import LensDataLoader
import traceback
import sys

class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

class OpticalSystemOptimizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Optical System Optimizer")
        self.root.geometry("900x900")
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initialize variables
        self.file_path = tk.StringVar()
        self.lens_count = tk.StringVar(value="3")
        self.rms_threshold = tk.StringVar(value="300000")
        self.aperture = tk.StringVar(value="10")
        self.num_cores = tk.StringVar(value="8")
        self.max_iterations = tk.StringVar(value="5")
        self.ap = tk.StringVar(value="1")
        self.type_code = tk.StringVar(value="1")
        
        self.create_widgets()
        
        # Redirect output
        redirector = RedirectText(self.log_text)
        sys.stdout = redirector
        sys.stderr = redirector

    def create_widgets(self):
        # File selection
        ttk.Label(self.main_frame, text="Lens Data File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.main_frame, textvariable=self.file_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(self.main_frame, text="Browse", command=self.browse_file).grid(row=0, column=2)
        
        # Parameter inputs
        # Lens count
        ttk.Label(self.main_frame, text="Lens Count:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.main_frame, textvariable=self.lens_count).grid(row=1, column=1, sticky=tk.W)
        
        # RMS threshold
        ttk.Label(self.main_frame, text="RMS Threshold:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.main_frame, textvariable=self.rms_threshold).grid(row=2, column=1, sticky=tk.W)
        
        # Aperture value
        ttk.Label(self.main_frame, text="Aperture Value:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.main_frame, textvariable=self.aperture).grid(row=3, column=1, sticky=tk.W)
        
        # CPU cores
        ttk.Label(self.main_frame, text="CPU Cores:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.main_frame, textvariable=self.num_cores).grid(row=4, column=1, sticky=tk.W)
        
        # Max iterations
        ttk.Label(self.main_frame, text="Max Iterations:").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.main_frame, textvariable=self.max_iterations).grid(row=5, column=1, sticky=tk.W)
        
        # AP value
        ttk.Label(self.main_frame, text="Aperture Position:").grid(row=6, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.main_frame, textvariable=self.ap).grid(row=6, column=1, sticky=tk.W)
        
        # Type code
        ttk.Label(self.main_frame, text="Optimization Type:").grid(row=7, column=0, sticky=tk.W, pady=5)
        type_frame = ttk.Frame(self.main_frame)
        type_frame.grid(row=7, column=1, sticky=tk.W)
        ttk.Radiobutton(type_frame, text="Entrance Pupil Diameter", variable=self.type_code, value="1").pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="Aperture F-Number", variable=self.type_code, value="2").pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="Macro NA", variable=self.type_code, value="3").pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, length=400, mode='indeterminate')
        self.progress.grid(row=8, column=0, columnspan=3, pady=10)
        
        # Status label
        self.status_label = ttk.Label(self.main_frame, text="Ready")
        self.status_label.grid(row=9, column=0, columnspan=3)
        
        # Log text box
        self.log_text = tk.Text(self.main_frame, height=40, width=120)
        self.log_text.grid(row=10, column=0, columnspan=3, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=10, column=3, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # Start button
        ttk.Button(self.main_frame, text="Start Optimization", command=self.start_optimization).grid(row=11, column=0, columnspan=3, pady=10)
        
    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
            self.log_message(f"Selected file: {filename}")
            
    def start_optimization(self):
        # Validate input
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a data file")
            return
        
        # Start progress bar
        self.progress.start()
        self.status_label.config(text="Optimizing...")
        self.log_message("Starting optimization process...")

        # Run optimization in a new thread
        threading.Thread(target=self.run_optimization, daemon=True).start()

    def run_optimization(self):
        try:
            # Initialize ZOS application
            self.log_message("Initializing ZOS application...")
            zos = PythonStandaloneApplication1()
            ZOSAPI = zos.ZOSAPI
            TheApplication = zos.TheApplication
            TheSystem = zos.TheSystem
            
            # Load lens data
            self.log_message("Loading lens data...")
            loader = LensDataLoader(
                self.file_path.get(),
                int(self.lens_count.get())
            )
            loader.load_data()
            lens_combinations = loader.get_combinations()
            self.log_message(f"Successfully loaded {len(lens_combinations)} lens combinations")

            # Read parameters
            lens_count = int(self.lens_count.get())
            rms_threshold = float(self.rms_threshold.get())
            aperture = float(self.aperture.get())
            num_cores = int(self.num_cores.get())
            max_iterations = int(self.max_iterations.get())
            ap_position = int(self.ap.get())
            type_code = int(self.type_code.get())
            
            self.log_message("Creating optimizer...")
            # Create optimizer instance
            optimizer = OpticalSystemOptimizer(
                ZOSAPI,
                TheSystem,
                lens_count=lens_count,
                rms_threshold=rms_threshold,
                aperture=aperture,
                num_cores=num_cores,
                max_iterations=max_iterations,
                ap_position=ap_position,
                is_macro=(type_code == 3)
            )
            
            self.log_message(f"Using {lens_count}-lens optimizer with aperture position {ap_position}")
            
            # Execute optimization
            self.log_message(f"Starting optimization, type code: {type_code}")
            optimizer.optimize_lens_combinations(lens_combinations, type_code)
            
            # Update UI on main thread after completion
            self.root.after(0, self.optimization_complete)
            
        except Exception as e:
            error_msg = f"Error details:\n{traceback.format_exc()}"
            self.root.after(0, lambda: self.show_error(error_msg))
            
    def optimization_complete(self):
        self.progress.stop()
        self.status_label.config(text="Optimization complete")
        self.log_message("Optimization process completed")
        messagebox.showinfo("Complete", "Optimization process completed")
        
    def show_error(self, error_message):
        self.progress.stop()
        self.status_label.config(text="Error occurred")
        self.log_message(f"Error: {error_message}")
        messagebox.showerror("Error", f"Error during optimization:\n{error_message}")

if __name__ == '__main__':
    root = tk.Tk()
    app = OpticalSystemOptimizerGUI(root)
    root.mainloop()