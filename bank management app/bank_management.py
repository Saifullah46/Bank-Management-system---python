import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import os
import base64
import time
import random
import hashlib
import datetime
from math import sin
from PIL import Image, ImageTk, ImageDraw
import io
import threading
 
class BankManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Bank Management System")
        self.root.geometry("1100x650")
        self.root.resizable(True, True)
        self.root.configure(bg="#f5f5f5")
         
        # Initialize database
        self.create_database()
         
        # Load and set icon
        self.load_icons()
         
        # Colors
        self.primary_color = "#1a73e8"
        self.secondary_color = "#f5f5f5"
        self.accent_color = "#4285f4"
        self.text_color = "#202124"
        self.error_color = "#ea4335"
        self.success_color = "#34a853"
         
        # Variables
        self.current_user = None
        self.current_frame = None
        self.animation_running = False
         
        # Start with login screen
        self.show_login()
     
    def create_database(self):
        """Create database and tables if they don't exist"""
        conn = sqlite3.connect('bank_management.db')
        cursor = conn.cursor()
         
        # Create Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT,
            registration_date TEXT,
            profile_pic BLOB
        )
        ''')
         
        # Create Accounts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            account_number TEXT UNIQUE NOT NULL,
            account_type TEXT NOT NULL,
            balance REAL DEFAULT 0.0,
            opening_date TEXT,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
         
        # Create Transactions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            transaction_date TEXT,
            reference_number TEXT,
            status TEXT DEFAULT 'completed',
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        )
        ''')
         
        conn.commit()
        conn.close()
     
    def load_icons(self):
        """Load and prepare icons"""
        # Create a dictionary to store icons
        self.icons = {}
         
        # Function to generate a simple icon as base64 string
        def create_icon(color, shape="circle", size=64):
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
             
            if shape == "circle":
                draw.ellipse((4, 4, size-4, size-4), fill=color)
            elif shape == "square":
                draw.rectangle((4, 4, size-4, size-4), fill=color)
            elif shape == "home":
                # Simple house shape
                draw.polygon([(size//2, 4), (size-4, size//2), (size-4, size-4), (4, size-4), (4, size//2)], fill=color)
            elif shape == "user":
                # User icon
                draw.ellipse((size//4, 4, 3*size//4, size//2), fill=color)  # Head
                draw.ellipse((size//8, size//2, 7*size//8, size-4), fill=color)  # Body
                 
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue())
         
        # Generate and store icons
        self.icons["home"] = create_icon("#1a73e8", "home")
        self.icons["user"] = create_icon("#4285f4", "user")
        self.icons["account"] = create_icon("#34a853", "circle")
        self.icons["transaction"] = create_icon("#fbbc04", "square")
        self.icons["logout"] = create_icon("#ea4335", "circle")
         
        # Create PhotoImage objects for icons
        self.icon_images = {}
        for name, data in self.icons.items():
            image_data = base64.b64decode(data)
            image = Image.open(io.BytesIO(image_data))
            self.icon_images[name] = ImageTk.PhotoImage(image)
     
    def apply_style(self):
        """Apply custom styles to widgets"""
        style = ttk.Style()
        style.theme_use('clam')
         
        # Configure styles for different widget types
        style.configure('TFrame', background=self.secondary_color)
        style.configure('TLabel', background=self.secondary_color, foreground=self.text_color, font=('Helvetica', 10))
        style.configure('TEntry', fieldbackground='white', font=('Helvetica', 10))
        style.configure('TButton', 
                        background=self.primary_color, 
                        foreground='white', 
                        font=('Helvetica', 10, 'bold'),
                        borderwidth=0,
                        focusthickness=3,
                        focuscolor=self.accent_color)
        style.map('TButton', 
                 background=[('active', self.accent_color), ('disabled', '#cccccc')],
                 foreground=[('disabled', '#666666')])
     
    def create_custom_button(self, parent, text, command, icon=None, **kwargs):
        """Create a custom styled button with optional icon"""
        frame = ttk.Frame(parent, style='Custom.TFrame')
         
        if icon:
            icon_label = ttk.Label(frame, image=self.icon_images.get(icon))
            icon_label.pack(side=tk.LEFT, padx=(5, 0))
         
        button = ttk.Button(frame, text=text, command=command, **kwargs)
        button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5 if icon else 0, 5), pady=5)
         
        return frame
     
    def animate_frame(self, frame, direction="right"):
        """Animate frame transition"""
        if self.animation_running:
            return
             
        self.animation_running = True
         
        # Hide all frames
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame) and widget != frame:
                widget.place_forget()
         
        # Set initial position
        width = self.root.winfo_width()
        if direction == "right":
            frame.place(x=width, y=0, width=width, height=self.root.winfo_height())
            target_x = 0
            start_x = width
        else:  # left
            frame.place(x=-width, y=0, width=width, height=self.root.winfo_height())
            target_x = 0
            start_x = -width
         
        # Animation function
        def animate_step(current_x, step=0):
            new_x = int(start_x + (target_x - start_x) * sin(step/20))
            frame.place(x=new_x, y=0, width=width, height=self.root.winfo_height())
            step += 1
             
            if step <= 20:
                self.root.after(10, lambda: animate_step(new_x, step))
            else:
                frame.place(x=target_x, y=0, relwidth=1, relheight=1)
                self.animation_running = False
                self.current_frame = frame
         
        animate_step(start_x)
     
    def show_login(self):
        """Display the login frame"""
        login_frame = ttk.Frame(self.root, style='TFrame')
         
        # Logo at the top
        logo_frame = ttk.Frame(login_frame, style='TFrame')
        logo_frame.pack(pady=30)
         
        # Create a circular logo
        canvas = tk.Canvas(logo_frame, width=100, height=100, bg=self.secondary_color, highlightthickness=0)
        canvas.create_oval(10, 10, 90, 90, fill=self.primary_color, outline="")
        canvas.create_text(50, 50, text="BMS", fill="white", font=("Helvetica", 24, "bold"))
        canvas.pack()
         
        # Title
        title_label = ttk.Label(login_frame, text="Bank Management System", font=("Helvetica", 24, "bold"), style='TLabel')
        title_label.pack(pady=10)
         
        # Login form
        form_frame = ttk.Frame(login_frame, style='TFrame')
        form_frame.pack(pady=20, padx=50, fill=tk.X)
         
        username_label = ttk.Label(form_frame, text="Username:", style='TLabel')
        username_label.grid(row=0, column=0, sticky=tk.W, pady=5)
         
        username_entry = ttk.Entry(form_frame, width=30)
        username_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
         
        password_label = ttk.Label(form_frame, text="Password:", style='TLabel')
        password_label.grid(row=1, column=0, sticky=tk.W, pady=5)
         
        password_entry = ttk.Entry(form_frame, width=30, show="*")
        password_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
         
        # Error message label
        error_label = ttk.Label(form_frame, text="", foreground=self.error_color, style='TLabel')
        error_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
         
        # Buttons
        button_frame = ttk.Frame(form_frame, style='TFrame')
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
         
        login_button = ttk.Button(button_frame, text="Login", command=lambda: self.login(username_entry.get(), password_entry.get(), error_label))
        login_button.pack(side=tk.LEFT, padx=5)
         
        register_button = ttk.Button(button_frame, text="Register", command=self.show_register)
        register_button.pack(side=tk.LEFT, padx=5)
         
        # Add some demo credentials for testing
        demo_frame = ttk.Frame(login_frame, style='TFrame')
        demo_frame.pack(pady=10)
         
        demo_label = ttk.Label(demo_frame, text="Demo: username 'admin', password 'admin123'", font=("Helvetica", 8), style='TLabel')
        demo_label.pack()
         
        # Display the frame with animation
        self.animate_frame(login_frame)
     
    def login(self, username, password, error_label):
        """Validate login credentials and log user in"""
        if not username or not password:
            error_label.config(text="Username and password are required")
            return
         
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
         
        # Check credentials
        conn = sqlite3.connect('bank_management.db')
        cursor = conn.cursor()
         
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        user = cursor.fetchone()
         
        if user:
            self.current_user = {
                'id': user[0],
                'username': user[1],
                'full_name': user[3],
                'email': user[4],
                'phone': user[5],
                'address': user[6],
                'registration_date': user[7]
            }
            conn.close()
            self.show_dashboard()
        else:
            conn.close()
            error_label.config(text="Invalid username or password")
     
    def show_register(self):
        """Display the registration frame"""
        register_frame = ttk.Frame(self.root, style='TFrame')
         
        # Title
        title_label = ttk.Label(register_frame, text="Create New Account", font=("Helvetica", 24, "bold"), style='TLabel')
        title_label.pack(pady=20)
         
        # Registration form
        form_frame = ttk.Frame(register_frame, style='TFrame')
        form_frame.pack(pady=10, padx=50, fill=tk.X)
         
        # Username
        username_label = ttk.Label(form_frame, text="Username:", style='TLabel')
        username_label.grid(row=0, column=0, sticky=tk.W, pady=5)
         
        username_entry = ttk.Entry(form_frame, width=30)
        username_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
         
        # Password
        password_label = ttk.Label(form_frame, text="Password:", style='TLabel')
        password_label.grid(row=1, column=0, sticky=tk.W, pady=5)
         
        password_entry = ttk.Entry(form_frame, width=30, show="*")
        password_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
         
        # Confirm Password
        conf_password_label = ttk.Label(form_frame, text="Confirm Password:", style='TLabel')
        conf_password_label.grid(row=2, column=0, sticky=tk.W, pady=5)
         
        conf_password_entry = ttk.Entry(form_frame, width=30, show="*")
        conf_password_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
         
        # Full Name
        fullname_label = ttk.Label(form_frame, text="Full Name:", style='TLabel')
        fullname_label.grid(row=3, column=0, sticky=tk.W, pady=5)
         
        fullname_entry = ttk.Entry(form_frame, width=30)
        fullname_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
         
        # Email
        email_label = ttk.Label(form_frame, text="Email:", style='TLabel')
        email_label.grid(row=4, column=0, sticky=tk.W, pady=5)
         
        email_entry = ttk.Entry(form_frame, width=30)
        email_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
         
        # Phone
        phone_label = ttk.Label(form_frame, text="Phone:", style='TLabel')
        phone_label.grid(row=5, column=0, sticky=tk.W, pady=5)
         
        phone_entry = ttk.Entry(form_frame, width=30)
        phone_entry.grid(row=5, column=1, sticky=tk.W, pady=5)
         
        # Address
        address_label = ttk.Label(form_frame, text="Address:", style='TLabel')
        address_label.grid(row=6, column=0, sticky=tk.W, pady=5)
         
        address_entry = ttk.Entry(form_frame, width=30)
        address_entry.grid(row=6, column=1, sticky=tk.W, pady=5)
         
        # Error message label
        error_label = ttk.Label(form_frame, text="", foreground=self.error_color, style='TLabel')
        error_label.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=5)
         
        # Buttons
        button_frame = ttk.Frame(form_frame, style='TFrame')
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
         
        register_button = ttk.Button(
            button_frame, 
            text="Register", 
            command=lambda: self.register_user(
                username_entry.get(),
                password_entry.get(),
                conf_password_entry.get(),
                fullname_entry.get(),
                email_entry.get(),
                phone_entry.get(),
                address_entry.get(),
                error_label
            )
        )
        register_button.pack(side=tk.LEFT, padx=5)
         
        back_button = ttk.Button(button_frame, text="Back to Login", command=self.show_login)
        back_button.pack(side=tk.LEFT, padx=5)
         
        # Display the frame with animation
        self.animate_frame(register_frame, "left")
     
    def register_user(self, username, password, conf_password, fullname, email, phone, address, error_label):
        """Register a new user"""
        # Validate fields
        if not all([username, password, conf_password, fullname, email]):
            error_label.config(text="All fields marked with * are required")
            return
         
        if password != conf_password:
            error_label.config(text="Passwords do not match")
            return
         
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
         
        # Get current date
        registration_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
         
        # Save to database
        try:
            conn = sqlite3.connect('bank_management.db')
            cursor = conn.cursor()
             
            cursor.execute('''
            INSERT INTO users (username, password, full_name, email, phone, address, registration_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, fullname, email, phone, address, registration_date))
             
            conn.commit()
            conn.close()
             
            messagebox.showinfo("Success", "Registration successful. Please login.")
            self.show_login()
        except sqlite3.IntegrityError:
            error_label.config(text="Username or email already exists")
        except Exception as e:
            error_label.config(text=f"Error: {str(e)}")
     
    def show_dashboard(self):
        """Display the main dashboard"""
        dashboard_frame = ttk.Frame(self.root, style='TFrame')
         
        # Create top bar
        top_bar = ttk.Frame(dashboard_frame, style='TFrame')
        top_bar.pack(fill=tk.X, padx=10, pady=10)
         
        # Welcome message
        welcome_label = ttk.Label(top_bar, text=f"Welcome, {self.current_user['full_name']}", font=("Helvetica", 16, "bold"), style='TLabel')
        welcome_label.pack(side=tk.LEFT)
         
        # Logout button
        logout_button = ttk.Button(top_bar, text="Logout", command=self.logout)
        logout_button.pack(side=tk.RIGHT)
         
        # Create sidebar and main content area
        content_frame = ttk.Frame(dashboard_frame, style='TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
         
        sidebar = ttk.Frame(content_frame, width=200, style='TFrame')
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
         
        # Ensure sidebar maintains its width
        sidebar.pack_propagate(False)
         
        # Main content area
        main_content = ttk.Frame(content_frame, style='TFrame')
        main_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
         
        # Add menu buttons to sidebar
        home_btn_frame = self.create_custom_button(sidebar, "Dashboard", lambda: self.load_dashboard_content(main_content), icon="home")
        home_btn_frame.pack(fill=tk.X, pady=5)
         
        accounts_btn_frame = self.create_custom_button(sidebar, "Accounts", lambda: self.load_accounts_content(main_content), icon="account")
        accounts_btn_frame.pack(fill=tk.X, pady=5)
         
        transactions_btn_frame = self.create_custom_button(sidebar, "Transactions", lambda: self.load_transactions_content(main_content), icon="transaction")
        transactions_btn_frame.pack(fill=tk.X, pady=5)
         
        profile_btn_frame = self.create_custom_button(sidebar, "Profile", lambda: self.load_profile_content(main_content), icon="user")
        profile_btn_frame.pack(fill=tk.X, pady=5)
         
        # Load dashboard content by default
        self.load_dashboard_content(main_content)
         
        # Display the frame with animation
        self.animate_frame(dashboard_frame)
     
    def load_dashboard_content(self, parent):
        """Load dashboard overview content"""
        # Clear previous content
        for widget in parent.winfo_children():
            widget.destroy()
         
        # Add title
        title_label = ttk.Label(parent, text="Dashboard Overview", font=("Helvetica", 16, "bold"), style='TLabel')
        title_label.pack(pady=10, anchor=tk.W)
         
        # Create stats section
        stats_frame = ttk.Frame(parent, style='TFrame')
        stats_frame.pack(fill=tk.X, pady=10)
         
        # Fetch account summary
        conn = sqlite3.connect('bank_management.db')
        cursor = conn.cursor()
         
        # Get accounts
        cursor.execute('''
        SELECT id, account_number, account_type, balance, status 
        FROM accounts 
        WHERE user_id = ?
        ''', (self.current_user['id'],))
         
        accounts = cursor.fetchall()
         
        # Get total balance
        total_balance = sum(account[3] for account in accounts)
         
        # Get recent transactions
        cursor.execute('''
        SELECT t.* FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE a.user_id = ?
        ORDER BY t.transaction_date DESC
        LIMIT 5
        ''', (self.current_user['id'],))
         
        recent_transactions = cursor.fetchall()
         
        conn.close()
         
        # Create stats cards
        card_frame = ttk.Frame(stats_frame, style='TFrame')
        card_frame.pack(fill=tk.X)
         
        # Card 1: Total Balance
        balance_card = ttk.Frame(card_frame, style='TFrame')
        balance_card.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
         
        balance_canvas = tk.Canvas(balance_card, width=200, height=100, bg=self.primary_color, highlightthickness=0)
        balance_canvas.pack(fill=tk.BOTH, expand=True)
         
        balance_canvas.create_text(100, 30, text="Total Balance", fill="white", font=("Helvetica", 12))
        balance_canvas.create_text(100, 60, text=f"${total_balance:.2f}", fill="white", font=("Helvetica", 18, "bold"))
         
        # Card 2: Number of Accounts
        accounts_card = ttk.Frame(card_frame, style='TFrame')
        accounts_card.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
         
        accounts_canvas = tk.Canvas(accounts_card, width=200, height=100, bg=self.accent_color, highlightthickness=0)
        accounts_canvas.pack(fill=tk.BOTH, expand=True)
         
        accounts_canvas.create_text(100, 30, text="Total Accounts", fill="white", font=("Helvetica", 12))
        accounts_canvas.create_text(100, 60, text=str(len(accounts)), fill="white", font=("Helvetica", 18, "bold"))
         
        # Card 3: Recent Activity
        activity_card = ttk.Frame(card_frame, style='TFrame')
        activity_card.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
         
        activity_canvas = tk.Canvas(activity_card, width=200, height=100, bg=self.success_color, highlightthickness=0)
        activity_canvas.pack(fill=tk.BOTH, expand=True)
         
        activity_canvas.create_text(100, 30, text="Recent Activity", fill="white", font=("Helvetica", 12))
        activity_canvas.create_text(100, 60, text=f"{len(recent_transactions)} transactions", fill="white", font=("Helvetica", 18, "bold"))
         
        # Quick Actions section
        actions_frame = ttk.Frame(parent, style='TFrame')
        actions_frame.pack(fill=tk.X, pady=20)
         
        actions_label = ttk.Label(actions_frame, text="Quick Actions", font=("Helvetica", 14, "bold"), style='TLabel')
        actions_label.pack(anchor=tk.W, pady=(0, 10))
         
        buttons_frame = ttk.Frame(actions_frame, style='TFrame')
        buttons_frame.pack(fill=tk.X)
         
        new_account_btn = ttk.Button(buttons_frame, text="New Account", command=lambda: self.show_new_account_dialog())
        new_account_btn.pack(side=tk.LEFT, padx=5)
         
        deposit_btn = ttk.Button(buttons_frame, text="Deposit", command=lambda: self.show_deposit_dialog())
        deposit_btn.pack(side=tk.LEFT, padx=5)
         
        withdraw_btn = ttk.Button(buttons_frame, text="Withdraw", command=lambda: self.show_withdraw_dialog())
        withdraw_btn.pack(side=tk.LEFT, padx=5)
         
        transfer_btn = ttk.Button(buttons_frame, text="Transfer", command=lambda: self.show_transfer_dialog())
        transfer_btn.pack(side=tk.LEFT, padx=5)
         
        # Recent Transactions section
        transactions_frame = ttk.Frame(parent, style='TFrame')
        transactions_frame.pack(fill=tk.BOTH, expand=True, pady=10)
         
        transactions_label = ttk.Label(transactions_frame, text="Recent Transactions", font=("Helvetica", 14, "bold"), style='TLabel')
        transactions_label.pack(anchor=tk.W, pady=(0, 10))
         
        # Create a treeview for transactions
        columns = ("date", "type", "amount", "description", "status")
        tree = ttk.Treeview(transactions_frame, columns=columns, show="headings")
         
        # Define headings
        tree.heading("date", text="Date")
        tree.heading("type", text="Type")
        tree.heading("amount", text="Amount")
        tree.heading("description", text="Description")
        tree.heading("status", text="Status")
         
        # Define columns
        tree.column("date", width=150)
        tree.column("type", width=100)
        tree.column("amount", width=100)
        tree.column("description", width=200)
        tree.column("status", width=100)
         
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(transactions_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
         
        # Populate the treeview with transactions
        for transaction in recent_transactions:
            transaction_id = transaction[0]
            transaction_type = transaction[2]
            amount = transaction[3]
            description = transaction[4]
            transaction_date = transaction[5]
            status = transaction[7]
             
            tree.insert("", tk.END, values=(transaction_date, transaction_type, f"${amount:.2f}", description, status))
     
    def load_accounts_content(self, parent):
        """Load accounts management content"""
        # Clear previous content
        for widget in parent.winfo_children():
            widget.destroy()
         
        # Add title
        title_label = ttk.Label(parent, text="Accounts Management", font=("Helvetica", 16, "bold"), style='TLabel')
        title_label.pack(pady=10, anchor=tk.W)
         
        # Create action buttons
        buttons_frame = ttk.Frame(parent, style='TFrame')
        buttons_frame.pack(fill=tk.X, pady=10)
         
        new_account_btn = ttk.Button(buttons_frame, text="New Account", command=lambda: self.show_new_account_dialog())
        new_account_btn.pack(side=tk.LEFT, padx=5)
         
        refresh_btn = ttk.Button(buttons_frame, text="Refresh", command=lambda: self.load_accounts_content(parent))
        refresh_btn.pack(side=tk.LEFT, padx=5)
         
        # Create accounts list
        accounts_frame = ttk.Frame(parent, style='TFrame')
        accounts_frame.pack(fill=tk.BOTH, expand=True, pady=10)
         
        # Create a treeview for accounts
        columns = ("number", "type", "balance", "status", "opening_date")
        tree = ttk.Treeview(accounts_frame, columns=columns, show="headings")
         
        # Define headings
        tree.heading("number", text="Account Number")
        tree.heading("type", text="Type")
        tree.heading("balance", text="Balance")
        tree.heading("status", text="Status")
        tree.heading("opening_date", text="Opening Date")
         
        # Define columns
        tree.column("number", width=150)
        tree.column("type", width=100)
        tree.column("balance", width=100)
        tree.column("status", width=100)
        tree.column("opening_date", width=150)
         
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(accounts_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
         
        # Fetch accounts
        conn = sqlite3.connect('bank_management.db')
        cursor = conn.cursor()
         
        cursor.execute('''
        SELECT id, account_number, account_type, balance, opening_date, status 
        FROM accounts 
        WHERE user_id = ?
        ''', (self.current_user['id'],))
         
        accounts = cursor.fetchall()
        conn.close()
         
        # Populate the treeview with accounts
        for account in accounts:
            account_id = account[0]
            number = account[1]
            account_type = account[2]
            balance = account[3]
            opening_date = account[4]
            status = account[5]
             
            tree.insert("", tk.END, iid=account_id, values=(number, account_type, f"${balance:.2f}", status, opening_date))
         
        # Add right-click menu
        menu = tk.Menu(tree, tearoff=0)
        menu.add_command(label="View Details", command=lambda: self.view_account_details(tree.focus()))
        menu.add_command(label="Deposit", command=lambda: self.show_deposit_dialog(tree.focus()))
        menu.add_command(label="Withdraw", command=lambda: self.show_withdraw_dialog(tree.focus()))
        menu.add_command(label="Close Account", command=lambda: self.close_account(tree.focus()))
         
        def show_menu(event):
            if tree.focus():  # Only show menu if an item is selected
                menu.post(event.x_root, event.y_root)
         
        tree.bind("<Button-3>", show_menu)  # Right-click
        tree.bind("<Double-1>", lambda event: self.view_account_details(tree.focus()))  # Double-click
     
    def load_transactions_content(self, parent):
        """Load transactions history content"""
        # Clear previous content
        for widget in parent.winfo_children():
            widget.destroy()
         
        # Add title
        title_label = ttk.Label(parent, text="Transaction History", font=("Helvetica", 16, "bold"), style='TLabel')
        title_label.pack(pady=10, anchor=tk.W)
         
        # Create filter section
        filter_frame = ttk.Frame(parent, style='TFrame')
        filter_frame.pack(fill=tk.X, pady=10)
         
        # Account filter
        account_label = ttk.Label(filter_frame, text="Account:", style='TLabel')
        account_label.pack(side=tk.LEFT, padx=5)
         
        account_var = tk.StringVar()
        account_var.set("All Accounts")
         
        # Fetch accounts for the dropdown
        conn = sqlite3.connect('bank_management.db')
        cursor = conn.cursor()
         
        cursor.execute('''
        SELECT id, account_number, account_type 
        FROM accounts 
        WHERE user_id = ?
        ''', (self.current_user['id'],))
         
        accounts = cursor.fetchall()
        account_options = ["All Accounts"] + [f"{account[1]} ({account[2]})" for account in accounts]
         
        account_dropdown = ttk.Combobox(filter_frame, textvariable=account_var, values=account_options, state="readonly")
        account_dropdown.pack(side=tk.LEFT, padx=5)
         
        # Type filter
        type_label = ttk.Label(filter_frame, text="Type:", style='TLabel')
        type_label.pack(side=tk.LEFT, padx=5)
         
        type_var = tk.StringVar()
        type_var.set("All Types")
         
        type_options = ["All Types", "Deposit", "Withdrawal", "Transfer"]
        type_dropdown = ttk.Combobox(filter_frame, textvariable=type_var, values=type_options, state="readonly")
        type_dropdown.pack(side=tk.LEFT, padx=5)
         
        # Apply button
        apply_btn = ttk.Button(filter_frame, text="Apply Filter", command=lambda: self.apply_transaction_filters(parent, account_var.get(), type_var.get()))
        apply_btn.pack(side=tk.LEFT, padx=5)
         
        # Create transactions list
        transactions_frame = ttk.Frame(parent, style='TFrame')
        transactions_frame.pack(fill=tk.BOTH, expand=True, pady=10)
         
        # Create a treeview for transactions
        columns = ("date", "account", "type", "amount", "description", "reference", "status")
        tree = ttk.Treeview(transactions_frame, columns=columns, show="headings")
         
        # Define headings
        tree.heading("date", text="Date")
        tree.heading("account", text="Account")
        tree.heading("type", text="Type")
        tree.heading("amount", text="Amount")
        tree.heading("description", text="Description")
        tree.heading("reference", text="Reference")
        tree.heading("status", text="Status")
         
        # Define columns
        tree.column("date", width=150)
        tree.column("account", width=150)
        tree.column("type", width=100)
        tree.column("amount", width=100)
        tree.column("description", width=200)
        tree.column("reference", width=100)
        tree.column("status", width=100)
         
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(transactions_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
         
        # Fetch all transactions for the user
        cursor.execute('''
        SELECT t.*, a.account_number
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE a.user_id = ?
        ORDER BY t.transaction_date DESC
        ''', (self.current_user['id'],))
         
        transactions = cursor.fetchall()
        conn.close()
         
        # Populate the treeview with transactions
        for transaction in transactions:
            transaction_id = transaction[0]
            account_number = transaction[8]
            transaction_type = transaction[2]
            amount = transaction[3]
            description = transaction[4]
            transaction_date = transaction[5]
            reference = transaction[6]
            status = transaction[7]
             
            tree.insert("", tk.END, iid=transaction_id, values=(transaction_date, account_number, transaction_type, f"${amount:.2f}", description, reference, status))
         
        # Add double-click to view details
        tree.bind("<Double-1>", lambda event: self.view_transaction_details(tree.focus()))
     
    def apply_transaction_filters(self, parent, account_filter, type_filter):
        """Apply filters to transaction history"""
        # Reload the content with filters
        self.load_transactions_content(parent)  # This is a simplified version, in reality you'd modify the query
     
    def load_profile_content(self, parent):
        """Load user profile content"""
        # Clear previous content
        for widget in parent.winfo_children():
            widget.destroy()
         
        # Add title
        title_label = ttk.Label(parent, text="User Profile", font=("Helvetica", 16, "bold"), style='TLabel')
        title_label.pack(pady=10, anchor=tk.W)
         
        # Create profile section
        profile_frame = ttk.Frame(parent, style='TFrame')
        profile_frame.pack(fill=tk.BOTH, expand=True, pady=10)
         
        # Profile picture frame
        pic_frame = ttk.Frame(profile_frame, style='TFrame')
        pic_frame.pack(side=tk.LEFT, padx=20, pady=20)
         
        # Create a circular avatar
        canvas = tk.Canvas(pic_frame, width=120, height=120, bg=self.secondary_color, highlightthickness=0)
        canvas.create_oval(10, 10, 110, 110, fill=self.primary_color, outline="")
        canvas.create_text(60, 60, text=self.current_user['full_name'][0].upper(), fill="white", font=("Helvetica", 36, "bold"))
        canvas.pack()
         
        # User info section
        info_frame = ttk.Frame(profile_frame, style='TFrame')
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
         
        # Full Name
        name_label = ttk.Label(info_frame, text="Full Name:", font=("Helvetica", 10, "bold"), style='TLabel')
        name_label.grid(row=0, column=0, sticky=tk.W, pady=5)
         
        name_value = ttk.Label(info_frame, text=self.current_user['full_name'], style='TLabel')
        name_value.grid(row=0, column=1, sticky=tk.W, pady=5)
         
        # Username
        username_label = ttk.Label(info_frame, text="Username:", font=("Helvetica", 10, "bold"), style='TLabel')
        username_label.grid(row=1, column=0, sticky=tk.W, pady=5)
         
        username_value = ttk.Label(info_frame, text=self.current_user['username'], style='TLabel')
        username_value.grid(row=1, column=1, sticky=tk.W, pady=5)
         
        # Email
        email_label = ttk.Label(info_frame, text="Email:", font=("Helvetica", 10, "bold"), style='TLabel')
        email_label.grid(row=2, column=0, sticky=tk.W, pady=5)
         
        email_value = ttk.Label(info_frame, text=self.current_user['email'], style='TLabel')
        email_value.grid(row=2, column=1, sticky=tk.W, pady=5)
         
        # Phone
        phone_label = ttk.Label(info_frame, text="Phone:", font=("Helvetica", 10, "bold"), style='TLabel')
        phone_label.grid(row=3, column=0, sticky=tk.W, pady=5)
         
        phone_value = ttk.Label(info_frame, text=self.current_user['phone'] or "Not provided", style='TLabel')
        phone_value.grid(row=3, column=1, sticky=tk.W, pady=5)
         
        # Address
        address_label = ttk.Label(info_frame, text="Address:", font=("Helvetica", 10, "bold"), style='TLabel')
        address_label.grid(row=4, column=0, sticky=tk.W, pady=5)
         
        address_value = ttk.Label(info_frame, text=self.current_user['address'] or "Not provided", style='TLabel')
        address_value.grid(row=4, column=1, sticky=tk.W, pady=5)
         
        # Registration Date
        reg_date_label = ttk.Label(info_frame, text="Registration Date:", font=("Helvetica", 10, "bold"), style='TLabel')
        reg_date_label.grid(row=5, column=0, sticky=tk.W, pady=5)
         
        reg_date_value = ttk.Label(info_frame, text=self.current_user['registration_date'], style='TLabel')
        reg_date_value.grid(row=5, column=1, sticky=tk.W, pady=5)
         
        # Edit profile button
        edit_button = ttk.Button(info_frame, text="Edit Profile", command=self.show_edit_profile_dialog)
        edit_button.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=20)
         
        # Change password button
        change_pwd_button = ttk.Button(info_frame, text="Change Password", command=self.show_change_password_dialog)
        change_pwd_button.grid(row=6, column=1, sticky=tk.E, pady=20)
     
    def show_new_account_dialog(self):
        """Show dialog to create a new account"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Account")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
         
        # Create form
        form_frame = ttk.Frame(dialog)
        form_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
         
        # Account Type
        type_label = ttk.Label(form_frame, text="Account Type:")
        type_label.grid(row=0, column=0, sticky=tk.W, pady=10)
         
        type_var = tk.StringVar()
        type_var.set("Savings")
         
        type_options = ["Savings", "Checking", "Fixed Deposit", "Loan"]
        type_dropdown = ttk.Combobox(form_frame, textvariable=type_var, values=type_options, state="readonly")
        type_dropdown.grid(row=0, column=1, sticky=tk.W, pady=10)
         
        # Initial Deposit
        deposit_label = ttk.Label(form_frame, text="Initial Deposit:")
        deposit_label.grid(row=1, column=0, sticky=tk.W, pady=10)
         
        deposit_entry = ttk.Entry(form_frame)
        deposit_entry.grid(row=1, column=1, sticky=tk.W, pady=10)
        deposit_entry.insert(0, "0.00")
         
        # Description
        desc_label = ttk.Label(form_frame, text="Description (Optional):")
        desc_label.grid(row=2, column=0, sticky=tk.W, pady=10)
         
        desc_entry = ttk.Entry(form_frame)
        desc_entry.grid(row=2, column=1, sticky=tk.W, pady=10)
         
        # Error message label
        error_label = ttk.Label(form_frame, text="", foreground=self.error_color)
        error_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)
         
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
         
        create_button = ttk.Button(
            button_frame, 
            text="Create Account", 
            command=lambda: self.create_new_account(
                type_var.get(),
                deposit_entry.get(),
                desc_entry.get(),
                error_label,
                dialog
            )
        )
        create_button.pack(side=tk.LEFT, padx=5)
         
        cancel_button = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
     
    def create_new_account(self, account_type, initial_deposit, description, error_label, dialog):
        """Create a new bank account"""
        try:
            # Validate initial deposit
            initial_deposit = float(initial_deposit)
            if initial_deposit < 0:
                error_label.config(text="Initial deposit cannot be negative")
                return
             
            # Generate account number
            account_number = f"{random.randint(10000, 99999)}-{random.randint(10000, 99999)}"
             
            # Get current date
            opening_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
             
            # Save to database
            conn = sqlite3.connect('bank_management.db')
            cursor = conn.cursor()
             
            cursor.execute('''
            INSERT INTO accounts (user_id, account_number, account_type, balance, opening_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.current_user['id'], account_number, account_type, initial_deposit, opening_date, "active"))
             
            # Get the new account ID
            account_id = cursor.lastrowid
             
            # If there's an initial deposit, create a transaction
            if initial_deposit > 0:
                reference_number = f"DEP-{random.randint(1000000, 9999999)}"
                 
                cursor.execute('''
                INSERT INTO transactions (account_id, transaction_type, amount, description, transaction_date, reference_number, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (account_id, "Deposit", initial_deposit, "Initial deposit", opening_date, reference_number, "completed"))
             
            conn.commit()
            conn.close()
             
            messagebox.showinfo("Success", f"New {account_type} account created successfully!")
            dialog.destroy()
             
            # Refresh the accounts view if it's open
            if self.current_frame:
                main_content = None
                for widget in self.current_frame.winfo_children():
                    if isinstance(widget, ttk.Frame) and widget.winfo_children():
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Frame) and child.winfo_width() > 200:
                                main_content = child
                                break
                 
                if main_content:
                    self.load_accounts_content(main_content)
        except ValueError:
            error_label.config(text="Please enter a valid amount for initial deposit")
        except Exception as e:
            error_label.config(text=f"Error: {str(e)}")
     
    def show_deposit_dialog(self, account_id=None):
        """Show dialog to make a deposit"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Make a Deposit")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
         
        # Create form
        form_frame = ttk.Frame(dialog)
        form_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
         
        # Account selection
        account_label = ttk.Label(form_frame, text="Select Account:")
        account_label.grid(row=0, column=0, sticky=tk.W, pady=10)
         
        # Fetch accounts
        conn = sqlite3.connect('bank_management.db')
        cursor = conn.cursor()
         
        cursor.execute('''
        SELECT id, account_number, account_type, balance 
        FROM accounts 
        WHERE user_id = ? AND status = 'active'
        ''', (self.current_user['id'],))
         
        accounts = cursor.fetchall()
        conn.close()
         
        account_var = tk.StringVar()
        account_options = [f"{account[1]} ({account[2]}) - ${account[3]:.2f}" for account in accounts]
        account_ids = [account[0] for account in accounts]
         
        if account_id and account_id in account_ids:
            index = account_ids.index(account_id)
            account_var.set(account_options[index])
        elif account_options:
            account_var.set(account_options[0])
         
        account_dropdown = ttk.Combobox(form_frame, textvariable=account_var, values=account_options, state="readonly")
        account_dropdown.grid(row=0, column=1, sticky=tk.W, pady=10)
         
        # Amount
        amount_label = ttk.Label(form_frame, text="Amount:")
        amount_label.grid(row=1, column=0, sticky=tk.W, pady=10)
         
        amount_entry = ttk.Entry(form_frame)
        amount_entry.grid(row=1, column=1, sticky=tk.W, pady=10)
         
        # Description
        desc_label = ttk.Label(form_frame, text="Description (Optional):")
        desc_label.grid(row=2, column=0, sticky=tk.W, pady=10)
         
        desc_entry = ttk.Entry(form_frame)
        desc_entry.grid(row=2, column=1, sticky=tk.W, pady=10)
         
        # Error message label
        error_label = ttk.Label(form_frame, text="", foreground=self.error_color)
        error_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)
         
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
         
        deposit_button = ttk.Button(
            button_frame, 
            text="Make Deposit", 
            command=lambda: self.make_deposit(
                account_var.get(),
                amount_entry.get(),
                desc_entry.get(),
                error_label,
                dialog,
                account_ids,
                account_options
            )
        )
        deposit_button.pack(side=tk.LEFT, padx=5)
         
        cancel_button = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
     
    def make_deposit(self, account_option, amount, description, error_label, dialog, account_ids, account_options):
        """Process a deposit transaction"""
        try:
            # Validate amount
            amount = float(amount)
            if amount <= 0:
                error_label.config(text="Amount must be positive")
                return
             
            # Get account ID
            account_index = account_options.index(account_option)
            account_id = account_ids[account_index]
             
            # Set default description if none provided
            if not description:
                description = "Deposit"
             
            # Generate reference number
            reference_number = f"DEP-{random.randint(1000000, 9999999)}"
             
            # Get current date
            transaction_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
             
            # Update database
            conn = sqlite3.connect('bank_management.db')
            cursor = conn.cursor()
             
            # Add transaction
            cursor.execute('''
            INSERT INTO transactions (account_id, transaction_type, amount, description, transaction_date, reference_number, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (account_id, "Deposit", amount, description, transaction_date, reference_number, "completed"))
             
            # Update account balance
            cursor.execute('''
            UPDATE accounts SET balance = balance + ? WHERE id = ?
            ''', (amount, account_id))
             
            conn.commit()
            conn.close()
             
            messagebox.showinfo("Success", f"Deposit of ${amount:.2f} completed successfully!")
            dialog.destroy()
             
            # Refresh the relevant view if it's open
            if self.current_frame:
                main_content = None
                for widget in self.current_frame.winfo_children():
                    if isinstance(widget, ttk.Frame) and widget.winfo_children():
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Frame) and child.winfo_width() > 200:
                                main_content = child
                                break
                 
                if main_content:
                    # Try to determine which view is open and refresh it
                    title_widget = None
                    for widget in main_content.winfo_children():
                        if isinstance(widget, ttk.Label) and widget.cget("text") in ["Dashboard Overview", "Accounts Management", "Transaction History"]:
                            title_widget = widget
                            break
                     
                    if title_widget:
                        if title_widget.cget("text") == "Dashboard Overview":
                            self.load_dashboard_content(main_content)
                        elif title_widget.cget("text") == "Accounts Management":
                            self.load_accounts_content(main_content)
                        elif title_widget.cget("text") == "Transaction History":
                            self.load_transactions_content(main_content)
        except ValueError:
            error_label.config(text="Please enter a valid amount")
        except Exception as e:
            error_label.config(text=f"Error: {str(e)}")
     
    def show_withdraw_dialog(self, account_id=None):
        """Show dialog to make a withdrawal"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Make a Withdrawal")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
         
        # Create form
        form_frame = ttk.Frame(dialog)
        form_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
         
        # Account selection
        account_label = ttk.Label(form_frame, text="Select Account:")
        account_label.grid(row=0, column=0, sticky=tk.W, pady=10)
         
        # Fetch accounts
        conn = sqlite3.connect('bank_management.db')
        cursor = conn.cursor()
         
        cursor.execute('''
        SELECT id, account_number, account_type, balance 
        FROM accounts 
        WHERE user_id = ? AND status = 'active'
        ''', (self.current_user['id'],))
         
        accounts = cursor.fetchall()
        conn.close()
         
        account_var = tk.StringVar()
        account_options = [f"{account[1]} ({account[2]}) - ${account[3]:.2f}" for account in accounts]
        account_ids = [account[0] for account in accounts]
         
        if account_id and account_id in account_ids:
            index = account_ids.index(account_id)
            account_var.set(account_options[index])
        elif account_options:
            account_var.set(account_options[0])
         
        account_dropdown = ttk.Combobox(form_frame, textvariable=account_var, values=account_options, state="readonly")
        account_dropdown.grid(row=0, column=1, sticky=tk.W, pady=10)
         
        # Amount
        amount_label = ttk.Label(form_frame, text="Amount:")
        amount_label.grid(row=1, column=0, sticky=tk.W, pady=10)
         
        amount_entry = ttk.Entry(form_frame)
        amount_entry.grid(row=1, column=1, sticky=tk.W, pady=10)
         
        # Description
        desc_label = ttk.Label(form_frame, text="Description (Optional):")
        desc_label.grid(row=2, column=0, sticky=tk.W, pady=10)
         
        desc_entry = ttk.Entry(form_frame)
        desc_entry.grid(row=2, column=1, sticky=tk.W, pady=10)
         
        # Error message label
        error_label = ttk.Label(form_frame, text="", foreground=self.error_color)
        error_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)
         
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
         
        withdraw_button = ttk.Button(
            button_frame, 
            text="Make Withdrawal", 
            command=lambda: self.make_withdrawal(
                account_var.get(),
                amount_entry.get(),
                desc_entry.get(),
                error_label,
                dialog,
                account_ids,
                account_options,
                accounts
            )
        )
        withdraw_button.pack(side=tk.LEFT, padx=5)
         
        cancel_button = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
     
    def make_withdrawal(self, account_option, amount, description, error_label, dialog, account_ids, account_options, accounts):
        """Process a withdrawal transaction"""
        try:
            # Validate amount
            amount = float(amount)
            if amount <= 0:
                error_label.config(text="Amount must be positive")
                return
             
            # Get account ID and balance
            account_index = account_options.index(account_option)
            account_id = account_ids[account_index]
            account_balance = accounts[account_index][3]
             
            # Check if sufficient balance
            if amount > account_balance:
                error_label.config(text="Insufficient balance")
                return
             
            # Set default description if none provided
            if not description:
                description = "Withdrawal"
             
            # Generate reference number
            reference_number = f"WDR-{random.randint(1000000, 9999999)}"
             
            # Get current date
            transaction_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
             
            # Update database
            conn = sqlite3.connect('bank_management.db')
            cursor = conn.cursor()
             
            # Add transaction
            cursor.execute('''
            INSERT INTO transactions (account_id, transaction_type, amount, description, transaction_date, reference_number, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (account_id, "Withdrawal", amount, description, transaction_date, reference_number, "completed"))
             
            # Update account balance
            cursor.execute('''
            UPDATE accounts SET balance = balance - ? WHERE id = ?
            ''', (amount, account_id))
             
            conn.commit()
            conn.close()
             
            messagebox.showinfo("Success", f"Withdrawal of ${amount:.2f} completed successfully!")
            dialog.destroy()
             
            # Refresh the relevant view if it's open
            if self.current_frame:
                main_content = None
                for widget in self.current_frame.winfo_children():
                    if isinstance(widget, ttk.Frame) and widget.winfo_children():
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Frame) and child.winfo_width() > 200:
                                main_content = child
                                break
                 
                if main_content:
                    # Try to determine which view is open and refresh it
                    title_widget = None
                    for widget in main_content.winfo_children():
                        if isinstance(widget, ttk.Label) and widget.cget("text") in ["Dashboard Overview", "Accounts Management", "Transaction History"]:
                            title_widget = widget
                            break
                     
                    if title_widget:
                        if title_widget.cget("text") == "Dashboard Overview":
                            self.load_dashboard_content(main_content)
                        elif title_widget.cget("text") == "Accounts Management":
                            self.load_accounts_content(main_content)
                        elif title_widget.cget("text") == "Transaction History":
                            self.load_transactions_content(main_content)
        except ValueError:
            error_label.config(text="Please enter a valid amount")
        except Exception as e:
            error_label.config(text=f"Error: {str(e)}")
     
    def show_transfer_dialog(self):
        """Show dialog to make a transfer between accounts"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Transfer Funds")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
         
        # Create form
        form_frame = ttk.Frame(dialog)
        form_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
         
        # Fetch accounts
        conn = sqlite3.connect('bank_management.db')
        cursor = conn.cursor()
         
        cursor.execute('''
        SELECT id, account_number, account_type, balance 
        FROM accounts 
        WHERE user_id = ? AND status = 'active'
        ''', (self.current_user['id'],))
         
        accounts = cursor.fetchall()
        conn.close()
         
        account_options = [f"{account[1]} ({account[2]}) - ${account[3]:.2f}" for account in accounts]
        account_ids = [account[0] for account in accounts]
         
        # From Account
        from_label = ttk.Label(form_frame, text="From Account:")
        from_label.grid(row=0, column=0, sticky=tk.W, pady=10)
         
        from_var = tk.StringVar()
        if account_options:
            from_var.set(account_options[0])
         
        from_dropdown = ttk.Combobox(form_frame, textvariable=from_var, values=account_options, state="readonly")
        from_dropdown.grid(row=0, column=1, sticky=tk.W, pady=10)
         
        # To Account
        to_label = ttk.Label(form_frame, text="To Account:")
        to_label.grid(row=1, column=0, sticky=tk.W, pady=10)
         
        to_var = tk.StringVar()
        if len(account_options) > 1:
            to_var.set(account_options[1])
        elif account_options:
            to_var.set(account_options[0])
         
        to_dropdown = ttk.Combobox(form_frame, textvariable=to_var, values=account_options, state="readonly")
        to_dropdown.grid(row=1, column=1, sticky=tk.W, pady=10)
         
        # Amount
        amount_label = ttk.Label(form_frame, text="Amount:")
        amount_label.grid(row=2, column=0, sticky=tk.W, pady=10)
         
        amount_entry = ttk.Entry(form_frame)
        amount_entry.grid(row=2, column=1, sticky=tk.W, pady=10)
         
        # Description
        desc_label = ttk.Label(form_frame, text="Description (Optional):")
        desc_label.grid(row=3, column=0, sticky=tk.W, pady=10)
         
        desc_entry = ttk.Entry(form_frame)
        desc_entry.grid(row=3, column=1, sticky=tk.W, pady=10)
         
        # Error message label
        error_label = ttk.Label(form_frame, text="", foreground=self.error_color)
        error_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=10)
         
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
         
        transfer_button = ttk.Button(
            button_frame, 
            text="Transfer Funds", 
            command=lambda: self.make_transfer(
                from_var.get(),
                to_var.get(),
                amount_entry.get(),
                desc_entry.get(),
                error_label,
                dialog,
                account_ids,
                account_options,
                accounts
            )
        )
        transfer_button.pack(side=tk.LEFT, padx=5)
         
        cancel_button = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
     
    def make_transfer(self, from_account, to_account, amount, description, error_label, dialog, account_ids, account_options, accounts):
        """Process a transfer between accounts"""
        try:
            # Validate amount
            amount = float(amount)
            if amount <= 0:
                error_label.config(text="Amount must be positive")
                return
             
            # Get account IDs and balances
            from_index = account_options.index(from_account)
            from_id = account_ids[from_index]
            from_balance = accounts[from_index][3]
             
            to_index = account_options.index(to_account)
            to_id = account_ids[to_index]
             
            # Check if accounts are different
            if from_id == to_id:
                error_label.config(text="Cannot transfer to the same account")
                return
             
            # Check if sufficient balance
            if amount > from_balance:
                error_label.config(text="Insufficient balance")
                return
             
            # Set default description if none provided
            if not description:
                description = "Transfer between accounts"
             
            # Generate reference number
            reference_number = f"TRF-{random.randint(1000000, 9999999)}"
             
            # Get current date
            transaction_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
             
            # Update database
            conn = sqlite3.connect('bank_management.db')
            cursor = conn.cursor()
             
            # Add withdrawal transaction
            cursor.execute('''
            INSERT INTO transactions (account_id, transaction_type, amount, description, transaction_date, reference_number, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (from_id, "Transfer (Out)", amount, description, transaction_date, reference_number, "completed"))
             
            # Add deposit transaction
            cursor.execute('''
            INSERT INTO transactions (account_id, transaction_type, amount, description, transaction_date, reference_number, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (to_id, "Transfer (In)", amount, description, transaction_date, reference_number, "completed"))
             
            # Update account balances
            cursor.execute('''
            UPDATE accounts SET balance = balance - ? WHERE id = ?
            ''', (amount, from_id))
             
            cursor.execute('''
            UPDATE accounts SET balance = balance + ? WHERE id = ?
            ''', (amount, to_id))
             
            conn.commit()
            conn.close()
             
            messagebox.showinfo("Success", f"Transfer of ${amount:.2f} completed successfully!")
            dialog.destroy()
             
            # Refresh the relevant view if it's open
            if self.current_frame:
                main_content = None
                for widget in self.current_frame.winfo_children():
                    if isinstance(widget, ttk.Frame) and widget.winfo_children():
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Frame) and child.winfo_width() > 200:
                                main_content = child
                                break
                 
                if main_content:
                    # Try to determine which view is open and refresh it
                    title_widget = None
                    for widget in main_content.winfo_children():
                        if isinstance(widget, ttk.Label) and widget.cget("text") in ["Dashboard Overview", "Accounts Management", "Transaction History"]:
                            title_widget = widget
                            break
                     
                    if title_widget:
                        if title_widget.cget("text") == "Dashboard Overview":
                            self.load_dashboard_content(main_content)
                        elif title_widget.cget("text") == "Accounts Management":
                            self.load_accounts_content(main_content)
                        elif title_widget.cget("text") == "Transaction History":
                            self.load_transactions_content(main_content)
        except ValueError:
            error_label.config(text="Please enter a valid amount")
        except Exception as e:
            error_label.config(text=f"Error: {str(e)}")
     
    def view_account_details(self, account_id):
        """Show detailed view of an account"""
        if not account_id:
            return
         
        # Fetch account details
        conn = sqlite3.connect('bank_management.db')
        cursor = conn.cursor()
         
        cursor.execute('''
        SELECT * FROM accounts WHERE id = ?
        ''', (account_id,))
         
        account = cursor.fetchone()
         
        if not account:
            conn.close()
            return
         
        # Fetch recent transactions
        cursor.execute('''
        SELECT * FROM transactions 
        WHERE account_id = ? 
        ORDER BY transaction_date DESC 
        LIMIT 10
        ''', (account_id,))
         
        transactions = cursor.fetchall()
        conn.close()
         
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Account Details - {account[2]}")
        dialog.geometry("600x500")
        dialog.resizable(True, True)
        dialog.transient(self.root)
         
        # Account details section
        details_frame = ttk.Frame(dialog)
        details_frame.pack(fill=tk.X, padx=20, pady=20)
         
        # Account number
        number_label = ttk.Label(details_frame, text="Account Number:", font=("Helvetica", 10, "bold"))
        number_label.grid(row=0, column=0, sticky=tk.W, pady=5)
         
        number_value = ttk.Label(details_frame, text=account[2])
        number_value.grid(row=0, column=1, sticky=tk.W, pady=5)
         
        # Account type
        type_label = ttk.Label(details_frame, text="Account Type:", font=("Helvetica", 10, "bold"))
        type_label.grid(row=1, column=0, sticky=tk.W, pady=5)
         
        type_value = ttk.Label(details_frame, text=account[3])
        type_value.grid(row=1, column=1, sticky=tk.W, pady=5)
         
        # Balance
        balance_label = ttk.Label(details_frame, text="Current Balance:", font=("Helvetica", 10, "bold"))
        balance_label.grid(row=2, column=0, sticky=tk.W, pady=5)
         
        balance_value = ttk.Label(details_frame, text=f"${account[4]:.2f}")
        balance_value.grid(row=2, column=1, sticky=tk.W, pady=5)
         
        # Opening date
        opening_label = ttk.Label(details_frame, text="Opening Date:", font=("Helvetica", 10, "bold"))
        opening_label.grid(row=3, column=0, sticky=tk.W, pady=5)
         
        opening_value = ttk.Label(details_frame, text=account[5])
        opening_value.grid(row=3, column=1, sticky=tk.W, pady=5)
         
        # Status
        status_label = ttk.Label(details_frame, text="Status:", font=("Helvetica", 10, "bold"))
        status_label.grid(row=4, column=0, sticky=tk.W, pady=5)
         
        status_value = ttk.Label(details_frame, text=account[6].capitalize())
        status_value.grid(row=4, column=1, sticky=tk.W, pady=5)
         
        # Buttons
        button_frame = ttk.Frame(details_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
         
        deposit_button = ttk.Button(button_frame, text="Deposit", command=lambda: self.show_deposit_dialog(account_id))
        deposit_button.grid(row=0, column=0, padx=5)
         
        withdraw_button = ttk.Button(button_frame, text="Withdraw", command=lambda: self.show_withdraw_dialog(account_id))
        withdraw_button.grid(row=0, column=1, padx=5)
         
        # Transactions section
        transactions_label = ttk.Label(dialog, text="Recent Transactions", font=("Helvetica", 12, "bold"))
        transactions_label.pack(anchor=tk.W, padx=20, pady=(10, 5))
         
        # Create a treeview for transactions
        transactions_frame = ttk.Frame(dialog)
        transactions_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
         
        columns = ("date", "type", "amount", "description", "reference", "status")
        tree = ttk.Treeview(transactions_frame, columns=columns, show="headings")
         
        # Define headings
        tree.heading("date", text="Date")
        tree.heading("type", text="Type")
        tree.heading("amount", text="Amount")
        tree.heading("description", text="Description")
        tree.heading("reference", text="Reference")
        tree.heading("status", text="Status")
         
        # Define columns
        tree.column("date", width=120)
        tree.column("type", width=100)
        tree.column("amount", width=80)
        tree.column("description", width=150)
        tree.column("reference", width=80)
        tree.column("status", width=80)
         
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(transactions_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
         
        # Populate the treeview with transactions
        for transaction in transactions:
            transaction_id = transaction[0]
            transaction_type = transaction[2]
            amount = transaction[3]
            description = transaction[4]
            transaction_date = transaction[5]
            reference = transaction[6]
            status = transaction[7]
             
            tree.insert("", tk.END, iid=transaction_id, values=(transaction_date, transaction_type, f"${amount:.2f}", description, reference, status))
     
    def view_transaction_details(self, transaction_id):
        """Show detailed view of a transaction"""
        if not transaction_id:
            return
         
        # Fetch transaction details
        conn = sqlite3.connect('bank_management.db')
        cursor = conn.cursor()
         
        cursor.execute('''
        SELECT t.*, a.account_number, a.account_type 
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE t.id = ?
        ''', (transaction_id,))
         
        transaction = cursor.fetchone()
        conn.close()
         
        if not transaction:
            return
         
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Transaction Details - {transaction[6]}")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.transient(self.root)
         
        # Transaction details section
        details_frame = ttk.Frame(dialog)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
         
        # Reference number
        ref_label = ttk.Label(details_frame, text="Reference Number:", font=("Helvetica", 10, "bold"))
        ref_label.grid(row=0, column=0, sticky=tk.W, pady=5)
         
        ref_value = ttk.Label(details_frame, text=transaction[6])
        ref_value.grid(row=0, column=1, sticky=tk.W, pady=5)
         
        # Account
        account_label = ttk.Label(details_frame, text="Account:", font=("Helvetica", 10, "bold"))
        account_label.grid(row=1, column=0, sticky=tk.W, pady=5)
         
        account_value = ttk.Label(details_frame, text=f"{transaction[8]} ({transaction[9]})")
        account_value.grid(row=1, column=1, sticky=tk.W, pady=5)
         
        # Type
        type_label = ttk.Label(details_frame, text="Transaction Type:", font=("Helvetica", 10, "bold"))
        type_label.grid(row=2, column=0, sticky=tk.W, pady=5)
         
        type_value = ttk.Label(details_frame, text=transaction[2])
        type_value.grid(row=2, column=1, sticky=tk.W, pady=5)
         
        # Amount
        amount_label = ttk.Label(details_frame, text="Amount:", font=("Helvetica", 10, "bold"))
        amount_label.grid(row=3, column=0, sticky=tk.W, pady=5)
         
        amount_value = ttk.Label(details_frame, text=f"${transaction[3]:.2f}")
        amount_value.grid(row=3, column=1, sticky=tk.W, pady=5)
         
        # Description
        desc_label = ttk.Label(details_frame, text="Description:", font=("Helvetica", 10, "bold"))
        desc_label.grid(row=4, column=0, sticky=tk.W, pady=5)
         
        desc_value = ttk.Label(details_frame, text=transaction[4] or "N/A")
        desc_value.grid(row=4, column=1, sticky=tk.W, pady=5)
         
        # Date
        date_label = ttk.Label(details_frame, text="Date:", font=("Helvetica", 10, "bold"))
        date_label.grid(row=5, column=0, sticky=tk.W, pady=5)
         
        date_value = ttk.Label(details_frame, text=transaction[5])
        date_value.grid(row=5, column=1, sticky=tk.W, pady=5)
         
        # Status
        status_label = ttk.Label(details_frame, text="Status:", font=("Helvetica", 10, "bold"))
        status_label.grid(row=6, column=0, sticky=tk.W, pady=5)
         
        status_value = ttk.Label(details_frame, text=transaction[7].capitalize())
        status_value.grid(row=6, column=1, sticky=tk.W, pady=5)
         
        # Close button
        close_button = ttk.Button(details_frame, text="Close", command=dialog.destroy)
        close_button.grid(row=7, column=0, columnspan=2, pady=20)
     
    def close_account(self, account_id):
        """Close an account"""
        if not account_id:
            return
         
        # Ask for confirmation
        if not messagebox.askyesno("Confirm", "Are you sure you want to close this account? This cannot be undone."):
            return
         
        # Check if account has balance
        conn = sqlite3.connect('bank_management.db')
        cursor = conn.cursor()
         
        cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
        balance = cursor.fetchone()[0]
         
        if balance > 0:
            if not messagebox.askyesno("Warning", f"This account has a balance of ${balance:.2f}. Do you want to proceed?"):
                conn.close()
                return
         
        # Update account status
        cursor.execute("UPDATE accounts SET status = 'closed' WHERE id = ?", (account_id,))
        conn.commit()
        conn.close()
         
        messagebox.showinfo("Success", "Account closed successfully")
         
        # Refresh the accounts view if it's open
        if self.current_frame:
            main_content = None
            for widget in self.current_frame.winfo_children():
                if isinstance(widget, ttk.Frame) and widget.winfo_children():
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Frame) and child.winfo_width() > 200:
                            main_content = child
                            break
             
            if main_content:
                title_widget = None
                for widget in main_content.winfo_children():
                    if isinstance(widget, ttk.Label) and widget.cget("text") == "Accounts Management":
                        title_widget = widget
                        break
                 
                if title_widget:
                    self.load_accounts_content(main_content)
     
    def show_edit_profile_dialog(self):
        """Show dialog to edit user profile"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Profile")
        dialog.geometry("400x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
         
        # Create form
        form_frame = ttk.Frame(dialog)
        form_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
         
        # Full Name
        name_label = ttk.Label(form_frame, text="Full Name:")
        name_label.grid(row=0, column=0, sticky=tk.W, pady=10)
         
        name_entry = ttk.Entry(form_frame, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=10)
        name_entry.insert(0, self.current_user['full_name'])
         
        # Email
        email_label = ttk.Label(form_frame, text="Email:")
        email_label.grid(row=1, column=0, sticky=tk.W, pady=10)
         
        email_entry = ttk.Entry(form_frame, width=30)
        email_entry.grid(row=1, column=1, sticky=tk.W, pady=10)
        email_entry.insert(0, self.current_user['email'])
         
        # Phone
        phone_label = ttk.Label(form_frame, text="Phone:")
        phone_label.grid(row=2, column=0, sticky=tk.W, pady=10)
         
        phone_entry = ttk.Entry(form_frame, width=30)
        phone_entry.grid(row=2, column=1, sticky=tk.W, pady=10)
        phone_entry.insert(0, self.current_user['phone'] or "")
         
        # Address
        address_label = ttk.Label(form_frame, text="Address:")
        address_label.grid(row=3, column=0, sticky=tk.W, pady=10)
         
        address_entry = ttk.Entry(form_frame, width=30)
        address_entry.grid(row=3, column=1, sticky=tk.W, pady=10)
        address_entry.insert(0, self.current_user['address'] or "")
         
        # Error message label
        error_label = ttk.Label(form_frame, text="", foreground=self.error_color)
        error_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=10)
         
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
         
        save_button = ttk.Button(
            button_frame, 
            text="Save Changes", 
            command=lambda: self.update_profile(
                name_entry.get(),
                email_entry.get(),
                phone_entry.get(),
                address_entry.get(),
                error_label,
                dialog
            )
        )
        save_button.pack(side=tk.LEFT, padx=5)
         
        cancel_button = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
     
    def update_profile(self, full_name, email, phone, address, error_label, dialog):
        """Update user profile information"""
        try:
            # Validate fields
            if not full_name or not email:
                error_label.config(text="Full Name and Email are required")
                return
             
            # Update database
            conn = sqlite3.connect('bank_management.db')
            cursor = conn.cursor()
             
            cursor.execute('''
            UPDATE users SET full_name = ?, email = ?, phone = ?, address = ?
            WHERE id = ?
            ''', (full_name, email, phone, address, self.current_user['id']))
             
            conn.commit()
            conn.close()
             
            # Update current user information
            self.current_user['full_name'] = full_name
            self.current_user['email'] = email
            self.current_user['phone'] = phone
            self.current_user['address'] = address
             
            messagebox.showinfo("Success", "Profile updated successfully")
            dialog.destroy()
             
            # Refresh the profile view if it's open
            if self.current_frame:
                main_content = None
                for widget in self.current_frame.winfo_children():
                    if isinstance(widget, ttk.Frame) and widget.winfo_children():
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Frame) and child.winfo_width() > 200:
                                main_content = child
                                break
                 
                if main_content:
                    title_widget = None
                    for widget in main_content.winfo_children():
                        if isinstance(widget, ttk.Label) and widget.cget("text") == "User Profile":
                            title_widget = widget
                            break
                     
                    if title_widget:
                        self.load_profile_content(main_content)
        except Exception as e:
            error_label.config(text=f"Error: {str(e)}")
     
    def show_change_password_dialog(self):
        """Show dialog to change password"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Password")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
         
        # Create form
        form_frame = ttk.Frame(dialog)
        form_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
         
        # Current Password
        current_label = ttk.Label(form_frame, text="Current Password:")
        current_label.grid(row=0, column=0, sticky=tk.W, pady=10)
         
        current_entry = ttk.Entry(form_frame, width=30, show="*")
        current_entry.grid(row=0, column=1, sticky=tk.W, pady=10)
         
        # New Password
        new_label = ttk.Label(form_frame, text="New Password:")
        new_label.grid(row=1, column=0, sticky=tk.W, pady=10)
         
        new_entry = ttk.Entry(form_frame, width=30, show="*")
        new_entry.grid(row=1, column=1, sticky=tk.W, pady=10)
         
        # Confirm New Password
        confirm_label = ttk.Label(form_frame, text="Confirm New Password:")
        confirm_label.grid(row=2, column=0, sticky=tk.W, pady=10)
         
        confirm_entry = ttk.Entry(form_frame, width=30, show="*")
        confirm_entry.grid(row=2, column=1, sticky=tk.W, pady=10)
         
        # Error message label
        error_label = ttk.Label(form_frame, text="", foreground=self.error_color)
        error_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)
         
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
         
        save_button = ttk.Button(
            button_frame, 
            text="Change Password", 
            command=lambda: self.change_password(
                current_entry.get(),
                new_entry.get(),
                confirm_entry.get(),
                error_label,
                dialog
            )
        )
        save_button.pack(side=tk.LEFT, padx=5)
         
        cancel_button = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
     
    def change_password(self, current_password, new_password, confirm_password, error_label, dialog):
        """Change user password"""
        try:
            # Validate fields
            if not current_password or not new_password or not confirm_password:
                error_label.config(text="All fields are required")
                return
             
            if new_password != confirm_password:
                error_label.config(text="New passwords do not match")
                return
             
            if len(new_password) < 6:
                error_label.config(text="Password must be at least 6 characters")
                return
             
            # Hash passwords
            current_hashed = hashlib.sha256(current_password.encode()).hexdigest()
            new_hashed = hashlib.sha256(new_password.encode()).hexdigest()
             
            # Verify current password
            conn = sqlite3.connect('bank_management.db')
            cursor = conn.cursor()
             
            cursor.execute("SELECT password FROM users WHERE id = ?", (self.current_user['id'],))
            stored_password = cursor.fetchone()[0]
             
            if current_hashed != stored_password:
                error_label.config(text="Current password is incorrect")
                conn.close()
                return
             
            # Update password
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_hashed, self.current_user['id']))
            conn.commit()
            conn.close()
             
            messagebox.showinfo("Success", "Password changed successfully")
            dialog.destroy()
        except Exception as e:
            error_label.config(text=f"Error: {str(e)}")
     
    def logout(self):
        """Log out current user and return to login screen"""
        self.current_user = None
        self.show_login()
 
