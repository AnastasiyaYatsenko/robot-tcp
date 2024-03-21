from async_server import *

# настраиваем логгинг
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
# запускаем сервер
serve_forever()

# from server import *
#
# # Створюємо серверний сокет без блокування основного потоку в очікуванні підключення
# server_socket = get_non_blocking_server_socket()
# INPUTS.append(server_socket)
# print("Server socket:")
# print(server_socket)
# print(server_socket.fileno())
#
# print("server is running, please, press ctrl+c to stop")
# try:
#     while INPUTS:
#         print("meanwhile")
#         readables, writables, exceptional = select.select(INPUTS, OUTPUTS, INPUTS)
#         handle_readables(readables, server_socket)
#         # handle_writables(writables)
# except KeyboardInterrupt:
#     clear_resource(server_socket)
#     print("Server stopped! Thank you for using!")
