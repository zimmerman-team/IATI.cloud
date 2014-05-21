import logging

logger = logging.getLogger('parser')

def exception_handler(e, ref, current_def):
    try:
        logger.info("error in " + ref + ", def: " + current_def)
        if e:
            if e.args and e.args.__len__() > 0:
                logger.warning(e.args[0])
            if e.args.__len__() > 1:
                logger.warning(e.args[1])
            logger.warning(type(e))
    except Exception as e:
        if e.args and e.args.__len__() > 0:
            print e.args[0]
        if e.args.__len__() > 1:
            print e.args[1]
        print type(e)
