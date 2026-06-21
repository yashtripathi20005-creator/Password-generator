"""
Password Generator - Main module
A complete password generator with GUI and CLI options
"""

import random
import string
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import json
import os
from datetime import datetime


class PasswordGenerator:
    """Core password generation logic"""
    
    def __init__(self):
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?/~"
        self.ambiguous_chars = "il1Lo0O"
        
    def generate_password(self, length=16, use_lower=True, use_upper=True, 
                         use_digits=True, use_symbols=True, 
                         exclude_ambiguous=False, min_each_type=0):
        """
        Generate a secure password
        
        Args:
            length (int): Desired password length
            use_lower (bool): Include lowercase letters
            use_upper (bool): Include uppercase letters
            use_digits (bool): Include digits
            use_symbols (bool): Include symbols
            exclude_ambiguous (bool): Exclude ambiguous characters (il1Lo0O)
            min_each_type (int): Minimum characters from each selected type
            
        Returns:
            str: Generated password
        """
        # Build character pool
        pool = ""
        if use_lower:
            pool += self.lowercase
        if use_upper:
            pool += self.uppercase
        if use_digits:
            pool += self.digits
        if use_symbols:
            pool += self.symbols
            
        if not pool:
            raise ValueError("At least one character type must be selected")
            
        # Remove ambiguous characters if requested
        if exclude_ambiguous:
            for char in self.ambiguous_chars:
                pool = pool.replace(char, "")
                
        # Ensure minimum characters from each type
        selected_types = []
        if use_lower:
            selected_types.append(self.lowercase)
        if use_upper:
            selected_types.append(self.uppercase)
        if use_digits:
            selected_types.append(self.digits)
        if use_symbols:
            selected_types.append(self.symbols)
            
        if min_each_type > 0 and len(selected_types) * min_each_type <= length:
            # Start with required minimum from each type
            password_parts = []
            for char_set in selected_types:
                for _ in range(min_each_type):
                    password_parts.append(random.choice(char_set))
            
            # Fill remaining length with random chars from full pool
            remaining = length - len(password_parts)
            for _ in range(remaining):
                password_parts.append(random.choice(pool))
            
            # Shuffle the password
            random.shuffle(password_parts)
            return ''.join(password_parts)
        else:
            # Simple generation
            return ''.join(random.choice(pool) for _ in range(length))
    
    def generate_memorable_password(self, words=3, separator="-", 
                                   include_numbers=True, capitalize=True):
        """
        Generate a memorable passphrase
        
        Args:
            words (int): Number of words
            separator (str): Separator between words
            include_numbers (bool): Include a number
            capitalize (bool): Capitalize each word
            
        Returns:
            str: Generated passphrase
        """
        word_list = [
            "apple", "bear", "cloud", "dragon", "eagle", "forest", "garden",
            "happy", "island", "jewel", "king", "lion", "moon", "night",
            "ocean", "peace", "queen", "rain", "sun", "tree", "umbrella",
            "vision", "water", "xenon", "yellow", "zeppelin", "mountain",
            "river", "star", "fire", "ice", "wind", "stone", "shadow"
        ]
        
        selected_words = random.sample(word_list, min(words, len(word_list)))
        
        if capitalize:
            selected_words = [word.capitalize() for word in selected_words]
            
        password = separator.join(selected_words)
        
        if include_numbers:
            password += str(random.randint(10, 99))
            
        return password
    
    def evaluate_strength(self, password):
        """
        Evaluate password strength
        
        Returns:
            dict: Strength metrics
        """
        score = 0
        feedback = []
        
        # Length check
        length = len(password)
        if length >= 12:
            score += 25
        elif length >= 8:
            score += 15
        else:
            feedback.append("Password is too short")
            
        # Character variety checks
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in self.symbols for c in password)
        
        if has_lower:
            score += 10
        if has_upper:
            score += 15
        if has_digit:
            score += 15
        if has_symbol:
            score += 20
            
        # Variety feedback
        types_used = sum([has_lower, has_upper, has_digit, has_symbol])
        if types_used < 3:
            feedback.append("Use more character types")
            
        # Uniqueness checks
        if len(set(password)) < length * 0.7:
            feedback.append("Too many repeated characters")
            
        # Common patterns
        common_patterns = ["123", "abc", "qwerty", "password", "admin", "letmein"]
        for pattern in common_patterns:
            if pattern.lower() in password.lower():
                score -= 10
                feedback.append(f"Avoid common patterns like '{pattern}'")
                
        # Final scoring
        if score < 40:
            strength = "Weak"
        elif score < 60:
            strength = "Fair"
        elif score < 80:
            strength = "Good"
        else:
            strength = "Strong"
            
        return {
            'score': min(100, max(0, score)),
            'strength': strength,
            'feedback': feedback,
            'length': length,
            'has_lower': has_lower,
            'has_upper': has_upper,
            'has_digit': has_digit,
            'has_symbol': has_symbol
        }


