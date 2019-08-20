class CommandPalette(object):

    def __init__(self, primary="ansibrightblue", confirm="ansigreen", accent="ansiyellow", warn="ansired", text="ansiblack", text_secondary="ansibrightblack", banner="ansired"):
        """Class holding the theme of the terminal, set values for theming color options
        
        Args:
            primary (str, optional): Primary color of the terminal. Defaults to "ansibrightblue".
            confirm (str, optional): Color seen in confirm. Defaults to "ansigreen".
            accent (str, optional): Color for info or accent text. Defaults to "ansiyellow".
            warn (str, optional): Color for warn or error. Defaults to "ansired".
            text (str, optional): Color for the body. Defaults to "ansiblack".
            text_secondary (str, optional): Secondary color. Defaults to "ansibrightblack".
            banner (str, optional): Custom color for the banner. Defaults to "ansired".
        """
        self.primary = primary
        self.confirm = confirm
        self.accent = accent
        self.warn = warn
        self.text = text
        self.text_secondary = text_secondary
        self.banner = banner

class ColorSelected(object):
    __instance = None
    def __new__(cls, theme=None):
        """Singleton Color selection, used for control the same theme in the hole CLI
        
        Args:
            theme (CommandPalette, optional): Default Command Palette. Defaults to None.
        
        Returns:
            instance: Instance of the object
        """
        if ColorSelected.__instance is None:
            ColorSelected.__instance = object.__new__(cls)
            ColorSelected.__instance.theme = colors_terminal["dark"]
        if(theme != None):
            ColorSelected.__instance.theme = theme
        return ColorSelected.__instance

# Just add your theme here and it will load to the CLI
colors_terminal = {
    "default": CommandPalette(),
    "light": CommandPalette(primary="ansibrightblue", confirm="ansigreen", accent="ansiyellow", warn="ansired", text="ansiblack", text_secondary="ansibrightblack", banner="ansired"),
    "dark": CommandPalette(primary="cyan", confirm="ansibrightgreen", accent="ansibrightyellow", warn="ansibrightred", text="ansiwhite", text_secondary="ansigray", banner="magenta"),
}