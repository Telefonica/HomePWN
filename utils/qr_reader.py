from utils.custom_print import print_info, print_ok, print_error, print_body, print_ok_raw
from prompt_toolkit import print_formatted_text, HTML
from utils.color_palette import ColorSelected



def display_qr(qr_read, verbose):
    """QR util method to display
    
    Args:
        qr_read ([Reg]): Data of the qr read
        verbose (Boolean): To display mor info
    """
    color = ColorSelected().theme.confirm
    print(color)
    print_ok_raw(f"Found {len(qr_read)} registries")
    for idx, reg in enumerate(qr_read):
        print_info(f"==== Reg {idx} ====")
        print_formatted_text(HTML(f"<{color}>Data:</{color}> {reg.data}"))
        if(verbose):
            print_formatted_text(HTML(f"<{color}>Type:</{color}> {reg.type}"))
            print_formatted_text(HTML(f"<{color}>Rect:</{color}> {reg.rect}"))
            print_formatted_text(HTML(f"<{color}>Polygon:</{color}> {reg.polygon}"))