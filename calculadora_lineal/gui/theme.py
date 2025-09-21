# calculadora_lineal/gui/theme.py
COLORS = {
    "bg": "#071427",           # fondo principal (oscuro)
    "sidebar": "#0b1d3a",      # azul más oscuro para sidebar
    "sidebar_btn": "#122a55",  # hover / botones sidebar
    "sidebar_active": "#1a3a70",
    "panel": "#0d2a44",
    "card": "#0f3a5a",
    "accent": "#2b8bd3",
    "text": "#E6EEF3",
    "muted": "#9BB0C9",
    "danger": "#e06c75",
}

# Fuentes (fácil de cambiar si agregas .ttf)
FONTS = {
    "title": ("Helvetica", 18, "bold"),
    "subtitle": ("Helvetica", 12, "bold"),
    "normal": ("Helvetica", 11),
    "mono": ("Courier New", 11),
    "icon": ("Segoe UI Emoji", 20)  # para fallback con emoji
}