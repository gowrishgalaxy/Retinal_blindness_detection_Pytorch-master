# Importing all packages
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import sys
import os

# Imports for PDF Generation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as PlatypusImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

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
    "user": "root",
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
        self.prediction_data = {} # To store the latest prediction data

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
        for F in (LoginPage, SignupPage, MainPage, ReportPage):
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
        if page_name == "ReportPage":
            self.frames["ReportPage"].update_report()
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

        self.view_report_button = ttk.Button(control_panel, text="View Report", command=self._view_report, state="disabled")
        self.view_report_button.pack(pady=10)

        chatbot_button = ttk.Button(control_panel, text="Chat with AI", command=self._open_chatbot)
        chatbot_button.pack(pady=10)

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
        self.view_report_button.config(state="disabled")
        self.result_label.config(text="Prediction will appear here.")
        self.controller.show_frame("LoginPage")

    def _open_chatbot(self):
        """Opens the AI chatbot window."""
        # Pass the latest prediction data to the chatbot
        prediction_context = self.controller.prediction_data if 'value' in self.controller.prediction_data else None
        ChatbotWindow(self, prediction_context)


    def _view_report(self):
        self.controller.show_frame("ReportPage")

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

            # Store prediction data in the controller
            self.controller.prediction_data = {
                'value': value,
                'class': classes,
                'username': self.controller.logged_in_user,
                'image_path': file_path
            }
            
            result_text = f"Prediction Result:\n\nLabel: {value}\nClass: {classes}"
            self.result_label.config(text=result_text)
            print(result_text)

            # Update database
            query = "UPDATE THEGREAT SET PREDICT = %s WHERE USERNAME = %s"
            self.controller.db_cursor.execute(query, (str(value), self.controller.logged_in_user))
            self.controller.db_connection.commit()
            print("Database updated successfully.")

            # Enable the report button
            self.view_report_button.config(state="normal")

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

class ChatbotWindow(tk.Toplevel):
    """Chatbot window to interact with the user."""
    def __init__(self, parent, prediction_context=None):
        super().__init__(parent)
        self.title("AI Eye Care Assistant")
        self.geometry("500x600")
        self.prediction_context = prediction_context

        # This would store conversation history for a real LLM
        # self.chat_history = [] 
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Chat Display ---
        chat_frame = ttk.Frame(self, padding="10")
        chat_frame.grid(row=0, column=0, sticky="nsew")
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)

        self.chat_display = tk.Text(chat_frame, wrap="word", state="disabled", width=60, height=20, font=NORMAL_FONT)
        self.chat_display.grid(row=0, column=0, sticky="nsew")

        # --- User Input ---
        input_frame = ttk.Frame(self, padding="10")
        input_frame.grid(row=1, column=0, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        self.user_input = ttk.Entry(input_frame, font=NORMAL_FONT)
        self.user_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.user_input.bind("<Return>", self._send_message)

        send_button = ttk.Button(input_frame, text="Send", command=self._send_message)
        send_button.grid(row=0, column=1)

        # Personalized greeting if a prediction has been made
        if self.prediction_context:
            class_name = self.prediction_context['class']
            greeting = f"AI: Hello! I see your recent scan indicated **{class_name}**. You can ask me more about this condition, or any other questions you have about eye health."
        else:
            greeting = "AI: Hello! I am your AI Eye Care Assistant. How can I help you today? Ask me about eye diseases or tips for healthy eyes."
        self._add_message(greeting, "ai")

    def _send_message(self, event=None):
        user_text = self.user_input.get()
        if not user_text.strip():
            return

        self._add_message(f"You: {user_text}", "user")
        self.user_input.delete(0, tk.END)

        # Get response from chatbot logic
        ai_response = get_chatbot_response(user_text, self.prediction_context)
        self._add_message(f"AI: {ai_response}", "ai")

    def _add_message(self, message, sender):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, message + "\n\n")
        self.chat_display.config(state="disabled")
        self.chat_display.see(tk.END) # Auto-scroll

