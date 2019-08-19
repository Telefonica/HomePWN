from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
from utils.color_palette import ColorSelected



def show_help():
    help_command = '''
    Core commands
    =============

        Command                    Description
        -------                    -----------
        help                       Help menu
        load <module>              Load module
        modules  [category]        List all modules or a certain category
        find <info>                Search modules with concret info
        exit|quit                  Exit application
        banner                     Show banner
        set <option> <value>       Set value for module's option
        unset <option>             Unset value for module's option
        run                        Run module
        back                       Unload module                                        
        show [options|info]        Show either options or info 
        global <option> <value>    Set global option
        export                     Save global options  
        import                     Load global options (previously exported)
        tasks <show/kill> [id]     Show tasks running or kill a task
        theme dark|light|default   Change the theme of the tool
        # <command>                Grant terminal commands        
    '''
    
    text = FormattedText([(f'{ColorSelected().theme.text}', help_command)])
    print_formatted_text(text)