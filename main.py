from server import *

# Створюємо серверний сокет без блокування основного потоку в очікуванні підключення
server_socket = get_non_blocking_server_socket()
INPUTS.append(server_socket)
robot_simulation()

print("server is running, please, press ctrl+c to stop")
try:
    while INPUTS:
        readables, writables, exceptional = select.select(INPUTS, OUTPUTS, INPUTS)
        handle_readables(readables, server_socket)
        handle_writables(writables)
        robot_simulation()
        #send_point()
except KeyboardInterrupt:
    clear_resource(server_socket)
    print("Server stopped! Thank you for using!")
