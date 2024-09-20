import socket
import threading
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener

# Server configuration
SERVER_IP = '0.0.0.0'  # Listen on all available interfaces
SERVER_PORT = 5000
connected_client_socket = None  # Renamed to avoid conflict

# Function to send mouse data to client
def send_mouse_event(x, y, button, pressed):
    if connected_client_socket:
        connected_client_socket.send(f"MOUSE,{x},{y},{button},{pressed}".encode())

# Function to send keyboard data to client
def send_keyboard_event(key, pressed):
    if connected_client_socket:
        connected_client_socket.send(f"KEYBOARD,{key},{pressed}".encode())

# Mouse event listener
def on_click(x, y, button, pressed):
    send_mouse_event(x, y, button, pressed)

def on_move(x, y):
    send_mouse_event(x, y, None, None)  # For mouse movement

# Keyboard event listener
def on_press(key):
    send_keyboard_event(key, True)

def on_release(key):
    send_keyboard_event(key, False)

# Start mouse and keyboard listeners
def start_listening():
    mouse_listener = MouseListener(on_click=on_click, on_move=on_move)
    keyboard_listener = KeyboardListener(on_press=on_press, on_release=on_release)

    mouse_listener.start()
    keyboard_listener.start()

    mouse_listener.join()
    keyboard_listener.join()

# Handle client connections
def handle_client(client_sock):
    global connected_client_socket
    connected_client_socket = client_sock  # Reassign to global variable
    print(f"Client {connected_client_socket.getpeername()} connected")

    try:
        start_listening()
    except Exception as e:
        print(f"Error: {e}")

# Start the server to listen for clients
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(1)
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        client_sock, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_sock,))
        client_thread.start()

if __name__ == '__main__':
    start_server()
