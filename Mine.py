import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import tkcalendar
from datetime import datetime, timedelta
import json
import os
import re

class DoctorAppointmentForm:
    def __init__(self, root):
        self.root = root
        self.root.title("Запис на прийом до лікаря")
        self.root.geometry("800x700")
        self.root.configure(bg="#f0f5f9")
        
        # Кольори
        self.primary_color = "#1e88e5"  # Синій
        self.secondary_color = "#4fc3f7"  # Світло-синій
        self.bg_color = "#f0f5f9"  # Світло-сірий фон
        self.text_color = "#37474f"  # Темно-сірий текст
        self.accent_color = "#43a047"  # Зелений для акцентів
        
        # Налаштування стилів
        self.setup_styles()
        
        # Створення змінних для зберігання даних форми
        self.first_name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()
        self.middle_name_var = tk.StringVar()
        self.birth_date_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.insurance_var = tk.StringVar()
        self.policy_number_var = tk.StringVar()
        self.doctor_var = tk.StringVar()
        self.department_var = tk.StringVar()
        self.appointment_date_var = tk.StringVar()
        self.appointment_time_var = tk.StringVar()
        self.urgent_var = tk.BooleanVar(value=False)
        self.first_visit_var = tk.BooleanVar(value=True)
        self.agree_terms_var = tk.BooleanVar(value=False)
        
        # Створення основного контейнера з прокруткою
        self.main_canvas = tk.Canvas(root, bg=self.bg_color)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(
                scrollregion=self.main_canvas.bbox("all")
            )
        )
        
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Створення та розміщення елементів форми
        self.create_widgets()
        
        # Прив'язка клавіші Enter до функції відправки форми
        self.root.bind('<Return>', lambda event: self.submit_appointment())
        
        # Словник з даними про лікарів та відділення
        self.doctors_data = {
            "Терапія": ["Іванов І.І.", "Петрова А.С.", "Сидоров М.В."],
            "Кардіологія": ["Сердечна В.П.", "Пульсов Д.К."],
            "Неврологія": ["Нейронов А.Б.", "Мозгова О.Л."],
            "Офтальмологія": ["Глазова О.О.", "Зрачков І.І."],
            "Хірургія": ["Скальпелев Р.Р.", "Шовна Н.Н."],
            "Педіатрія": ["Дитяча А.А.", "Малишев О.П."],
            "Стоматологія": ["Зубов З.З.", "Щетинкіна Д.Д."]
        }
        
        # Заповнення випадаючого списку відділень
        self.department_combobox['values'] = list(self.doctors_data.keys())
        
        # Оновлення списку лікарів при виборі відділення
        self.department_var.trace('w', self.update_doctors_list)
    
    def setup_styles(self):
        # Налаштування стилів для ttk віджетів
        style = ttk.Style()
        style.theme_use('clam')  # Використовуємо тему clam як основу
        
        # Основні стилі
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=("Arial", 10))
        style.configure("TButton", background=self.primary_color, foreground="white", font=("Arial", 10, "bold"))
        
        # Заголовки
        style.configure("Header.TLabel", font=("Arial", 16, "bold"), background=self.bg_color, foreground=self.primary_color)
        style.configure("Subheader.TLabel", font=("Arial", 12, "bold"), background=self.bg_color, foreground=self.text_color)
        
        # Рамки для секцій
        style.configure("Section.TFrame", background=self.bg_color, relief="ridge", borderwidth=1)
        
        # Кнопки
        style.configure("Submit.TButton", background=self.accent_color, foreground="white", font=("Arial", 11, "bold"))
        style.map("Submit.TButton",
                 background=[('active', self.accent_color), ('pressed', '#2e7d32')],
                 foreground=[('active', 'white'), ('pressed', 'white')])
        
        style.configure("Cancel.TButton", background="#e57373", foreground="white", font=("Arial", 11, "bold"))
        style.map("Cancel.TButton",
                 background=[('active', '#e57373'), ('pressed', '#c62828')],
                 foreground=[('active', 'white'), ('pressed', 'white')])
    
    def create_widgets(self):
        # Заголовок
        header_frame = ttk.Frame(self.scrollable_frame, style="TFrame")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ttk.Label(header_frame, text="Запис на прийом до лікаря", style="Header.TLabel")
        title_label.pack(pady=5)
        
        subtitle_label = ttk.Label(header_frame, text="Будь ласка, заповніть форму для запису на прийом", style="TLabel")
        subtitle_label.pack(pady=5)
        
        # Роздільник
        separator = ttk.Separator(self.scrollable_frame, orient='horizontal')
        separator.pack(fill='x', padx=20, pady=10)
        
        # Основна форма
        main_form = ttk.Frame(self.scrollable_frame, style="TFrame")
        main_form.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Персональні дані
        personal_frame = ttk.LabelFrame(main_form, text="Персональні дані", style="TFrame")
        personal_frame.pack(fill="x", pady=10, padx=5)
        
        # Ім'я
        name_frame = ttk.Frame(personal_frame, style="TFrame")
        name_frame.pack(fill="x", pady=5)
        
        # Прізвище
        last_name_label = ttk.Label(name_frame, text="Прізвище*:", style="TLabel")
        last_name_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        last_name_entry = ttk.Entry(name_frame, textvariable=self.last_name_var, width=20)
        last_name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Ім'я
        first_name_label = ttk.Label(name_frame, text="Ім'я*:", style="TLabel")
        first_name_label.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        first_name_entry = ttk.Entry(name_frame, textvariable=self.first_name_var, width=20)
        first_name_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        # По батькові
        middle_name_label = ttk.Label(name_frame, text="По батькові:", style="TLabel")
        middle_name_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        middle_name_entry = ttk.Entry(name_frame, textvariable=self.middle_name_var, width=20)
        middle_name_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Дата народження
        birth_date_label = ttk.Label(name_frame, text="Дата народження*:", style="TLabel")
        birth_date_label.grid(row=1, column=2, sticky="w", padx=5, pady=5)
        
        # Використовуємо віджет календаря для вибору дати
        birth_date_entry = tkcalendar.DateEntry(
            name_frame, 
            width=17, 
            background=self.primary_color,
            foreground='white', 
            borderwidth=2,
            date_pattern='dd.mm.yyyy',
            textvariable=self.birth_date_var
        )
        birth_date_entry.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        
        # Контактна інформація
        contact_frame = ttk.Frame(personal_frame, style="TFrame")
        contact_frame.pack(fill="x", pady=5)
        
        # Телефон
        phone_label = ttk.Label(contact_frame, text="Телефон*:", style="TLabel")
        phone_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        phone_entry = ttk.Entry(contact_frame, textvariable=self.phone_var, width=20)
        phone_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Email
        email_label = ttk.Label(contact_frame, text="Email:", style="TLabel")
        email_label.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        email_entry = ttk.Entry(contact_frame, textvariable=self.email_var, width=20)
        email_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        # Інформація про прийом
        appointment_frame = ttk.LabelFrame(main_form, text="Інформація про прийом", style="TFrame")
        appointment_frame.pack(fill="x", pady=10, padx=5)
        
        # Відділення
        department_label = ttk.Label(appointment_frame, text="Відділення*:", style="TLabel")
        department_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.department_combobox = ttk.Combobox(appointment_frame, textvariable=self.department_var, state="readonly", width=20)
        self.department_combobox.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Лікар
        doctor_label = ttk.Label(appointment_frame, text="Лікар*:", style="TLabel")
        doctor_label.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        self.doctor_combobox = ttk.Combobox(appointment_frame, textvariable=self.doctor_var, state="readonly", width=20)
        self.doctor_combobox.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        # Дата прийому
        date_label = ttk.Label(appointment_frame, text="Дата прийому*:", style="TLabel")
        date_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        # Мінімальна дата - завтрашній день
        tomorrow = datetime.now() + timedelta(days=1)
        
        appointment_date_entry = tkcalendar.DateEntry(
            appointment_frame, 
            width=17, 
            background=self.primary_color,
            foreground='white', 
            borderwidth=2,
            date_pattern='dd.mm.yyyy',
            textvariable=self.appointment_date_var,
            mindate=tomorrow
        )
        appointment_date_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Час прийому
        time_label = ttk.Label(appointment_frame, text="Час прийому*:", style="TLabel")
        time_label.grid(row=1, column=2, sticky="w", padx=5, pady=5)
        
        # Створюємо список часу з 9:00 до 18:00 з інтервалом 30 хвилин
        time_slots = []
        for hour in range(9, 18):
            time_slots.append(f"{hour:02d}:00")
            time_slots.append(f"{hour:02d}:30")
        
        time_combobox = ttk.Combobox(appointment_frame, textvariable=self.appointment_time_var, values=time_slots, state="readonly", width=17)
        time_combobox.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        
        # Додаткові опції
        options_frame = ttk.Frame(appointment_frame, style="TFrame")
        options_frame.grid(row=2, column=0, columnspan=4, sticky="w", padx=5, pady=5)
        
        urgent_check = ttk.Checkbutton(options_frame, text="Терміновий прийом", variable=self.urgent_var)
        urgent_check.pack(side="left", padx=5)
        
        first_visit_check = ttk.Checkbutton(options_frame, text="Первинний прийом", variable=self.first_visit_var)
        first_visit_check.pack(side="left", padx=20)
        
        # Причина звернення
        reason_frame = ttk.LabelFrame(main_form, text="Причина звернення", style="TFrame")
        reason_frame.pack(fill="x", pady=10, padx=5)
        
        reason_label = ttk.Label(reason_frame, text="Опишіть ваші симптоми або причину звернення:", style="TLabel")
        reason_label.pack(anchor="w", padx=5, pady=5)
        
        self.reason_text = scrolledtext.ScrolledText(reason_frame, wrap=tk.WORD, width=60, height=5)
        self.reason_text.pack(fill="x", padx=5, pady=5)
        
        # Згода на обробку даних
        consent_frame = ttk.Frame(main_form, style="TFrame")
        consent_frame.pack(fill="x", pady=10, padx=5)
        
        consent_check = ttk.Checkbutton(
            consent_frame, 
            text="Я погоджуюсь на обробку моїх персональних даних і підтверджую достовірність вказаної інформації", 
            variable=self.agree_terms_var
        )
        consent_check.pack(anchor="w", padx=5, pady=5)
        
        # Примітка про обов'язкові поля
        note_label = ttk.Label(main_form, text="* - обов'язкові поля", style="TLabel", foreground="red")
        note_label.pack(anchor="w", padx=5, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(main_form, style="TFrame")
        button_frame.pack(fill="x", pady=20, padx=5)
        
        submit_button = ttk.Button(
            button_frame, 
            text="Записатися на прийом", 
            command=self.submit_appointment,
            style="Submit.TButton"
        )
        submit_button.pack(side="right", padx=5)
        
        clear_button = ttk.Button(
            button_frame, 
            text="Очистити форму", 
            command=self.clear_form,
            style="Cancel.TButton"
        )
        clear_button.pack(side="right", padx=5)
        
        # Статус
        self.status_label = ttk.Label(main_form, text="", foreground="green", style="TLabel")
        self.status_label.pack(pady=10)
    
    def update_doctors_list(self, *args):
        """Оновлює список лікарів залежно від обраного відділення"""
        department = self.department_var.get()
        if department in self.doctors_data:
            self.doctor_combobox['values'] = self.doctors_data[department]
            self.doctor_var.set("")  # Скидаємо вибраного лікаря
        else:
            self.doctor_combobox['values'] = []
    
    def validate_email(self, email):
        """Перевірка коректності email"""
        if not email:  # Email необов'язковий
            return True
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email)
    
    def validate_phone(self, phone):
        """Перевірка коректності номера телефону"""
        pattern = r'^\\+?[0-9]{10,15}$'
        # Видаляємо всі нецифрові символи для перевірки
        digits_only = ''.join(filter(str.isdigit, phone))
        return len(digits_only) >= 10 and len(digits_only) <= 15
    
    def submit_appointment(self):
        """Обробка відправки форми"""
        # Отримання даних з форми
        last_name = self.last_name_var.get().strip()
        first_name = self.first_name_var.get().strip()
        middle_name = self.middle_name_var.get().strip()
        birth_date = self.birth_date_var.get()
        phone = self.phone_var.get().strip()
        email = self.email_var.get().strip()
        insurance = self.insurance_var.get()
        policy_number = self.policy_number_var.get().strip()
        department = self.department_var.get()
        doctor = self.doctor_var.get()
        appointment_date = self.appointment_date_var.get()
        appointment_time = self.appointment_time_var.get()
        urgent = self.urgent_var.get()
        first_visit = self.first_visit_var.get()
        reason = self.reason_text.get("1.0", tk.END).strip()
        agree_terms = self.agree_terms_var.get()
        
        # Перевірка обов'язкових полів
        required_fields = [
            (last_name, "Прізвище"),
            (first_name, "Ім'я"),
            (birth_date, "Дата народження"),
            (phone, "Телефон"),
            (department, "Відділення"),
            (doctor, "Лікар"),
            (appointment_date, "Дата прийому"),
            (appointment_time, "Час прийому")
        ]
        
        for value, field_name in required_fields:
            if not value:
                messagebox.showerror("Помилка", f"Будь ласка, заповніть поле '{field_name}'")
                return
        
        # Перевірка email
        if email and not self.validate_email(email):
            messagebox.showerror("Помилка", "Будь ласка, введіть коректний email")
            return
        
        # Перевірка згоди на обробку даних
        if not agree_terms:
            messagebox.showerror("Помилка", "Необхідна згода на обробку персональних даних")
            return
        
        # Створення об'єкта запису на прийом
        appointment_data = {
            "last_name": last_name,
            "first_name": first_name,
            "middle_name": middle_name,
            "birth_date": birth_date,
            "phone": phone,
            "email": email,
            "insurance": insurance,
            "policy_number": policy_number,
            "department": department,
            "doctor": doctor,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "urgent": urgent,
            "first_visit": first_visit,
            "reason": reason,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # У реальному додатку тут був би код для відправки даних на сервер
        # Для демонстрації збережемо в JSON файл
        try:
            # Перевірка існування директорії
            if not os.path.exists("appointments"):
                os.makedirs("appointments")
            
            # Генерація імені файлу
            file_name = f"appointments/{last_name}_{first_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            
            # Збереження даних запису
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(appointment_data, f, ensure_ascii=False, indent=4)
            
            messagebox.showinfo("Успіх", f"Ви успішно записані на прийом до лікаря {doctor} на {appointment_date} о {appointment_time}!")
            self.status_label.config(text="Запис на прийом успішно створено", foreground="green")
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Виникла помилка при створенні запису: {e}")
    
    def clear_form(self):
        """Очищення полів форми"""
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.middle_name_var.set("")
        self.birth_date_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.insurance_var.set("")
        self.policy_number_var.set("")
        self.department_var.set("")
        self.doctor_var.set("")
        self.appointment_date_var.set("")
        self.appointment_time_var.set("")
        self.urgent_var.set(False)
        self.first_visit_var.set(True)
        self.reason_text.delete("1.0", tk.END)
        self.agree_terms_var.set(False)
        self.status_label.config(text="")

def main():
    root = tk.Tk()
    app = DoctorAppointmentForm(root)
    root.mainloop()

if __name__ == "__main__":
    main()