# Importing all packages
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import sys
import os

import mysql.connector

# Assuming model.py and send_sms.py are in the same directory
from model import main as get_prediction
from send_sms import send

print('GUI SYSTEM STARTED...')

# --- Constants ---
LARGE_FONT = ("Arial", 16)
NORMAL_FONT = ("Arial", 12)
DB_CONFIG = {
    "host": "localhost",
    "user": "app",
    "password": "Kannada@143.",
    "database": "batch_db_new"
}

class BlindnessDetectionApp(tk.Tk):
    """Main application class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Retinal Blindness Detection System")
        self.geometry("900x600")

        # --- Database Connection ---
        self.db_connection = None
        self.db_cursor = None
        self._connect_to_database()

        self.logged_in_user = None

        # --- Styling ---
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TButton", padding=6, relief="flat", background="#cccccc", font=NORMAL_FONT)
        style.configure("TLabel", background="#f0f0f0", font=NORMAL_FONT)
        style.configure("Header.TLabel", font=LARGE_FONT)
        style.configure("Link.TLabel", foreground="blue", font=NORMAL_FONT)

        # --- Frame container ---
        container = ttk.Frame(self, padding="10 10 10 10")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginPage, SignupPage, MainPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _connect_to_database(self):
        try:
            self.db_connection = mysql.connector.connect(**DB_CONFIG)
            self.db_cursor = self.db_connection.cursor()
            print("Database connected successfully.")
        except mysql.connector.Error as e:
            messagebox.showerror(
                "Database Connection Error",
                f"Could not connect to the database.\n"
                f"Please ensure the MySQL server is running and the credentials are correct.\n\n"
                f"Error: {e}"
            )
            self.destroy()
            sys.exit(1)

    def _on_closing(self):
        """Handle window closing event."""
        if self.db_connection and self.db_connection.is_connected():
            self.db_cursor.close()
            self.db_connection.close()
            print("Database connection closed.")
        self.destroy()

    def show_frame(self, page_name):
        """Show a frame for the given page name."""
        frame = self.frames[page_name]
        if page_name == "MainPage" and self.logged_in_user:
             self.frames["MainPage"].update_welcome_message(self.logged_in_user)
        frame.tkraise()

class AuthPage(ttk.Frame):
    """Base class for Login and Signup pages."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        # Center the content
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        ttk.Label(self, text="Username:", font=NORMAL_FONT).grid(row=1, column=0, pady=5, sticky="s")
        username_entry = ttk.Entry(self, textvariable=self.username_var, width=30, font=NORMAL_FONT)
        username_entry.grid(row=2, column=0, padx=20, pady=(0, 10))

        ttk.Label(self, text="Password:", font=NORMAL_FONT).grid(row=3, column=0, pady=5, sticky="s")
        password_entry = ttk.Entry(self, textvariable=self.password_var, show="*", width=30, font=NORMAL_FONT)
        password_entry.grid(row=4, column=0, padx=20, pady=(0, 10))

class LoginPage(AuthPage):
    """Login Page."""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        ttk.Label(self, text="Login to Your Account", style="Header.TLabel").grid(row=0, column=0, pady=(20, 20), sticky="n")

        login_button = ttk.Button(self, text="Login", command=self._login)
        login_button.grid(row=5, column=0, pady=10, sticky="n")

        switch_label = ttk.Label(self, text="Don't have an account? Sign Up", style="Link.TLabel", cursor="hand2")
        switch_label.grid(row=6, column=0, pady=10, sticky="n")
        switch_label.bind("<Button-1>", lambda e: controller.show_frame("SignupPage"))

    def _login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return

        try:
            # IMPORTANT: Storing passwords in plaintext is a major security risk.
            # In a real application, you should hash passwords using a library like bcrypt.
            query = "SELECT * FROM THEGREAT WHERE USERNAME = %s AND PASSWORD = %s"
            self.controller.db_cursor.execute(query, (username, password))
            user_record = self.controller.db_cursor.fetchone()

            if user_record:
                self.controller.logged_in_user = username
                messagebox.showinfo("Success", f"Welcome, {username}!")
                self.controller.show_frame("MainPage")
                self.username_var.set("")
                self.password_var.set("")
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"An error occurred during login: {e}")

