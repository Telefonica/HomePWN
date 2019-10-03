from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.shortcuts import CompleteStyle
from utils.customcompleter import CustomCompleter
from utils.color_palette import ColorSelected
from os import getuid

if getuid() == 0:
    session = PromptSession(history=FileHistory("/tmp/homeS_historyroot"))
else:
    session = PromptSession(history=FileHistory("/tmp/homeS_history"))
    
def prompt(commands, module=None):
    """Launch the prompt with the given commands
    
    Args:
        commands ([str]): List of commands to autocomplete
        module (str, optional): Name of the module. Defaults to None.
    
    Returns:
        prompt session: Session of the promt
    """
    default_prompt = "homePwn"
    color_default_prompt = ColorSelected().theme.primary
    warn = ColorSelected().theme.warn
    confirm = ColorSelected().theme.confirm
    html = HTML(f"<bold><{color_default_prompt}>{default_prompt} >></{color_default_prompt}></bold>")
    if module:
        html = HTML(f"<bold><{color_default_prompt}>{default_prompt}</{color_default_prompt}> (<{warn}>{module}</{warn}>) <{confirm}>>></{confirm}></bold> ")
    data = session.prompt(
        html,
        completer= CustomCompleter(commands),
        complete_style=CompleteStyle.READLINE_LIKE,
        auto_suggest=AutoSuggestFromHistory(),
        enable_history_search=True)
    return  data
