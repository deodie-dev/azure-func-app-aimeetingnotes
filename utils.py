import logging
# from config import dev_mode

def log_and_print (message=None):
    # if dev_mode:
    #     print(message)
    logging.info  (message)

def log_and_print_err (message=None):
    # if dev_mode:
    #     print(message)
    logging.error  (message)