class SignupPage(AuthPage):
    """Signup Page."""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        ttk.Label(self, text="Create a New Account", style="Header.TLabel").grid(row=0, column=0, pady=(20, 20), sticky="n")

        signup_button = ttk.Button(self, text="Sign Up", command=self._signup)
        signup_button.grid(row=5, column=0, pady=10, sticky="n")

        switch_label = ttk.Label(self, text="Already have an account? Login", style="Link.TLabel", cursor="hand2")
        switch_label.grid(row=6, column=0, pady=10, sticky="n")
        switch_label.bind("<Button-1>", lambda e: controller.show_frame("LoginPage"))

    def _signup(self):
        username = self.username_var.get()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return

        try:
            # Check if username already exists
            check_query = "SELECT USERNAME FROM THEGREAT WHERE USERNAME = %s"
            self.controller.db_cursor.execute(check_query, (username,))
            if self.controller.db_cursor.fetchone():
                messagebox.showerror("Error", "This username is already registered. Please choose another one.")
                return

            # Insert new user
            insert_query = "INSERT INTO THEGREAT (USERNAME, PASSWORD) VALUES (%s, %s)"
            self.controller.db_cursor.execute(insert_query, (username, password))
            self.controller.db_connection.commit()

            messagebox.showinfo("Success", f"Account for '{username}' created successfully! You can now log in.")
            self.username_var.set("")
            self.password_var.set("")
            self.controller.show_frame("LoginPage")
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"An error occurred during signup: {e}")

class MainPage(ttk.Frame):
    """Main application page after login."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Header ---
        header_frame = ttk.Frame(self, padding="5 5 5 5")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.welcome_label = ttk.Label(header_frame, text="Welcome!", style="Header.TLabel")
        self.welcome_label.pack(side="left")
        logout_button = ttk.Button(header_frame, text="Logout", command=self._logout)
        logout_button.pack(side="right")

        # --- Control Panel (Left) ---
        control_panel = ttk.Frame(self, padding="10 10 10 10", relief="groove")
        control_panel.grid(row=1, column=0, sticky="ns", padx=(0, 10))
        
        upload_button = ttk.Button(control_panel, text="Upload Retinal Image", command=self._upload_and_predict)
        upload_button.pack(pady=10)

        self.result_label = ttk.Label(control_panel, text="Prediction will appear here.", wraplength=200, justify="left")
        self.result_label.pack(pady=10, fill="x")

        # --- Image Display (Right) ---
        image_frame = ttk.Frame(self, padding="10 10 10 10", relief="groove")
        image_frame.grid(row=1, column=1, sticky="nsew")
        image_frame.grid_rowconfigure(0, weight=1)
        image_frame.grid_columnconfigure(0, weight=1)

        self.image_label = ttk.Label(image_frame, text="Uploaded image will be displayed here.", anchor="center")
        self.image_label.grid(row=0, column=0, sticky="nsew")
        self.image_label.image = None # Keep a reference

    def update_welcome_message(self, username):
        self.welcome_label.config(text=f"Welcome, {username}!")

    def _logout(self):
        self.controller.logged_in_user = None
        # Reset UI elements
        self.image_label.config(image='', text="Uploaded image will be displayed here.")
        self.image_label.image = None
        self.result_label.config(text="Prediction will appear here.")
        self.controller.show_frame("LoginPage")

    def _upload_and_predict(self):
        file_path = filedialog.askopenfilename(
            title="Select a Retinal Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
        )
        if not file_path:
            print("File not selected.")
            return

        try:
            print(f"Processing file: {file_path}")
            # Get prediction from the model
            value, classes = get_prediction(file_path)
            
            result_text = f"Prediction Result:\n\nLabel: {value}\nClass: {classes}"
            self.result_label.config(text=result_text)
            print(result_text)

            # Update database
            query = "UPDATE THEGREAT SET PREDICT = %s WHERE USERNAME = %s"
            self.controller.db_cursor.execute(query, (str(value), self.controller.logged_in_user))
            self.controller.db_connection.commit()
            print("Database updated successfully.")

            # --- Send SMS Notification ---
            # This requires a configured send_sms.py file with your Twilio credentials.
            try:
                send(value, classes)
                print("SMS notification sent.")
            except Exception as sms_error:
                print(f"Failed to send SMS: {sms_error}")

            # Display image in the GUI
            self._display_image(file_path)

            print('Thanks for using the system!')

        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: {file_path}")
        except Exception as e:
            messagebox.showerror("Prediction Error", f"An error occurred during prediction: {e}")
            print(f"Error during prediction: {e}")

    def _display_image(self, file_path):
        """Loads and displays an image on the image_label."""
        try:
            # Open image and resize it to fit the label
            img = Image.open(file_path)
            
            # Calculate aspect ratio
            w, h = img.size
            max_size = 400
            if w > h:
                new_w = max_size
                new_h = int(max_size * (h/w))
            else:
                new_h = max_size
                new_w = int(max_size * (w/h))
            
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo  # Keep a reference to avoid garbage collection
        except Exception as e:
            self.image_label.config(image='', text=f"Error displaying image:\n{e}")
            self.image_label.image = None
            print(f"Error displaying image: {e}")


if __name__ == "__main__":
    app = BlindnessDetectionApp()
    app.mainloop()
