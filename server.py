import socket
import threading
import time
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
from screeninfo import get_monitors

# Server configuration
SERVER_IP = '0.0.0.0'  # Listen on all available interfaces
SERVER_PORT = 5000
client_socket = None

# Global variables
mouse_on_client = False
monitor = get_monitors()[0]  # Get primary monitor dimensions
screen_width = monitor.width
screen_height = monitor.height
edge_threshold = 50  # Increased threshold to detect edge properly
switch_cooldown = 1  # Cooldown in seconds to avoid flickering between screens

last_switch_time = time.time()  # To track cooldown

# Function to send mouse data to client
def send_mouse_event(x, y, button, pressed):
    if client_socket:
        client_socket.send(f"MOUSE,{x},{y},{button},{pressed}".encode())

# Function to send keyboard data to client
def send_keyboard_event(key, pressed):
    if client_socket:
        client_socket.send(f"KEYBOARD,{key},{pressed}".encode())

# Check if the mouse is at the right edge of the screen
def is_mouse_on_client(x, y):
    global mouse_on_client, last_switch_time
    current_time = time.time()

    # Avoid switching back and forth too quickly
    if current_time - last_switch_time < switch_cooldown:
        return mouse_on_client  # Keep current state

    # If mouse reaches the right edge of the screen
    if x >= screen_width - edge_threshold:
        if not mouse_on_client:
            print("Switching mouse to client screen")
            send_mouse_event(x, y, None, True)  # Send event to make mouse visible on the client
            last_switch_time = current_time  # Update the last switch time
        mouse_on_client = True
        return True
    else:
        if mouse_on_client:
            print("Switching mouse to server screen")
            last_switch_time = current_time  # Update the last switch time
        mouse_on_client = False
        return False

# Mouse event listener
def on_move(x, y):
    if is_mouse_on_client(x, y):
        # Send events to the client
        send_mouse_event(x, y, None, None)  # Mouse movement on client screen
    else:
        # Mouse is still on the server screen, no event sent to the client
        pass

def on_click(x, y, button, pressed):
    if mouse_on_client:
        # If mouse is on the client, send click event to the client
        send_mouse_event(x, y, button, pressed)

# Keyboard event listener
def on_press(key):
    if mouse_on_client:
        # Send keyboard event to the client if mouse is on the client screen
        send_keyboard_event(key, True)

def on_release(key):
    if mouse_on_client:
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
    global client_socket
    client_socket = client_sock
    print(f"Client {client_socket.getpeername()} connected")

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
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == '__main__':
    start_server()