from async_server import *
import argparse

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

parser = argparse.ArgumentParser()
parser.add_argument("--ip", help="ip for server",
                    type=str)
args = parser.parse_args()

# запускаємо сервер
serve_forever(args.ip)
