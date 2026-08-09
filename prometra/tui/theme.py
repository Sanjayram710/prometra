
THEMES: dict[str, dict[str, str]] = {
    "cyan": {
        "primary": "#00E5FF",
        "secondary": "#00B0FF",
        "accent": "#76FF03",
        "background": "#0F172A",
        "surface": "#1E293B",
        "text": "#F8FAFC",
        "text_muted": "#94A3B8",
        "border": "#334155",
        "success": "#22C55E",
        "warning": "#F59E0B",
        "error": "#EF4444",
    },
    "dark": {
        "primary": "#3B82F6",
        "secondary": "#6366F1",
        "accent": "#10B981",
        "background": "#18181B",
        "surface": "#27272A",
        "text": "#FAFAFA",
        "text_muted": "#A1A1AA",
        "border": "#3F3F46",
        "success": "#10B981",
        "warning": "#F59E0B",
        "error": "#F43F5E",
    },
    "dracula": {
        "primary": "#BD93F9",
        "secondary": "#FF79C6",
        "accent": "#50FA7B",
        "background": "#282A36",
        "surface": "#44475A",
        "text": "#F8F8F2",
        "text_muted": "#6272A4",
        "border": "#6272A4",
        "success": "#50FA7B",
        "warning": "#FFB86C",
        "error": "#FF5555",
    },
    "high_contrast": {
        "primary": "#FFFF00",
        "secondary": "#00FFFF",
        "accent": "#00FF00",
        "background": "#000000",
        "surface": "#1C1C1C",
        "text": "#FFFFFF",
        "text_muted": "#CCCCCC",
        "border": "#FFFFFF",
        "success": "#00FF00",
        "warning": "#FFFF00",
        "error": "#FF0000",
    },
}


class ThemeManager:
    """Manages color themes for the Prometra TUI application."""

    def __init__(self, default_theme: str = "cyan"):
        self.theme_names = list(THEMES.keys())
        self.current_index = (
            self.theme_names.index(default_theme)
            if default_theme in self.theme_names
            else 0
        )

    @property
    def current_theme_name(self) -> str:
        return self.theme_names[self.current_index]

    @property
    def current_theme(self) -> dict[str, str]:
        return THEMES[self.current_theme_name]

    def cycle_theme(self) -> str:
        self.current_index = (self.current_index + 1) % len(self.theme_names)
        return self.current_theme_name

    def set_theme(self, name: str) -> bool:
        if name in THEMES:
            self.current_index = self.theme_names.index(name)
            return True
        return False
