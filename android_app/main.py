from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

from storage import TrackerStorage
from screens import TrackerScreens

Window.clearcolor = get_color_from_hex("#100D20")


class JomzTracker(App, TrackerScreens):

    def build(self):
        self.title = "JOMZ Tracker PRO"

        # Private storage for each installation
        self.storage = TrackerStorage(self.user_data_dir)

        # Scrollable Android screen
        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )
        self.scroll = scroll

        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=18,
            spacing=12,
            size_hint_y=None
        )

        # Fill the screen when content is shorter than viewport.
        def fit_content(*args):
            self.root_layout.height = max(
                self.scroll.height,
                self.root_layout.minimum_height
            )

        self.root_layout.bind(minimum_height=fit_content)
        scroll.bind(size=fit_content)

        scroll.add_widget(self.root_layout)

        # Load records and show PIN screen
        self.init_screens(self.storage)

        return scroll


if __name__ == "__main__":
    JomzTracker().run()
