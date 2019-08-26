from prompt_toolkit import print_formatted_text, HTML
from utils.color_palette import ColorSelected

"""Set of utils for printing with custom colors and format
"""

def print_error(msg, start="", end=""):
    print_formatted_text(HTML(f"<{ColorSelected().theme.warn}>{start}[!] {msg}{end}</{ColorSelected().theme.warn}>"))

def print_error_raw(msg, start="", end=""):
    print_formatted_text(HTML(f"<{ColorSelected().theme.warn}>{start}{msg}{end}</{ColorSelected().theme.warn}>"))
    
def print_info(msg, start="", end=""):
    print_formatted_text(HTML(f"<{ColorSelected().theme.accent}>{start}{msg}{end}</{ColorSelected().theme.accent}>"))

def print_ok(msg, start="", end=""):
    print_formatted_text(HTML(f"<{ColorSelected().theme.confirm}>{start}[+] {msg}{end}</{ColorSelected().theme.confirm}>"))

def print_ok_raw(msg, start="", end=""):
    print_formatted_text(HTML(f"<{ColorSelected().theme.confirm}>{start}{msg}{end}</{ColorSelected().theme.confirm}>"))

def print_body(msg, start="", end=""):
    print_formatted_text(HTML(f"<{ColorSelected().theme.text}>{start}{msg}{end}</{ColorSelected().theme.text}>"))

def print_msg(msg, color, start="", end=""):
    print_formatted_text(HTML(f"<ansi{color}>{start}{msg}{end}</ansi{color}>"))
