import socket
import threading
import pyautogui

# Client configuration
SERVER_IP = '192.168.x.x'  # Replace with the server's IP address
SERVER_PORT = 5000

# Function to handle incoming server messages and simulate mouse/keyboard
def handle_server_message(client_socket):
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            data_parts = data.split(',')
            
            if data_parts[0] == "MOUSE":
                x, y = int(data_parts[1]), int(data_parts[2])
                button = data_parts[3]
                pressed = data_parts[4] == 'True'

                if button is None:
                    # Move the cursor to the given coordinates
                    pyautogui.moveTo(x, y)
                elif button == 'Button.left' and pressed:
                    pyautogui.click(x, y)
                elif button == 'Button.right' and pressed:
                    pyautogui.rightClick(x, y)

            elif data_parts[0] == "KEYBOARD":
                key = data_parts[1]
                pressed = data_parts[2] == 'True'
                
                # Handle special key cases (e.g., key format varies for control, shift)
                if pressed:
                    pyautogui.press(key)
                else:
                    pyautogui.keyUp(key)

        except Exception as e:
            print(f"Error: {e}")
            break

# Start the client to connect to the server and listen for input events
def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))

    client_thread = threading.Thread(target=handle_server_message, args=(client_socket,))
    client_thread.start()

if __name__ == '__main__':
    start_client()