def get_chatbot_response(user_input, context=None):
    """
    A rule-based chatbot logic that can be extended.
    `context` is the prediction data, e.g., {'value': 1, 'class': 'Mild'}.
    """
    user_input = user_input.lower()
    
    # --- LLM Integration (Future Enhancement) ---
    # To enable this, you would:
    # 1. `pip install google-generativeai`
    # 2. Get an API key from Google AI Studio.
    # 3. Uncomment the code below and replace "YOUR_API_KEY".
    #
    # import google.generativeai as genai
    # try:
    #     genai.configure(api_key="YOUR_API_KEY")
    #     model = genai.GenerativeModel('gemini-pro')
    #     prompt = f"You are an expert AI assistant for eye health. A user has a question: '{user_input}'. "
    #     if context:
    #         prompt += f"Their last diagnosis was '{context['class']}'. "
    #     prompt += "Provide a helpful and concise answer."
    #     response = model.generate_content(prompt)
    #     return response.text
    # except Exception as e:
    #     print(f"Error with LLM API: {e}")
    #     return "I'm having trouble connecting to my advanced knowledge base right now. Please try again later."
    # --- End of LLM Integration ---

    # --- General Health & Prevention Queries ---
    prevention_keywords = ["prevent", "prevention", "protect", "safety", "tips", "precaution", "avoid"]
    if any(keyword in user_input for keyword in prevention_keywords):
        return ("To protect your vision and maintain eye health:\n"
                "1. Eat a balanced diet rich in vitamins A, C, and E.\n"
                "2. Wear sunglasses that block 99% or more of UVA and UVB radiation.\n"
                "3. Follow the 20-20-20 rule to reduce digital eye strain: Every 20 minutes, look at something 20 feet away for 20 seconds.\n"
                "4. Get regular comprehensive eye exams.\n"
                "5. Don't smoke, as it increases the risk of many eye diseases.")

    # --- Smoking-related Queries ---
    if "smoke" in user_input or "smoking" in user_input:
        return ("Smoking significantly increases the risk of several serious eye conditions, including:\n"
                "1. **Cataracts:** Smokers are at a much higher risk of developing cataracts.\n"
                "2. **Macular Degeneration (AMD):** Smoking is a major risk factor for AMD, a leading cause of severe vision loss in older adults.\n"
                "3. **Diabetic Retinopathy:** Smoking can worsen diabetes and accelerate damage to the retina.\n"
                "4. **Glaucoma:** There is a strong link between smoking and high pressure in the eye, which can lead to glaucoma.\n"
                "Quitting smoking is one of the best steps you can take to protect your eyesight.")

    # --- General Disease Listing ---
    if "types of eye disease" in user_input or "list diseases" in user_input:
        return "I can provide information on the following conditions: Diabetic Retinopathy, Glaucoma, and Cataracts. Which one would you like to know about?"

    # --- Expanded Rule-Based Logic ---
    disease_keywords = {
        "diabetic retinopathy": "diabetic retinopathy", "retinopathy": "diabetic retinopathy",
        "glaucoma": "glaucoma",
        "cataracts": "cataracts", "cataract": "cataracts",
        "macular degeneration": "macular degeneration", "amd": "macular degeneration"
    }

    detected_disease = None
    for keyword, disease in disease_keywords.items():
        if keyword in user_input:
            detected_disease = disease
            break

    # Context-aware questions
    if context and not detected_disease:
        if "tell me more" in user_input or "what is it" in user_input:
            if context['class'] == 'No DR':
                return "That's great news! 'No DR' means no signs of diabetic retinopathy were found. To keep your eyes healthy, it's important to maintain a healthy lifestyle and continue with regular eye check-ups."
            else:
                # Map other prediction classes to a keyword the chatbot understands
                context_disease_map = { 'Mild': 'diabetic retinopathy', 'Moderate': 'diabetic retinopathy', 'Severe': 'diabetic retinopathy', 'Proliferative DR': 'diabetic retinopathy' }
                detected_disease = context_disease_map.get(context['class'])


    # Responses based on detected disease
    if detected_disease == "diabetic retinopathy":
        if "symptoms" in user_input: return "Symptoms of diabetic retinopathy include blurred vision, floaters, and dark spots. It often has no early symptoms, making regular eye exams crucial for diabetics."
        if "treatment" in user_input: return "Treatments for diabetic retinopathy, which aim to slow progression, include laser therapy, eye injections, and surgery. Managing blood sugar is also vital."
        return "Diabetic retinopathy is an eye condition affecting blood vessels in the retina, often linked to diabetes. Early detection is key to preventing vision loss."
    
    if detected_disease == "glaucoma":
        if "symptoms" in user_input: return "Glaucoma often has no early symptoms. In later stages, it can cause gradual loss of peripheral vision. This is why it's called the 'silent thief of sight'."
        if "treatment" in user_input: return "Glaucoma treatment focuses on lowering eye pressure and may include prescription eye drops, laser therapy, or surgery to prevent further vision loss."
        return "Glaucoma is a group of eye conditions that damage the optic nerve, which is vital for good vision. It's often linked to high pressure inside your eye."

    if detected_disease == "cataracts":
        if "symptoms" in user_input: return "Symptoms of cataracts include cloudy or blurry vision, faded colors, glare (especially at night), and poor night vision."
        if "treatment" in user_input: return "The most effective treatment for cataracts is surgery to remove the cloudy lens and replace it with a clear, artificial one. It is a very common and safe procedure."
        return "A cataract is a clouding of the lens in the eye, which leads to a decrease in vision. It is a common part of aging."

    elif "hello" in user_input or "hi" in user_input:
        return "Hello! How can I assist you with your eye health questions?"
    else:
        return "I can provide information on Diabetic Retinopathy, Glaucoma, and Cataracts. Please ask me about one of these topics, their symptoms, or treatments."

