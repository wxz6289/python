import os
import sys

from loguru import logger

root_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(root_dir, 'log')

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "{process.name} | {thread.name} | "
    "<cyan>{module}</cyan>.<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{level}</level>: <level>{message}</level>"
)


class MyLogger:
    def __init__(self, log_file: str | None = None):
        self.logger = logger
        self.logger.remove()
        self.logger.add(sys.stdout, level='DEBUG', format=LOG_FORMAT)
        if log_file:
            self.logger.add(
                os.path.join(log_dir, log_file),
                level='DEBUG',
                format=LOG_FORMAT,
                rotation="10 MB",
                retention="7 days",
                encoding="utf-8",
            )

    def get_logger(self):
        return self.logger


if __name__ == '__main__':
    log = MyLogger().get_logger()
    log.debug('debug')
    log.info('info')
    log.warning('warning')
    log.error('error')
    log.critical('critical')
