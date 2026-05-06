# bind - The server socket to bind.
bind = "0.0.0.0:8000"

# workers - The number of worker processes for handling requests.
# A positive integer generally in the 2-4 x $(NUM_CORES) range
workers = 5

# chdir - Chdir to specified directory before apps loading.
chdir = "/app/src"

# control_socket_disable - Inspect and manage Gunicorn via a Unix socket.
control_socket_disable = True