class PasswordHistory:
    """Manage password history"""
    
    def __init__(self, history_file="password_history.json"):
        self.history_file = history_file
        self.history = []
        self.load_history()
        
    def load_history(self):
        """Load history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except:
                self.history = []
                
    def save_history(self):
        """Save history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history[-100:], f, indent=2)  # Keep last 100
            
    def add_password(self, password, service="", strength=""):
        """Add password to history"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'password': password,
            'service': service,
            'strength': strength
        }
        self.history.append(entry)
        self.save_history()
        
    def get_history(self, limit=20):
        """Get recent history"""
        return self.history[-limit:][::-1]
    
    def clear_history(self):
        """Clear history"""
        self.history = []
        self.save_history()


class PasswordGeneratorApp:
    """Main GUI Application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator Pro")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        
        # Initialize components
        self.generator = PasswordGenerator()
        self.history = PasswordHistory()
        
        # Variables
        self.password_var = tk.StringVar()
        self.length_var = tk.IntVar(value=16)
        self.use_lower_var = tk.BooleanVar(value=True)
        self.use_upper_var = tk.BooleanVar(value=True)
        self.use_digits_var = tk.BooleanVar(value=True)
        self.use_symbols_var = tk.BooleanVar(value=True)
        self.exclude_ambiguous_var = tk.BooleanVar(value=False)
        self.min_each_type_var = tk.IntVar(value=1)
        self.memorable_var = tk.BooleanVar(value=False)
        self.words_var = tk.IntVar(value=4)
        
        self.create_widgets()
        self.generate_password()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Secure Password Generator", 
                               font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Password display area
        display_frame = ttk.LabelFrame(main_frame, text="Generated Password", padding="10")
        display_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.password_entry = ttk.Entry(display_frame, textvariable=self.password_var, 
                                       font=('Courier', 14), width=50)
        self.password_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        
        copy_btn = ttk.Button(display_frame, text="📋 Copy", command=self.copy_password)
        copy_btn.grid(row=0, column=1, padx=5)
        
        generate_btn = ttk.Button(display_frame, text="🔄 Generate", command=self.generate_password)
        generate_btn.grid(row=0, column=2, padx=5)
        
        # Strength indicator
        self.strength_label = ttk.Label(display_frame, text="Strength: ")
        self.strength_label.grid(row=1, column=0, columnspan=3, pady=5)
        
        # Settings area
        settings_frame = ttk.LabelFrame(main_frame, text="Password Settings", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Length
        ttk.Label(settings_frame, text="Length:").grid(row=0, column=0, sticky=tk.W)
        ttk.Scale(settings_frame, from_=4, to=64, variable=self.length_var, 
                 orient=tk.HORIZONTAL, length=200).grid(row=0, column=1, padx=5)
        ttk.Label(settings_frame, textvariable=self.length_var).grid(row=0, column=2)
        
        # Character types
        ttk.Checkbutton(settings_frame, text="Lowercase", 
                       variable=self.use_lower_var).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(settings_frame, text="Uppercase", 
                       variable=self.use_upper_var).grid(row=1, column=1, sticky=tk.W)
        ttk.Checkbutton(settings_frame, text="Digits", 
                       variable=self.use_digits_var).grid(row=1, column=2, sticky=tk.W)
        ttk.Checkbutton(settings_frame, text="Symbols", 
                       variable=self.use_symbols_var).grid(row=2, column=0, sticky=tk.W)
        ttk.Checkbutton(settings_frame, text="Exclude Ambiguous (il1Lo0O)", 
                       variable=self.exclude_ambiguous_var).grid(row=2, column=1, columnspan=2, sticky=tk.W)
        
        # Memorable passphrase
        ttk.Checkbutton(settings_frame, text="Use Memorable Passphrase", 
                       variable=self.memorable_var).grid(row=3, column=0, columnspan=2, sticky=tk.W)
        ttk.Label(settings_frame, text="Words:").grid(row=3, column=2, sticky=tk.W)
        ttk.Spinbox(settings_frame, from_=2, to=8, textvariable=self.words_var, 
                   width=5).grid(row=3, column=3, padx=5)
        
        # Minimum each type
        ttk.Label(settings_frame, text="Min. of each type:").grid(row=4, column=0, sticky=tk.W)
        ttk.Spinbox(settings_frame, from_=0, to=5, textvariable=self.min_each_type_var, 
                   width=5).grid(row=4, column=1, sticky=tk.W)
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(action_frame, text="🔍 Evaluate Strength", 
                  command=self.evaluate_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="💾 Save to History", 
                  command=self.save_to_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="📜 View History", 
                  command=self.show_history).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
    def generate_password(self):
        """Generate a new password"""
        try:
            if self.memorable_var.get():
                password = self.generator.generate_memorable_password(
                    words=self.words_var.get(),
                    include_numbers=True,
                    capitalize=True
                )
            else:
                password = self.generator.generate_password(
                    length=self.length_var.get(),
                    use_lower=self.use_lower_var.get(),
                    use_upper=self.use_upper_var.get(),
                    use_digits=self.use_digits_var.get(),
                    use_symbols=self.use_symbols_var.get(),
                    exclude_ambiguous=self.exclude_ambiguous_var.get(),
                    min_each_type=self.min_each_type_var.get()
                )
            self.password_var.set(password)
            self.status_var.set("Password generated successfully")
            self.update_strength_display(password)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error generating password")
            
    def update_strength_display(self, password):
        """Update strength indicator"""
        strength = self.generator.evaluate_strength(password)
        colors = {"Weak": "red", "Fair": "orange", "Good": "blue", "Strong": "green"}
        self.strength_label.config(
            text=f"Strength: {strength['strength']} (Score: {strength['score']}/100)",
            foreground=colors.get(strength['strength'], 'black')
        )
        
    def evaluate_password(self):
        """Show detailed strength evaluation"""
        password = self.password_var.get()
        if not password:
            messagebox.showinfo("Info", "Generate a password first")
            return
            
        strength = self.generator.evaluate_strength(password)
        
        details = f"""
Password Length: {strength['length']}
Character Types:
  • Lowercase: {'✓' if strength['has_lower'] else '✗'}
  • Uppercase: {'✓' if strength['has_upper'] else '✗'}
  • Digits: {'✓' if strength['has_digit'] else '✗'}
  • Symbols: {'✓' if strength['has_symbol'] else '✗'}

Strength Score: {strength['score']}/100
Strength Level: {strength['strength']}

Feedback:
{chr(10).join('• ' + f for f in strength['feedback']) if strength['feedback'] else '✓ No issues detected'}
"""
        messagebox.showinfo("Password Strength Analysis", details)
        
    def copy_password(self):
        """Copy password to clipboard"""
        password = self.password_var.get()
        if password:
            pyperclip.copy(password)
            self.status_var.set("Password copied to clipboard!")
        else:
            messagebox.showinfo("Info", "Generate a password first")
            
    def save_to_history(self):
        """Save current password to history"""
        password = self.password_var.get()
        if not password:
            messagebox.showinfo("Info", "Generate a password first")
            return
            
        strength = self.generator.evaluate_strength(password)
        self.history.add_password(password, "Manual Entry", strength['strength'])
        self.status_var.set("Password saved to history")
        messagebox.showinfo("Success", "Password saved to history!")
        
    def show_history(self):
        """Display password history"""
        history = self.history.get_history()
        if not history:
            messagebox.showinfo("History", "No passwords in history")
            return
            
        # Create a new window
        history_window = tk.Toplevel(self.root)
        history_window.title("Password History")
        history_window.geometry("600x400")
        
        # Create text widget
        text_widget = tk.Text(history_window, wrap=tk.WORD, font=('Courier', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(text_widget)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text_widget.yview)
        
        # Display history
        text_widget.insert(tk.END, "Password History\n" + "="*50 + "\n\n")
        for entry in history[:20]:  # Show last 20
            text_widget.insert(tk.END, 
                f"Date: {entry['timestamp'][:19]}\n"
                f"Password: {entry['password']}\n"
                f"Strength: {entry.get('strength', 'Unknown')}\n"
                f"Service: {entry.get('service', 'Manual')}\n"
                + "-"*50 + "\n")
        
        text_widget.config(state=tk.DISABLED)
        
        # Clear history button
        clear_btn = ttk.Button(history_window, text="Clear History", 
                              command=lambda: self.clear_history(history_window))
        clear_btn.pack(pady=5)
        
    def clear_history(self, window):
        """Clear password history"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear history?"):
            self.history.clear_history()
            window.destroy()
            messagebox.showinfo("Success", "History cleared")
            self.status_var.set("History cleared")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
