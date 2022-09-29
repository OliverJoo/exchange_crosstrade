import logging
import sys
import datetime

logging.basicConfig(
    level=logging.INFO,
    format="'%(asctime)s : %(filename)s	: %(funcName)s : %(lineno)d	: %(levelname)s : %(message)s",
    # format="'%(asctime)s : %(name)s  : %(filename)s	: %(funcName)s : %(lineno)d	: %(levelname)s : %(message)s",
    handlers=[
        logging.FileHandler('./oliver_util_package/log/debug_{:%Y%m%d}.log'.format(datetime.datetime.now()),
                            encoding='UTF-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
