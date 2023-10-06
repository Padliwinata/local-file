import socket
import os

# Define the host and port to listen on
HOST = '127.0.0.1'  # Listen on all available network interfaces
PORT = 1000     # Use an available port number

# Specify the directory to share
SHARED_DIRECTORY = './soal'  # Replace with the actual directory path

# Create a socket and bind it to the host and port
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen(1)  # Allow only one client to connect at a time

print(f"Server is listening on {HOST}:{PORT}")

while True:
    # Accept a client connection
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address}")

    try:
        # Receive the requested filename from the client
        filename = client_socket.recv(1024).decode('utf-8')

        # Build the full path to the requested file
        file_path = os.path.join(SHARED_DIRECTORY, filename)

        # Check if the file exists
        if os.path.isfile(file_path):
            # Send the file size to the client
            file_size = os.path.getsize(file_path)
            client_socket.send(str(file_size).encode('utf-8'))

            # Send the file contents in chunks
            with open(file_path, 'rb') as file:
                data = file.read(1024)
                while data:
                    client_socket.send(data)
                    data = file.read(1024)

            print(f"Sent '{filename}' to {client_address}")
        else:
            # If the file doesn't exist, send an error message
            client_socket.send(b'File not found')

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the client socket
        client_socket.close()
