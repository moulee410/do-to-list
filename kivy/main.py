from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox

TASKS_FILE = 'tasks.txt'  # File to store tasks

# User credentials and roles
users = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'user': {'password': 'user123', 'role': 'user'}
}

# Load tasks from the file (with completed status)
def load_tasks():
    try:
        tasks = []
        with open(TASKS_FILE, 'r') as f:
            for line in f:
                # Ignore empty lines or lines that don't contain the expected separator
                line = line.strip()
                if line:
                    try:
                        task, completed = line.split('|')
                        tasks.append({'task': task, 'completed': completed == 'True'})
                    except ValueError:
                        continue  # Skip lines that don't have the expected format
        return tasks
    except FileNotFoundError:
        return []

# Save tasks to the file (with completed status)
def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        for task in tasks:
            f.write(f"{task['task']}|{task['completed']}\n")

# Login Screen
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.layout.size_hint = (None, None)
        
        # Username Input (Wider and Taller)
        self.username_input = TextInput(hint_text="Enter Username", multiline=False, size_hint=(9, None), height=50)
        self.username_input.font_size = 18
        self.layout.add_widget(self.username_input)

        # Password Input (Wider and Taller)
        self.password_input = TextInput(hint_text="Enter Password", multiline=False, password=True, size_hint=(9, None), height=50)
        self.password_input.font_size = 18
        self.layout.add_widget(self.password_input)

        # Login Button
        self.login_button = Button(text="Login", size_hint=(0.9, None), height=50, background_color=(0.2, 0.6, 0.2, 1))
        self.login_button.bind(on_press=self.on_login)
        self.layout.add_widget(self.login_button)

        # Label for feedback
        self.feedback_label = Label(text="", font_size=18, color=(1, 0, 0, 1))
        self.layout.add_widget(self.feedback_label)

        self.add_widget(self.layout)

    def on_login(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        if username in users and users[username]['password'] == password:
            role = users[username]['role']
            self.feedback_label.text = f"Login Successful as {role.capitalize()}!"
            # Switch to the To-Do screen and pass the role
            self.manager.get_screen('todo').set_role(role)
            self.manager.current = 'todo'
        else:
            self.feedback_label.text = "Invalid credentials."

# To-Do Screen
class ToDoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Task Input (Wider and Taller)
        self.task_input = TextInput(hint_text="Enter a new task", multiline=False, size_hint=(0.9, None), height=50)
        self.task_input.font_size = 18
        self.layout.add_widget(self.task_input)

        # Add Task Button (Visible for Admin only)
        self.add_task_button = Button(text="Add Task", size_hint=(0.9, None), height=50, background_color=(0.2, 0.6, 0.2, 1))
        self.add_task_button.bind(on_press=self.add_task)
        self.layout.add_widget(self.add_task_button)

        # Task List (Scrollable)
        self.scroll_view = ScrollView(size_hint=(1, None), size=(400, 400))
        self.task_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.task_list.bind(minimum_height=self.task_list.setter('height'))
        self.scroll_view.add_widget(self.task_list)

        self.layout.add_widget(self.scroll_view)

        # Load saved tasks
        self.load_and_display_tasks()

        # Log Out Button
        self.logout_button = Button(text="Log Out", size_hint=(0.9, None), height=50, background_color=(0.8, 0.2, 0.2, 1))
        self.logout_button.bind(on_press=self.logout)
        self.layout.add_widget(self.logout_button)

        self.add_widget(self.layout)

    def load_and_display_tasks(self):
        tasks = load_tasks()
        for task in tasks:
            self.add_task_to_list(task)

    def add_task(self, instance):
        task = self.task_input.text
        if task:
            self.add_task_to_list({'task': task, 'completed': False})
            tasks = load_tasks()  # Load current tasks
            tasks.append({'task': task, 'completed': False})  # Add the new task
            save_tasks(tasks)  # Save the updated task list
            self.task_input.text = ""  # Clear the input

    def add_task_to_list(self, task):
        task_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        
        # Add task label
        task_label = Label(text=task['task'], size_hint_x=0.6, font_size=18)
        task_layout.add_widget(task_label)

        # Add checkbox to mark task as completed
        task_checkbox = CheckBox(size_hint_x=None, width=40)
        task_checkbox.active = task['completed']
        task_checkbox.bind(active=lambda checkbox, value: self.toggle_task_completion(value, task_label, task))
        task_layout.add_widget(task_checkbox)

        # Add delete button (Visible for Admin only)
        delete_button = Button(text="Delete", size_hint_x=0.2, background_color=(0.8, 0.2, 0.2, 1))
        delete_button.bind(on_press=lambda btn, task_label=task_label: self.delete_task(task_label))
        task_layout.add_widget(delete_button)

        # Add the task to the list
        self.task_list.add_widget(task_layout)

    def toggle_task_completion(self, completed, task_label, task):
        task['completed'] = completed
        if completed:
            task_label.text = f"[s]{task['task']}[/s]"  # Cross out the task text
        else:
            task_label.text = task['task']  # Remove the strikethrough

        # Save updated tasks to file
        tasks = load_tasks()
        for t in tasks:
            if t['task'] == task['task']:
                t['completed'] = completed
        save_tasks(tasks)

    def delete_task(self, task_label):
        task = task_label.text
        self.task_list.remove_widget(task_label.parent)  # Remove the task layout
        tasks = load_tasks()  # Load current tasks
        tasks = [t for t in tasks if t['task'] != task]  # Remove the task
        save_tasks(tasks)  # Save the updated task list

    def set_role(self, role):
        self.role = role
        if self.role == 'user':
            self.add_task_button.disabled = True  # Disable adding tasks for users
            for widget in self.task_list.children:
                if isinstance(widget, BoxLayout):
                    for sub_widget in widget.children:
                        if isinstance(sub_widget, Button):
                            sub_widget.disabled = True  # Disable delete button for users
        else:
            self.add_task_button.disabled = False
            for widget in self.task_list.children:
                if isinstance(widget, BoxLayout):
                    for sub_widget in widget.children:
                        if isinstance(sub_widget, Button):
                            sub_widget.disabled = False  # Enable delete button for admins

    def logout(self, instance):
        # Clear user session and go back to the Login Screen
        self.manager.current = 'login'
        self.manager.get_screen('login').username_input.text = ''
        self.manager.get_screen('login').password_input.text = ''
        self.manager.get_screen('login').feedback_label.text = ''
        self.manager.get_screen('todo').task_input.text = ''  # Clear any existing task input

# Main App
class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))  # Add LoginScreen
        sm.add_widget(ToDoScreen(name='todo'))  # Add ToDoScreen
        return sm

if __name__ == "__main__":
    MyApp().run()
