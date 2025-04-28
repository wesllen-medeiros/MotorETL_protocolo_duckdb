import sys
from loguru import logger

logger.remove()
LEVEL = 'INFO'

formats = {
    'TRACE': '{time:HH:mm:ss}  [<cyan>TRACE</cyan>]: {message}',
    'DEBUG': '{time:HH:mm:ss}  [DEBUG]: {message}',
    'INFO': '{time:HH:mm:ss}  {message}',
    'WARNING': '{time:HH:mm:ss}  [<yellow>WARNING</yellow>]: {message}',
    'ERROR': '{time:HH:mm:ss}  [<red>ERROR</red>]: {message}',
    'CRITICAL': '{time:HH:mm:ss}  [<red>CRITICAL</red>]: \033[41m {message} \033[0m',
}

# >>>>>>
# Adiciona um handler para o stdout do terminal.
# >>>>>>
log_levels = ['TRACE', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
level_index = log_levels.index(LEVEL)
for level, fmt in formats.items():
    if log_levels.index(level) >= level_index:
        logger.add(
            sys.stdout,
            level=level,
            format=fmt,
            backtrace=True,
            diagnose=True,
        )
# >>>>>>
# Adiciona um handler para um arquivo de log.
# >>>>>>
logger.add(
    'logs/file_{time}.log',
    rotation='30 MB',
    retention='10 days',
    compression='zip',
    level='TRACE',
    format='{time:YYYY-MM-DD HH:mm:ss} {level} {message}',
    backtrace=True,
    diagnose=True,
)


def get_logger():
    return logger