class ReportPage(ttk.Frame):
    """Page to display a detailed report of the prediction."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.report_content = ""

        # --- Header ---
        header_frame = ttk.Frame(self, padding="5 5 5 5")
        header_frame.pack(fill="x")
        ttk.Label(header_frame, text="Diagnosis Report", style="Header.TLabel").pack(side="left")

        # --- Buttons ---
        button_frame = ttk.Frame(self, padding="5")
        button_frame.pack(fill="x")
        back_button = ttk.Button(button_frame, text="Back to Main", command=lambda: controller.show_frame("MainPage"))
        back_button.pack(side="left", padx=5)
        download_button = ttk.Button(button_frame, text="Download Report", command=self._download_report)
        download_button.pack(side="left", padx=5)

        # --- Report Display ---
        report_frame = ttk.Frame(self, padding="10", relief="groove")
        report_frame.pack(fill="both", expand=True, padx=10, pady=10)
        report_frame.grid_rowconfigure(0, weight=1)
        report_frame.grid_columnconfigure(0, weight=1)

        self.report_text = tk.Text(report_frame, wrap="word", state="disabled", font=NORMAL_FONT, height=20)
        self.report_text.grid(row=0, column=0, sticky="nsew")

    def update_report(self):
        """Generates and displays the report content."""
        data = self.controller.prediction_data
        if not data or 'value' not in data:
            self.report_content = "No prediction has been made yet. Please go back and upload an image."
        else:
            self.report_content = self._generate_report_text(data)

        self.report_text.config(state="normal")
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, self.report_content)
        self.report_text.config(state="disabled")

    def _generate_report_text(self, data, for_pdf=False):
        """Creates the detailed report string or returns components for PDF."""
        username = data['username']
        value = data['value']
        class_name = data['class']

        details = {
            0: ("No Diabetic Retinopathy (No DR)",
                "Your retinal scan shows no signs of diabetic retinopathy. This is excellent news. \n\nRecommendation: Continue with your annual eye screenings and maintain good control of your blood sugar levels, blood pressure, and cholesterol."),
            1: ("Mild Diabetic Retinopathy",
                "The scan indicates early signs of diabetic retinopathy, such as microaneurysms (tiny bulges in blood vessels). Vision is not usually affected at this stage.\n\nRecommendation: It is crucial to manage your diabetes and blood pressure strictly to prevent progression. More frequent eye exams may be recommended by your doctor."),
            2: ("Moderate Diabetic Retinopathy",
                "There is further progression of the disease with more significant damage to the blood vessels in the retina. There might be some vision impairment.\n\nRecommendation: Your condition requires close monitoring. Your ophthalmologist may suggest treatments to slow the disease. Strict management of your diabetes is essential."),
            3: ("Severe Diabetic Retinopathy",
                "The scan shows extensive vessel blockage and areas of the retina that are not receiving adequate blood flow. There is a high risk of vision loss.\n\nRecommendation: This stage requires prompt and active treatment from an eye care specialist. Treatments like laser therapy may be necessary to save your vision."),
            4: ("Proliferative Diabetic Retinopathy (PDR)",
                "This is the most advanced stage of the disease, where new, fragile blood vessels grow on the retina. These can leak blood, leading to severe vision loss or blindness.\n\nRecommendation: Immediate medical attention from an ophthalmologist is critical. Advanced treatments, including laser surgery and injections, are required to prevent permanent blindness.")
        }

        title, description = details.get(value, ("Unknown", "Could not determine the condition details."))

        if for_pdf:
            return title, description

        report = (
            f"--- RETINAL BLINDNESS DETECTION REPORT ---\n\n"
            f"Patient ID: {username}\n"
            f"Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"--- DIAGNOSIS ---\n"
            f"Prediction: {class_name} (Severity Level: {value})\n"
            f"Condition: {title}\n\n"
            f"--- DETAILS & RECOMMENDATIONS ---\n"
            f"{description}\n\n"
            f"--- DISCLAIMER ---\n"
            "This report is generated by an automated system and is not a substitute for a professional medical diagnosis. "
            "Consult with a qualified ophthalmologist or healthcare provider for a complete evaluation and treatment plan.\n"
        )
        return report

    def _download_report(self):
        """Saves the report content to a text file."""
        if not self.controller.prediction_data or 'value' not in self.controller.prediction_data:
            messagebox.showwarning("No Report", "There is no report to download.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf"), ("All Files", "*.*")],
            title="Save Report As",
            initialfile=f"Retinal_Report_{self.controller.logged_in_user}.pdf"
        )

        if not file_path:
            return

        try:
            self._create_pdf_report(file_path)
            messagebox.showinfo("Success", f"Report saved successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save the report: {e}")
            print(f"PDF generation error: {e}")

    def _create_pdf_report(self, file_path):
        """Generates and saves a PDF report."""
        doc = SimpleDocTemplate(file_path, pagesize=A4,
                                rightMargin=inch, leftMargin=inch,
                                topMargin=inch, bottomMargin=inch)
        styles = getSampleStyleSheet()
        story = []

        # --- Title ---
        story.append(Paragraph("Retinal Blindness Detection Report", styles['h1']))
        story.append(Spacer(1, 0.2 * inch))

        # --- Patient Info ---
        data = self.controller.prediction_data
        story.append(Paragraph(f"<b>Patient ID:</b> {data['username']}", styles['Normal']))
        story.append(Paragraph(f"<b>Date:</b> {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # --- Scanned Image ---
        story.append(Paragraph("<b>Scanned Retinal Image:</b>", styles['h3']))
        story.append(Spacer(1, 0.1 * inch))
        img_path = data.get('image_path')
        if img_path and os.path.exists(img_path):
            img = PlatypusImage(img_path, width=3*inch, height=3*inch, kind='proportional')
            story.append(img)
        else:
            story.append(Paragraph("Image not available.", styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # --- Diagnosis Details ---
        story.append(Paragraph("<b>Diagnosis Details:</b>", styles['h3']))
        story.append(Spacer(1, 0.1 * inch))

        username = data['username']
        value = data['value']
        class_name = data['class']
        title, description = self._generate_report_text(data, for_pdf=True)

        story.append(Paragraph(f"<b>Prediction:</b> {class_name} (Severity Level: {value})", styles['Normal']))
        story.append(Paragraph(f"<b>Condition:</b> {title}", styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # --- Details & Recommendations ---
        story.append(Paragraph("<b>Details & Recommendations:</b>", styles['h3']))
        # Create a style with indentation for the description
        body_style = ParagraphStyle(name='Body', parent=styles['Normal'], leftIndent=20)
        story.append(Paragraph(description.replace('\n', '<br/>'), body_style))
        story.append(Spacer(1, 0.3 * inch))

        # --- Disclaimer ---
        story.append(Paragraph("<b>Disclaimer:</b>", styles['h3']))
        disclaimer_text = ("This report is generated by an automated system and is not a substitute for a professional "
                           "medical diagnosis. Consult with a qualified ophthalmologist or healthcare provider for a "
                           "complete evaluation and treatment plan.")
        story.append(Paragraph(disclaimer_text, body_style))

        doc.build(story)

if __name__ == "__main__":
    app = BlindnessDetectionApp()
    app.mainloop()
