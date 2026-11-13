from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.utils import get_color_from_hex

PURPLE = "#8B5CF6"
WHITE = "#FFFFFF"
MUTED = "#B8B2D6"


class TrackerScreens:

    def init_screens(self, storage):
        self.storage = storage
        self.accounts = storage.load_accounts()
        self.show_pin()

    def label(self, text, size=16, color=WHITE):
        return Label(
            text=str(text),
            font_size=size,
            color=get_color_from_hex(color),
            halign="center",
            valign="middle"
        )

    def button(self, text, callback):
        btn = Button(
            text=text,
            size_hint_y=None,
            height=48,
            background_normal="",
            background_color=get_color_from_hex(PURPLE)
        )
        btn.bind(on_release=callback)
        return btn

    def field(self, hint, password=False):
        return TextInput(
            hint_text=hint,
            password=password,
            multiline=False,
            size_hint_y=None,
            height=48
        )

    def message(self, title, message):
        Popup(
            title=title,
            content=self.label(message),
            size_hint=(0.85, 0.35)
        ).open()

    def page(self, title):
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(
            self.label(title, 23, PURPLE)
        )

    def back(self):
        self.root_layout.add_widget(
            self.button("BACK HOME", lambda x: self.show_home())
        )

    def show_pin(self):
        self.page("JOMZ TRACKER PRO")
        self.root_layout.add_widget(
            self.label("SECURE LOCAL APP", 12, MUTED)
        )

        pin = self.field("Enter 4–8 digit PIN", True)
        self.root_layout.add_widget(pin)

        if not self.storage.has_pin():
            confirm = self.field("Confirm PIN", True)
            self.root_layout.add_widget(confirm)

            def create(btn):
                if pin.text != confirm.text:
                    self.message("ERROR", "PINs do not match.")
                    return

                if not self.storage.create_pin(pin.text):
                    self.message("ERROR", "Use 4–8 digits only.")
                    return

                self.storage.log_activity(
                    "SETUP", "APP", "PIN created"
                )
                self.show_home()

            self.root_layout.add_widget(
                self.button("CREATE PIN", create)
            )
        else:
            def login(btn):
                if self.storage.verify_pin(pin.text):
                    self.show_home()
                else:
                    self.message("ACCESS DENIED", "Incorrect PIN.")

            self.root_layout.add_widget(
                self.button("UNLOCK APP", login)
            )

    def show_home(self):
        self.accounts = self.storage.load_accounts()
        self.page("JOMZ TRACKER PRO")

        self.root_layout.add_widget(
            self.label("PREMIUM ACCOUNT MANAGER", 12, MUTED)
        )

        counts = {}
        for item in self.accounts:
            status = item.get("status", "Pending")
            counts[status] = counts.get(status, 0) + 1

        dashboard = GridLayout(
            cols=2,
            spacing=8,
            size_hint_y=None,
            height=125
        )

        for title, value in [
            ("TOTAL", len(self.accounts)),
            ("PENDING", counts.get("Pending", 0)),
            ("BOUND", counts.get("Bound", 0)),
            ("VERIFIED", counts.get("Verified", 0))
        ]:
            card = BoxLayout(orientation="vertical")
            card.add_widget(self.label(title, 12, MUTED))
            card.add_widget(self.label(value, 24, PURPLE))
            dashboard.add_widget(card)

        self.root_layout.add_widget(dashboard)

        buttons = [
            ("＋ ADD ENTRY", self.add_entry),
            ("▤ VIEW ENTRIES", self.view_entries),
            ("⌕ SEARCH", self.search_entry),
            ("↻ UPDATE STATUS", self.update_entry),
            ("✕ DELETE ENTRY", self.delete_entry),
            ("⇩ EXPORT CSV", self.export_csv),
            ("◷ ACTIVITY HISTORY", self.activity_history),
            ("🔒 LOCK APP", lambda x: self.show_pin())
        ]

        for title, callback in buttons:
            self.root_layout.add_widget(
                self.button(title, callback)
            )


    def add_entry(self, btn=None):
        self.page("ADD NEW ENTRY")

        name = self.field("Enter account name")
        gmail = self.field("Enter Gmail address")

        self.root_layout.add_widget(name)
        self.root_layout.add_widget(gmail)

        def save(btn):
            account_name = name.text.strip()
            email = gmail.text.strip()

            if not account_name or not email:
                self.message("ERROR", "Please fill in all fields.")
                return

            if "@" not in email:
                self.message("ERROR", "Please enter a valid Gmail address.")
                return

            self.accounts = self.storage.load_accounts()

            self.accounts.append({
                "name": account_name,
                "gmail": email,
                "status": "Pending"
            })

            self.storage.save_accounts(self.accounts)
            self.storage.log_activity(
                "ADD", account_name, "Status: Pending"
            )

            self.message("SUCCESS", "Entry added successfully!")
            self.show_home()

        self.root_layout.add_widget(
            self.button("SAVE ENTRY", save)
        )
        self.back()

    def view_entries(self, btn=None):
        self.accounts = self.storage.load_accounts()
        self.page("SAVED ENTRIES")

        if not self.accounts:
            self.root_layout.add_widget(
                self.label("NO ENTRIES FOUND", 16, MUTED)
            )
        else:
            for index, item in enumerate(self.accounts, 1):
                info = (
                    f"{index}. {item.get('name', 'Unknown')}\n"
                    f"{item.get('gmail', 'No Gmail')}\n"
                    f"STATUS: {item.get('status', 'Pending')}"
                )

                self.root_layout.add_widget(
                    self.label(info, 14, WHITE)
                )

        self.back()


    def search_entry(self, btn=None):
        self.page("SEARCH ENTRIES")

        query = self.field("Search name or Gmail")
        self.root_layout.add_widget(query)

        results = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=8
        )
        results.bind(
            minimum_height=results.setter("height")
        )

        from kivy.uix.scrollview import ScrollView

        scroll = ScrollView(size_hint=(1, 0.65))
        scroll.add_widget(results)

        self.root_layout.add_widget(scroll)

        def search(btn):
            results.clear_widgets()
            keyword = query.text.strip().lower()

            self.accounts = self.storage.load_accounts()
            matches = [
                item for item in self.accounts
                if keyword in item.get("name", "").lower()
                or keyword in item.get("gmail", "").lower()
            ]

            if not matches:
                results.add_widget(
                    self.label("NO MATCH FOUND", 15, MUTED)
                )
                return

            for item in matches:
                info = (
                    f"{item.get('name', 'Unknown')}\n"
                    f"{item.get('gmail', '')}\n"
                    f"STATUS: {item.get('status', 'Pending')}"
                )
                results.add_widget(
                    self.label(info, 14, WHITE)
                )

        self.root_layout.add_widget(
            self.button("SEARCH NOW", search)
        )
        self.back()

    def update_entry(self, btn=None):
        self.accounts = self.storage.load_accounts()
        self.page("UPDATE STATUS")

        if not self.accounts:
            self.root_layout.add_widget(
                self.label("NO ENTRIES FOUND", 16, MUTED)
            )
            self.back()
            return

        choices = [
            f"{i + 1}. {item.get('name', 'Unknown')}"
            for i, item in enumerate(self.accounts)
        ]

        picker = Spinner(
            text="Select an entry",
            values=choices,
            size_hint_y=None,
            height=48
        )
        self.root_layout.add_widget(picker)

        status_picker = Spinner(
            text="Select new status",
            values=("Pending", "Bound", "Locked", "Failed", "Verified"),
            size_hint_y=None,
            height=48
        )
        self.root_layout.add_widget(status_picker)

        def update(btn):
            if picker.text not in choices:
                self.message("ERROR", "Select an entry first.")
                return

            if status_picker.text == "Select new status":
                self.message("ERROR", "Select a status first.")
                return

            index = choices.index(picker.text)
            old_status = self.accounts[index].get(
                "status", "Pending"
            )
            new_status = status_picker.text
            account_name = self.accounts[index].get(
                "name", "Unknown"
            )

            self.accounts[index]["status"] = new_status
            self.storage.save_accounts(self.accounts)

            self.storage.log_activity(
                "UPDATE",
                account_name,
                f"{old_status} -> {new_status}"
            )

            self.message("SUCCESS", "Status updated!")
            self.show_home()

        self.root_layout.add_widget(
            self.button("SAVE STATUS", update)
        )
        self.back()


    def delete_entry(self, btn=None):
        self.accounts = self.storage.load_accounts()
        self.page("DELETE ENTRY")

        if not self.accounts:
            self.root_layout.add_widget(
                self.label("NO ENTRIES FOUND", 16, MUTED)
            )
            self.back()
            return

        choices = [
            f"{i + 1}. {item.get('name', 'Unknown')}"
            for i, item in enumerate(self.accounts)
        ]

        picker = Spinner(
            text="Select entry to delete",
            values=choices,
            size_hint_y=None,
            height=48
        )
        self.root_layout.add_widget(picker)

        def remove(btn):
            if picker.text not in choices:
                self.message("ERROR", "Select an entry first.")
                return

            index = choices.index(picker.text)
            account = self.accounts[index]
            account_name = account.get("name", "Unknown")

            del self.accounts[index]
            self.storage.save_accounts(self.accounts)

            self.storage.log_activity(
                "DELETE", account_name, "Entry deleted"
            )

            self.message("SUCCESS", "Entry deleted successfully!")
            self.show_home()

        self.root_layout.add_widget(
            self.button("DELETE SELECTED ENTRY", remove)
        )
        self.back()

    def activity_history(self, btn=None):
        self.page("ACTIVITY HISTORY")

        from kivy.uix.scrollview import ScrollView

        logs = self.storage.get_activity(50)

        content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=8
        )
        content.bind(
            minimum_height=content.setter("height")
        )

        if not logs:
            content.add_widget(
                self.label("NO ACTIVITY YET", 15, MUTED)
            )
        else:
            for line in reversed(logs):
                content.add_widget(
                    self.label(line.strip(), 13, WHITE)
                )

        scroll = ScrollView(size_hint=(1, 0.65))
        scroll.add_widget(content)
        self.root_layout.add_widget(scroll)
        self.back()

    def export_csv(self, btn=None):
        try:
            path = self.storage.export_csv()

            self.storage.log_activity(
                "EXPORT", "CSV", "Account records exported"
            )

            self.message(
                "CSV EXPORT SUCCESS",
                "CSV file created:\n" + path
            )
        except Exception as error:
            self.message(
                "EXPORT ERROR",
                str(error)
            )
