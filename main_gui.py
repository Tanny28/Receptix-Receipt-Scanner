import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import os
from datetime import datetime
import threading
from ocr_utils import extract_text_from_image
from categorizer import categorize_expenses, parse_amounts_and_items,smart_categorize
import logging

class ReceptixGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Receptix - Smart Receipt Scanner")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize variables
        self.current_image_path = None
        self.extracted_text = ""
        self.expense_data = {}
        
        # Setup logging
        self.setup_logging()
        
        # Create GUI elements
        self.create_widgets()
        
        # Center the window
        self.center_window()
    
    def setup_logging(self):
        """Setup logging configuration"""
        os.makedirs("logs", exist_ok=True)
        logging.basicConfig(
            filename="logs/receipts.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """Create and arrange GUI widgets"""
        # Main title
        title_label = tk.Label(
            self.root, 
            text="🧾 Receptix - Smart Receipt Scanner", 
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=10)
        
        # Create main frames
        self.create_upload_frame()
        self.create_text_display_frame()
        self.create_results_frame()
        self.create_action_buttons_frame()
        
        # Status bar
        self.create_status_bar()
    
    def create_upload_frame(self):
        """Create image upload section"""
        upload_frame = tk.LabelFrame(
            self.root, 
            text="📸 Upload Receipt Image", 
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="#34495e"
        )
        upload_frame.pack(fill="x", padx=20, pady=10)
        
        # File path display
        self.file_path_var = tk.StringVar(value="No file selected")
        path_label = tk.Label(
            upload_frame, 
            textvariable=self.file_path_var,
            bg="#f0f0f0",
            fg="#7f8c8d",
            font=("Arial", 10)
        )
        path_label.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        # Browse button
        browse_btn = tk.Button(
            upload_frame,
            text="📁 Browse Image",
            command=self.browse_image,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief="flat"
        )
        browse_btn.pack(side="right", padx=10, pady=10)
    
    def create_text_display_frame(self):
        """Create extracted text display section"""
        text_frame = tk.LabelFrame(
            self.root,
            text="📄 Extracted Text",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="#34495e"
        )
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Text display area
        self.text_display = scrolledtext.ScrolledText(
            text_frame,
            height=8,
            font=("Courier", 10),
            bg="#ffffff",
            fg="#2c3e50",
            wrap=tk.WORD
        )
        self.text_display.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_results_frame(self):
        """Create results display section"""
        results_frame = tk.LabelFrame(
            self.root,
            text="💰 Expense Analysis",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="#34495e"
        )
        results_frame.pack(fill="x", padx=20, pady=10)
        
        # Total amount display
        total_frame = tk.Frame(results_frame, bg="#f0f0f0")
        total_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(
            total_frame, 
            text="Total Amount:", 
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        ).pack(side="left")
        
        self.total_amount_var = tk.StringVar(value="$0.00")
        tk.Label(
            total_frame,
            textvariable=self.total_amount_var,
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="#e74c3c"
        ).pack(side="right")
        
        # Category breakdown
        self.create_category_tree(results_frame)
    
    def create_category_tree(self, parent):
        """Create treeview for category breakdown"""
        tree_frame = tk.Frame(parent, bg="#f0f0f0")
        tree_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(
            tree_frame,
            text="Category Breakdown:",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        ).pack(anchor="w")
        
        # Treeview
        self.category_tree = ttk.Treeview(
            tree_frame,
            columns=("Amount", "Items"),
            show="tree headings",
            height=6
        )
        
        # Configure columns
        self.category_tree.heading("#0", text="Category")
        self.category_tree.heading("Amount", text="Amount")
        self.category_tree.heading("Items", text="Items Found")
        
        self.category_tree.column("#0", width=200)
        self.category_tree.column("Amount", width=100, anchor="center")
        self.category_tree.column("Items", width=200)
        
        # Scrollbar for treeview
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.category_tree.yview)
        self.category_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.category_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
    
    def create_action_buttons_frame(self):
        """Create action buttons"""
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        # Scan button
        self.scan_btn = tk.Button(
            button_frame,
            text="🔍 Scan & Categorize",
            command=self.scan_and_categorize,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            relief="flat",
            state="disabled"
        )
        self.scan_btn.pack(side="left", padx=5)
        
        # Clear button
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear",
            command=self.clear_all,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            relief="flat"
        )
        clear_btn.pack(side="left", padx=5)
        
        # Save report button
        self.save_btn = tk.Button(
            button_frame,
            text="💾 Save Report",
            command=self.save_report,
            bg="#f39c12",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            relief="flat",
            state="disabled"
        )
        self.save_btn.pack(side="left", padx=5)

        
        # Exit button
        exit_btn = tk.Button(
            button_frame,
            text="❌ Exit",
            command=self.root.quit,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12, "bold"),
            cursor="hand2",
            relief="flat"
        )
        exit_btn.pack(side="right", padx=5)
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_var = tk.StringVar(value="Ready - Please upload a receipt image")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w",
            bg="#ecf0f1",
            fg="#7f8c8d",
            font=("Arial", 9)
        )
        status_bar.pack(side="bottom", fill="x")
    
    def browse_image(self):
        """Open file dialog to browse for image"""
        file_types = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select Receipt Image",
            filetypes=file_types
        )
        
        if file_path:
            self.current_image_path = file_path
            self.file_path_var.set(os.path.basename(file_path))
            self.scan_btn.config(state="normal")
            self.status_var.set(f"Image loaded: {os.path.basename(file_path)}")
            logging.info(f"Image loaded: {file_path}")
    
    def scan_and_categorize(self):
        """Perform OCR and categorization in a separate thread"""
        if not self.current_image_path:
            messagebox.showerror("Error", "Please select an image first!")
            return
        
        self.scan_btn.config(state="disabled", text="🔄 Processing...")
        self.status_var.set("Processing image - This may take a moment...")
        
        # Run OCR in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self._process_image)
        thread.daemon = True
        thread.start()
    
    def _process_image(self):
        """Process image (OCR and categorization) - runs in separate thread"""
        try:
            # Extract text using OCR
            self.status_var.set("Extracting text from image...")
            self.extracted_text = extract_text_from_image(self.current_image_path)
            
            # Update text display in main thread
            self.root.after(0, self._update_text_display)
            
            # Parse amounts and items
            self.status_var.set("Analyzing expenses...")
            amounts, items = parse_amounts_and_items(self.extracted_text)
            
            # Categorize expenses
            
            self.expense_data, total_amount = smart_categorize(self.extracted_text)

            # Update GUI in main thread
            self.root.after(0, self._update_results)
            
            # Log the scan
            logging.info(f"Receipt processed: {self.current_image_path}")
            logging.info(f"Total amount: ${sum(amounts):.2f}")
            logging.info(f"Categories found: {list(self.expense_data.keys())}")
            
        except Exception as e:
            error_msg = f"Error processing image: {str(e)}"
            logging.error(error_msg)
            self.root.after(0, lambda: self._show_error(error_msg))
        finally:
            # Re-enable button in main thread
            self.root.after(0, self._reset_scan_button)
    
    def _update_text_display(self):
        """Update text display widget (called from main thread)"""
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(1.0, self.extracted_text)
    
    def _update_results(self):
        """Update results display (called from main thread)"""
        # Calculate total
        total = sum(sum(data['amounts']) for data in self.expense_data.values())
        self.total_amount_var.set(f"${total:.2f}")
        
        # Clear existing tree items
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
        
        # Populate category tree
        for category, data in self.expense_data.items():
            if data['amounts']:  # Only show categories with amounts
                category_total = sum(data['amounts'])
                items_text = ", ".join(data['items'][:3])  # Show first 3 items
                if len(data['items']) > 3:
                    items_text += f" (+{len(data['items'])-3} more)"
                
                self.category_tree.insert(
                    "",
                    "end",
                    text=f"🏷️ {category}",
                    values=(f"${category_total:.2f}", items_text)
                )
        
        self.save_btn.config(state="normal")
        self.status_var.set("Analysis complete! Review the results above.")
    
    def _show_error(self, error_msg):
        """Show error message (called from main thread)"""
        messagebox.showerror("Processing Error", error_msg)
        self.status_var.set("Error occurred - Please try again")
    
    def _reset_scan_button(self):
        """Reset scan button state (called from main thread)"""
        self.scan_btn.config(state="normal", text="🔍 Scan & Categorize")
    
    def clear_all(self):
        """Clear all data and reset interface"""
        self.current_image_path = None
        self.extracted_text = ""
        self.expense_data = {}
        
        self.file_path_var.set("No file selected")
        self.text_display.delete(1.0, tk.END)
        self.total_amount_var.set("$0.00")
        
        # Clear tree
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
        
        self.scan_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        self.status_var.set("Ready - Please upload a receipt image")
        
        logging.info("Interface cleared")
    
    def save_report(self):
        """Save expense report to file"""
        if not self.expense_data:
            messagebox.showwarning("Warning", "No data to save!")
            return
        
        # Create reports directory
        os.makedirs("reports", exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/receipt_report_{timestamp}.txt"
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("=" * 50 + "\n")
                f.write("RECEPTIX - EXPENSE REPORT\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Source Image: {os.path.basename(self.current_image_path) if self.current_image_path else 'N/A'}\n")
                f.write("-" * 50 + "\n\n")
                
                # Write extracted text
                f.write("EXTRACTED TEXT:\n")
                f.write("-" * 20 + "\n")
                f.write(self.extracted_text + "\n\n")
                
                # Write expense breakdown
                f.write("EXPENSE BREAKDOWN:\n")
                f.write("-" * 20 + "\n")
                
                total = 0
                for category, data in self.expense_data.items():
                    if data['amounts']:
                        category_total = sum(data['amounts'])
                        total += category_total
                        f.write(f"\n{category.upper()}:\n")
                        f.write(f"  Total: ${category_total:.2f}\n")
                        f.write(f"  Items: {', '.join(data['items'])}\n")
                
                f.write(f"\nGRAND TOTAL: ${total:.2f}\n")
                f.write("=" * 50 + "\n")
            
            messagebox.showinfo("Success", f"Report saved to:\n{filename}")
            self.status_var.set(f"Report saved: {os.path.basename(filename)}")
            logging.info(f"Report saved: {filename}")
            
        except Exception as e:
            error_msg = f"Error saving report: {str(e)}"
            messagebox.showerror("Error", error_msg)
            logging.error(error_msg)


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = ReceptixGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()