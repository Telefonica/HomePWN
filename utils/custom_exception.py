import functools
from utils.logger import Logger
from utils.custom_print import  print_error


def exception(msg):
    """Decorator used to handle exception and print custom messages or error message
    
    Args:
        msg (str): Custom message to print
    
    Returns:
        function: decorator
    """
    def exception_decorator(func):
        def wrapper(*args, **kwargs):
            logger = Logger.get_instance().get_logger()
            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                print_error("Interrupted...")
                return
            except:
                error = f"There was an exception in  {func.__name__}"
                logger.exception(error)
            if msg:
                print_error(msg)

        return wrapper
    return exception_decorator