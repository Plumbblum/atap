import streamlit as st
import datetime
import json
import os
import re

# Данные о врачах и отделениях
DOCTORS_DATA = {
    "Терапія": ["Іванов І.І.", "Петрова А.С.", "Сидоров М.В."],
    "Кардіологія": ["Сердечна В.П.", "Пульсов Д.К."],
    "Неврологія": ["Нейронов А.Б.", "Мозгова О.Л."],
    "Офтальмологія": ["Глазова О.О.", "Зрачков І.І."],
    "Хірургія": ["Скальпелев Р.Р.", "Шовна Н.Н."],
    "Педіатрія": ["Дитяча А.А.", "Малишев О.П."],
    "Стоматологія": ["Зубов З.З.", "Щетинкіна Д.Д."]
}

def validate_email(email):
    """Проверка корректности email"""
    if not email:
        return True
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email)

def validate_phone(phone):
    """Проверка корректности номера телефона"""
    pattern = r'^\+?[0-9]{10,15}$'
    digits_only = ''.join(filter(str.isdigit, phone))
    return len(digits_only) >= 10 and len(digits_only) <= 15

def main():
    st.set_page_config(page_title="Запис на прийом до лікаря", layout="wide")
    
    st.title("🩺 Запис на прийом до лікаря")
    st.write("Будь ласка, заповніть форму для запису на прийом")

    with st.form("appointment_form"):
        # Персональные данные
        st.subheader("Персональні дані")
        col1, col2 = st.columns(2)
        
        with col1:
            last_name = st.text_input("Прізвище*", max_chars=50)
            first_name = st.text_input("Ім'я*", max_chars=50)
            middle_name = st.text_input("По батькові", max_chars=50)
            
        with col2:
            birth_date = st.date_input("Дата народження*", 
                                      min_value=datetime.date(1900, 1, 1),
                                      max_value=datetime.date.today())
            phone = st.text_input("Телефон*", max_chars=15)
            email = st.text_input("Email", max_chars=50)

        # Информация о приеме
        st.subheader("Інформація про прийом")
        col3, col4 = st.columns(2)
        
        with col3:
            department = st.selectbox("Відділення*", options=list(DOCTORS_DATA.keys()))
            doctors = DOCTORS_DATA.get(department, [])
            doctor = st.selectbox("Лікар*", options=doctors if doctors else ["Оберіть відділення"])
            
        with col4:
            appointment_date = st.date_input("Дата прийому*", 
                                            min_value=datetime.date.today() + datetime.timedelta(days=1))
            
            # Генерация временных слотов
            time_slots = [f"{h:02d}:{m:02d}" for h in range(9, 18) for m in [0, 30]]
            appointment_time = st.selectbox("Час прийому*", options=time_slots)

        # Дополнительные опции
        urgent = st.checkbox("Терміновий прийом")
        first_visit = st.checkbox("Первинний прийом", value=True)
        
        # Причина обращения
        reason = st.text_area("Причина звернення*", 
                             height=150,
                             placeholder="Опишіть ваші симптоми або причину звернення...")

        # Согласие
        agree_terms = st.checkbox("Я погоджуюсь на обробку моїх персональних даних*", value=False)

        # Кнопка отправки
        submitted = st.form_submit_button("📝 Записатися на прийом")

    if submitted:
        # Валидация данных
        errors = []
        
        required_fields = {
            "Прізвище": last_name,
            "Ім'я": first_name,
            "Дата народження": birth_date,
            "Телефон": phone,
            "Відділення": department,
            "Лікар": doctor,
            "Дата прийому": appointment_date,
            "Час прийому": appointment_time,
            "Причина звернення": reason
        }
        
        for field, value in required_fields.items():
            if not value:
                errors.append(f"Поле '{field}' є обов'язковим")
                
        if email and not validate_email(email):
            errors.append("Некоректний формат email")
            
        if not validate_phone(phone):
            errors.append("Некоректний формат телефону")
            
        if not agree_terms:
            errors.append("Необхідна згода на обробку даних")
            
        if errors:
            for error in errors:
                st.error(error)
        else:
            # Сохранение данных
            appointment_data = {
                "last_name": last_name,
                "first_name": first_name,
                "middle_name": middle_name,
                "birth_date": str(birth_date),
                "phone": phone,
                "email": email,
                "department": department,
                "doctor": doctor,
                "appointment_date": str(appointment_date),
                "appointment_time": appointment_time,
                "urgent": urgent,
                "first_visit": first_visit,
                "reason": reason,
                "created_at": datetime.datetime.now().isoformat()
            }
            
            try:
                os.makedirs("appointments", exist_ok=True)
                filename = f"appointments/{last_name}_{first_name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json"
                
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(appointment_data, f, ensure_ascii=False, indent=2)
                
                st.success(f"✅ Ви успішно записані на прийом до лікаря {doctor} на {appointment_date} о {appointment_time}!")
                st.balloons()
                
            except Exception as e:
                st.error(f"Помилка збереження: {str(e)}")

if __name__ == "__main__":
    main()
