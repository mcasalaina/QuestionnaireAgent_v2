#!/usr/bin/env python3
"""
Script to demonstrate the UI behavior before and after the fix.
This creates a simplified mock version for testing purposes.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from unittest.mock import Mock, patch
import sys
import os

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MockQuestionnaireUI:
    """Simplified version for demonstration purposes."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Questionnaire Agent - UI Demo")
        self.root.geometry("800x600")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Question section
        question_label = ttk.Label(left_frame, text="Question")
        question_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.question_text = scrolledtext.ScrolledText(left_frame, height=8, width=50)
        self.question_text.insert(tk.END, "Does your service offer video generative AI?")
        self.question_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.ask_button = tk.Button(button_frame, text="🤖 Ask", command=self.on_ask_clicked)
        self.ask_button.pack(fill=tk.X, pady=(0, 5))
        
        self.import_button = tk.Button(button_frame, text="📊 Import From Excel", command=self.on_import_excel_clicked)
        self.import_button.pack(fill=tk.X)
        
        # Right panel with tabs
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Answer tab
        answer_frame = ttk.Frame(self.notebook)
        self.notebook.add(answer_frame, text="Answer")
        self.answer_text = scrolledtext.ScrolledText(answer_frame, height=20, width=50)
        self.answer_text.insert(tk.END, "Response will appear here after clicking Ask!")
        self.answer_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Documentation tab
        docs_frame = ttk.Frame(self.notebook)
        self.notebook.add(docs_frame, text="Documentation")
        self.docs_text = scrolledtext.ScrolledText(docs_frame, height=20, width=50)
        self.docs_text.insert(tk.END, "Documentation will appear here...")
        self.docs_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Reasoning tab
        reasoning_frame = ttk.Frame(self.notebook)
        self.notebook.add(reasoning_frame, text="Reasoning")
        self.reasoning_text = scrolledtext.ScrolledText(reasoning_frame, height=20, width=50)
        self.reasoning_text.insert(tk.END, "Reasoning will appear here...")
        self.reasoning_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status label
        self.status_label = ttk.Label(self.root, text="Demo: Question box clearing behavior")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
    
    def on_ask_clicked(self):
        messagebox.showinfo("Demo", "Ask button clicked - this is just a demo")
    
    def on_import_excel_clicked(self):
        """Demonstrate the question box clearing behavior."""
        # Show a message explaining what's happening
        messagebox.showinfo("Demo", 
                          "This demonstrates the question box clearing behavior when Excel processing starts.\n\n" +
                          "BEFORE: Question box contains default text\n" +
                          "AFTER: Question box will be cleared")
        
        # Switch to Reasoning tab
        self.notebook.select(2)
        
        # Clear reasoning text
        self.reasoning_text.delete(1.0, tk.END)
        self.reasoning_text.insert(tk.END, "Starting Excel processing...\n")
        
        # THIS IS THE FIX: Clear the question text box when Excel processing starts
        if self.question_text:
            self.question_text.delete(1.0, tk.END)
        
        # Update status
        self.status_label.config(text="✅ Question box cleared - Excel processing would start here")
        
        # Simulate some processing messages
        self.reasoning_text.insert(tk.END, "Reading Excel file...\n")
        self.reasoning_text.insert(tk.END, "Identifying columns...\n") 
        self.reasoning_text.insert(tk.END, "Processing questions...\n")
        
        # After a delay, simulate showing first question
        self.root.after(2000, self.simulate_first_question)
    
    def simulate_first_question(self):
        """Simulate showing the first question being processed."""
        first_question = "What is Azure AI Vision?"
        self.question_text.insert(tk.END, first_question)
        self.reasoning_text.insert(tk.END, f"Now processing: {first_question}\n")
        self.status_label.config(text="✅ First question now shown in question box")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MockQuestionnaireUI()
    app.run()