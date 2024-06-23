class AddException(Exception):
    """Exception raised when an error occurred during data adding"""
    pass


class ProcessingException(Exception):
    """Exception raised when an error occurred during indicator computation"""
    pass


class JobException(Exception):
    """Exception raised when an error occurred during job scheduling"""
    pass
