import logging

logger = logging.getLogger('parser')

def exception_handler(e, ref, current_def):
    try:
        if e:
            logger.info("error in " + ref + ", def: " + current_def)
            if e.args and e.args.__len__() > 0:
                logger.warning(e.args[0])
            if e.args.__len__() > 1:
                logger.warning(e.args[1])
            logger.warning(type(e))
        else:
            logger.info("Message: " + ref + ", message 2: " + current_def)

    except Exception as e2:
        if e2.args and e2.args.__len__() > 0:
            logger.error(e2.args[0])
        if e2.args.__len__() > 1:
            logger.error(e2.args[1])
        logger.error(type(e2))