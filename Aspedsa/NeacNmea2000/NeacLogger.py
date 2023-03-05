import logging

formatter = logging.Formatter('%(asctime)s;%(message)s')

class NeacLogger():
    def __init__(self, log_name, log_file_name):
        """To setup as many loggers as you want"""

        handler = logging.FileHandler('./log/' + log_file_name)        
        handler.setFormatter(formatter)

        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)        
        
    def get_logger(self):
        return self.logger

    