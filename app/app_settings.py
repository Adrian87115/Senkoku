import json
import os

class AppSettings:
    DEFAULT_SETTINGS = {"official_online": False,
                        "confirmation_panel_enabled": True,
                        
                        # shortcut of screen selector
                        "screen_selector_sc": "ctrl+q"}

    def __init__(self, path = "settings.json"):
        self.path = path
        self._data = {}

        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding = "utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}
        else:
            self._data = {}

        # add missing options
        for key, default_value in self.DEFAULT_SETTINGS.items():
            self._data.setdefault(key, default_value)

        self.save()

    def save(self):
        with open(self.path, "w", encoding = "utf-8") as f:
            json.dump(self._data, f, indent = 4, ensure_ascii = False)

    def __getattr__(self, item):
        return self._data.get(item)

    def __setattr__(self, key, value):
        if key in ("path", "_data", "DEFAULT_SETTINGS"):
            return super().__setattr__(key, value)

        self._data[key] = value
        self.save()