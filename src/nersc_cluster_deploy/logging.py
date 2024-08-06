from __future__ import annotations
import logging

def setup_logger(level: int = logging.DEBUG) -> logging.Logger:
    """
    Setup logging for testing purposes.

    Args:
        level: int, optional
            The logging level, by default logging.DEBUG

    Returns:
        logging.Logger
    """
    #Create logger
    logger = logging.getLogger('nersc_cluster_deploy')
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s %(message)s')

    #Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)

    #Create file handler
    fh = logging.FileHandler('nersc_cluster_deploy.log')
    fh.setLevel(logging.NOTSET)
    fh.setFormatter(formatter)

    #Add handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger