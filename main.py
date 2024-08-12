from async_server import *

# налаштовуємо лог
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] [%(thread)s] %(message)s',
    '%H:%M:%S'
)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.info('Run')
# запускаємо сервер
serve_forever()
