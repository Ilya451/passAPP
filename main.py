import tkinter as tk
from tkinter import messagebox, ttk
import os
import pyautogui
import time
import subprocess
from cryptography.fernet import Fernet


class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PassMan")
        self.root.geometry("400x350")

        # Инициализация ключа
        self.key = None
        self.cipher_suite = None

        # Создание виджетов
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Введите секретный ключ:", padx=10, pady=5).grid(row=0, column=0, sticky='e')
        self.key_entry = tk.Entry(self.root, width=50)
        self.key_entry.grid(row=0, column=1)

        load_key_button = tk.Button(self.root, text="Загрузить ключ", command=self.load_key)
        load_key_button.grid(row=1, columnspan=2, pady=5)

        tk.Label(self.root, text="Имя лаунчера:", padx=10, pady=5).grid(row=2, column=0, sticky='e')
        self.launcher_entry = tk.Entry(self.root, width=30)
        self.launcher_entry.grid(row=2, column=1)

        tk.Label(self.root, text="Путь до лаунчера:", padx=10, pady=5).grid(row=3, column=0, sticky='e')
        self.launcher_path_entry = tk.Entry(self.root, width=30)
        self.launcher_path_entry.grid(row=3, column=1)

        tk.Label(self.root, text="Логин:", padx=10, pady=5).grid(row=4, column=0, sticky='e')
        self.login_entry = tk.Entry(self.root, width=30)
        self.login_entry.grid(row=4, column=1)

        tk.Label(self.root, text="Пароль:", padx=10, pady=5).grid(row=5, column=0, sticky='e')
        self.password_entry = tk.Entry(self.root, show='*', width=30)
        self.password_entry.grid(row=5, column=1)

        tk.Label(self.root, text="Выберите лаунчер:", padx=10, pady=5).grid(row=6, column=0, sticky='e')
        self.launcher_combobox = ttk.Combobox(self.root, state='readonly')
        self.launcher_combobox.grid(row=6, column=1)

        # Создаем контекстное меню
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Удалить", command=self.delete_launcher)

        # Привязываем контекстное меню к ComboBox
        self.launcher_combobox.bind("<Button-3>", self.show_context_menu)

        save_button = tk.Button(self.root, text="Сохранить данные", command=self.save_credentials)
        save_button.grid(row=7, columnspan=2, pady=5)

        launch_button = tk.Button(self.root, text="Запустить и подставить", command=self.launch_and_fill)
        launch_button.grid(row=8, columnspan=2, pady=5)

    def load_key(self):
        key_input = self.key_entry.get().strip()

        if key_input:
            try:
                self.key = key_input.encode()
                self.cipher_suite = Fernet(self.key)
                messagebox.showinfo("Успех", "Ключ загружен успешно.")
                self.update_launcher_list()  # Обновляем список лаунчеров после загрузки ключа
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки ключа: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Пожалуйста, введите ключ.")

    def save_credentials(self):
        if not self.cipher_suite:
            messagebox.showwarning("Предупреждение", "Пожалуйста, загрузите ключ перед сохранением данных.")
            return

        launcher_name = self.launcher_entry.get().strip()
        launcher_path = self.launcher_path_entry.get().strip()
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()

        if not launcher_name or not login or not password or not launcher_path:
            messagebox.showwarning("Предупреждение", "Пожалуйста, заполните все поля")
            return

        if not os.path.exists('credentials'):
            os.makedirs('credentials')

        # Шифрование пароля перед сохранением
        encrypted_password = self.cipher_suite.encrypt(password.encode())

        # Форматируем данные для записи в файл
        data_to_save = f'Login: {login}\nPassword: {encrypted_password.decode()}\nPath: {launcher_path}\n'

        with open(f'credentials/{launcher_name}.txt', 'wb') as file:
            file.write(data_to_save.encode())  # Сохраняем данные

        self.update_launcher_list()
        messagebox.showinfo("Успех", f"Данные сохранены для {launcher_name}")

    def launch_and_fill(self):
        if not self.cipher_suite:
            messagebox.showwarning("Предупреждение", "Пожалуйста, загрузите ключ перед запуском.")
            return

        launcher_name = self.launcher_combobox.get()

        if launcher_name:
            try:
                with open(f'credentials/{launcher_name}.txt', 'rb') as file:
                    data = file.read().decode()  # Читаем данные
                    lines = data.splitlines()
                    login = lines[0].split(': ')[1].strip()
                    encrypted_password = lines[1].split(': ')[1].strip().encode()
                    launcher_path = lines[2].split(': ')[1].strip()

                    # Дешифруем пароль
                    password = self.cipher_suite.decrypt(encrypted_password).decode()

                    # Запускаем лаунчер
                    subprocess.Popen(launcher_path)  # Запуск лаунчера
                    time.sleep(15)  # Задержка для загрузки лаунчера
                    pyautogui.typewrite(login)
                    pyautogui.press('tab')
                    pyautogui.typewrite(password)
                    pyautogui.press('enter')
            except FileNotFoundError:
                messagebox.showwarning("Предупреждение", f"Данные для {launcher_name} не найдены.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите лаунчер")

    def delete_launcher(self):
        launcher_name = self.launcher_combobox.get()

        if launcher_name:
            confirm = messagebox.askyesno("Подтверждение удаления",
                                          f"Вы уверены, что хотите удалить лаунчер '{launcher_name}'?")
            if confirm:
                try:
                    os.remove(f'credentials/{launcher_name}.txt')
                    self.update_launcher_list()
                    messagebox.showinfo("Успех", f"Лаунчер '{launcher_name}' успешно удален.")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить лаунчер: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите лаунчер для удаления.")

    def show_context_menu(self, event):
        if self.launcher_combobox.current() >= 0:  # Проверяем, что выбран элемент
            self.context_menu.post(event.x_root, event.y_root)

    def update_launcher_list(self):
        if not os.path.exists('credentials'):
            os.makedirs('credentials')

        self.launcher_combobox['values'] = [f[:-4] for f in os.listdir('credentials') if f.endswith('.txt')]
        self.launcher_combobox.set('')

    def encrypt_key(key, password):
        """Шифрует ключ с использованием пароля."""
        fernet = Fernet(Fernet.generate_key())
        encrypted_key = fernet.encrypt(key.encode())
        return encrypted_key


if __name__ == "__main__":
        root = tk.Tk()
        app = PasswordManagerApp(root)
        root.mainloop()





