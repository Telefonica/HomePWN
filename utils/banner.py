from random import choice
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.formatted_text import FormattedText
from utils.color_palette import ColorSelected
from time import sleep

# Info display
info = '''

       ☠ HomePwn - IoT Pentesting & Ethical Hacking ☠                 

      Created with ♥  by: 'Ideas Locas (CDO Telefonica)'        
                                                          
                      Version: '0.0.1b'                         
                                                          
'''

# Thanks to http://patorjk.com/software/taag/#p=display&f=Graffiti&t=Type%20Something%20

banner1 = """

.__                         __________                
|  |__   ____   _____   ____\______   \__  _  ______  
|  |  \ /  _ \ /     \_/ __ \|     ___/\ \/ \/ /    \ 
|   Y  (  <_> )  Y Y  \  ___/|    |     \     /   |  \\
|___|  /\____/|__|_|  /\___  >____|      \/\_/|___|  /
     \/             \/     \/                      \/ 

"""
banner2 = """

 ('-. .-.             _   .-')       ('-.     _ (`-.   (`\ .-') /`     .-') _  
( OO )  /            ( '.( OO )_   _(  OO)   ( (OO  )   `.( OO ),'    ( OO ) ) 
,--. ,--. .-'),-----. ,--.   ,--.)(,------. _.`     \,--./  .--.  ,--./ ,--,'  
|  | |  |( OO'  .-.  '|   `.'   |  |  .---'(__...--''|      |  |  |   \ |  |\  
|   .|  |/   |  | |  ||         |  |  |     |  /  | ||  |   |  |, |    \|  | ) 
|       |\_) |  |\|  ||  |'.'|  | (|  '--.  |  |_.' ||  |.'.|  |_)|  .     |/  
|  .-.  |  \ |  | |  ||  |   |  |  |  .--'  |  .___.'|         |  |  |\    |   
|  | |  |   `'  '-'  '|  |   |  |  |  `---. |  |     |   ,'.   |  |  | \   |   
`--' `--'     `-----' `--'   `--'  `------' `--'     '--'   '--'  `--'  `--'   
                                                                        
"""

banner3 = """

 ██░ ██  ▒█████   ███▄ ▄███▓▓█████  ██▓███   █     █░███▄    █ 
▓██░ ██▒▒██▒  ██▒▓██▒▀█▀ ██▒▓█   ▀ ▓██░  ██▒▓█░ █ ░█░██ ▀█   █ 
▒██▀▀██░▒██░  ██▒▓██    ▓██░▒███   ▓██░ ██▓▒▒█░ █ ░█▓██  ▀█ ██▒
░▓█ ░██ ▒██   ██░▒██    ▒██ ▒▓█  ▄ ▒██▄█▓▒ ▒░█░ █ ░█▓██▒  ▐▌██▒
░▓█▒░██▓░ ████▓▒░▒██▒   ░██▒░▒████▒▒██▒ ░  ░░░██▒██▓▒██░   ▓██░
 ▒ ░░▒░▒░ ▒░▒░▒░ ░ ▒░   ░  ░░░ ▒░ ░▒▓▒░ ░  ░░ ▓░▒ ▒ ░ ▒░   ▒ ▒ 
 ▒ ░▒░ ░  ░ ▒ ▒░ ░  ░      ░ ░ ░  ░░▒ ░       ▒ ░ ░ ░ ░░   ░ ▒░
 ░  ░░ ░░ ░ ░ ▒  ░      ░      ░   ░░         ░   ░    ░   ░ ░ 
 ░  ░  ░    ░ ░         ░      ░  ░             ░            ░ 
                                                               
"""

def little_animation():
    msg = "homePwn >>"
    index = 0
    while True:
        print(msg[index], end="", flush=True)
        index += 1
        if index == len(msg):
          break
        sleep(0.1)

    print("\033[A")

def banner(animation=True):
    banners = [banner1, banner2, banner3]
    color = ColorSelected()
    text = FormattedText([
    (color.theme.banner, choice(banners)),
    (color.theme.primary, info)
    ])
    print_formatted_text(text)
    if animation:
      little_animation()