# Animation Classes
class FadeAnimation:
    """Provides fade in/out animations for widgets"""
     
    @staticmethod
    def fade_in(widget, duration=500, steps=20):
        """Fade in a widget from transparent to opaque"""
        alpha = 0.0
        step_time = duration / steps
         
        def update_alpha(current_alpha):
            current_alpha += 1.0 / steps
            if current_alpha <= 1.0:
                widget.attributes("-alpha", current_alpha)
                widget.after(int(step_time), lambda: update_alpha(current_alpha))
         
        widget.attributes("-alpha", alpha)
        update_alpha(alpha)
     
    @staticmethod
    def fade_out(widget, duration=500, steps=20, callback=None):
        """Fade out a widget from opaque to transparent"""
        alpha = 1.0
        step_time = duration / steps
         
        def update_alpha(current_alpha):
            current_alpha -= 1.0 / steps
            if current_alpha >= 0:
                widget.attributes("-alpha", current_alpha)
                widget.after(int(step_time), lambda: update_alpha(current_alpha))
            elif callback:
                callback()
         
        update_alpha(alpha)
 
class LoadingAnimation:
    """Provides a loading animation for long operations"""
     
    def __init__(self, parent, text="Loading..."):
        self.parent = parent
        self.text = text
        self.frame = None
        self.canvas = None
        self.angle = 0
        self.running = False
     
    def start(self):
        """Start the loading animation"""
        self.frame = ttk.Frame(self.parent)
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
         
        self.canvas = tk.Canvas(self.frame, width=100, height=100, bg=self.parent.cget("background"), highlightthickness=0)
        self.canvas.pack()
         
        self.text_id = self.canvas.create_text(50, 70, text=self.text, fill="#333333", font=("Helvetica", 10))
         
        self.running = True
        self.update_spinner()
     
    def update_spinner(self):
        """Update the spinner animation"""
        if not self.running:
            return
         
        self.canvas.delete("spinner")
         
        # Draw spinner
        x, y = 50, 40
        radius = 20
        segments = 8
        for i in range(segments):
            angle = self.angle + (i * 360 / segments)
            alpha = 0.2 + (i / segments) * 0.8
            color = self.get_color_with_alpha("#1a73e8", alpha)
             
            x1 = x + radius * cos(angle * 3.14159 / 180)
            y1 = y + radius * sin(angle * 3.14159 / 180)
            self.canvas.create_oval(x1-5, y1-5, x1+5, y1+5, fill=color, outline="", tags="spinner")
         
        self.angle = (self.angle + 10) % 360
        self.canvas.after(50, self.update_spinner)
     
    def get_color_with_alpha(self, color, alpha):
        """Convert color with alpha to hex format"""
        r = int(int(color[1:3], 16) * alpha + 255 * (1 - alpha))
        g = int(int(color[3:5], 16) * alpha + 255 * (1 - alpha))
        b = int(int(color[5:7], 16) * alpha + 255 * (1 - alpha))
        return f"#{r:02x}{g:02x}{b:02x}"
     
    def stop(self):
        """Stop the loading animation"""
        self.running = False
        if self.frame:
            self.frame.destroy()
            self.frame = None
 
# Main application launch
def main():
    root = tk.Tk()
    app = BankManagementSystem(root)
    root.mainloop()
 
if __name__ == "__main__":
    main()