import logging

logger = logging.getLogger(__name__)

def exception_handler(e, ref, current_def):

    logger.info("error in " + ref + ", def: " + current_def)
    if e.args and e.args.__len__() > 0:
        logger.warning(e.args[0])
    if e.args.__len__() > 1:
        logger.warning(e.args[1])
    logger.warning(type(e))
