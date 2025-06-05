import socket
import threading
import random

HOST = '0.0.0.0'
PORT = 12345
MAX_PLAYERS = 4
connected_count = 1
player_number = None

clients = []  # Ahora será [(conn, addr)]
server_socket = None
lock = threading.Lock()

on_bomb_role = None
on_manual_role = None
assigned_role = None

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # print("[🌐] Intentando obtener la IP local... ",s)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def handle_client(conn, addr):
    print(f"[+] Cliente conectado desde {addr}")
    with lock:
        player_number = len(clients) + 1
        clients.append((conn, addr, player_number))

    # Enviar al nuevo cliente su número
    try:
        conn.send(f"player:{player_number}".encode())
        print(f"[🎮] Jugador {player_number} asignado a {addr}")
    except:
        pass

    # Enviar update a todos
    broadcast_connected_players()

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
    except:
        pass
    finally:
        with lock:
            for c in clients:
                if c[0] == conn:
                    clients.remove(c)
                    break
        conn.close()
        broadcast_connected_players()

def broadcast_connected_players():
    with lock:
        for idx, (conn, _, _) in enumerate(clients):
            try:
                conn.send(f"player:{idx+1}".encode())
                conn.send(f"update:{len(clients)}".encode())
            except:
                pass



def get_connected_count():
    return len(clients)


def assign_roles():
    with lock:
        if len(clients) == 0:
            print("[❌] No hay jugadores conectados.")
            return

        bomb_index = random.randint(0, len(clients) - 1)
        print(f"[🎲] Jugador {bomb_index + 1} tendrá la bomba.")

        for idx, (conn, addr, _) in enumerate(clients):
            role = "bomb" if idx == bomb_index else "manual"
            try:
                conn.send(role.encode())
            except Exception as e:
                print(f"[❌] Error enviando rol al jugador {idx + 1}: {e}")

        # Cierra el servidor si quieres evitar más conexiones
        if server_socket:
            try:
                server_socket.close()
                print("[🛑] Servidor cerrado después de asignar roles.")
            except Exception as e:
                print(f"[❌] Error cerrando servidor: {e}")


def trigger_role_assignment():
    if len(clients) < 2:
        print("[⛔] No se puede iniciar la partida: mínimo 2 jugadores.")
        return
    assign_roles()



def start_server():
    global server_socket, clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    ip= get_local_ip()
    print(f"[🎮] Servidor iniciado en {HOST}:{PORT}")
    print(f"[🌐] IP del host (local): {ip}")
    clients = []

    def accept_clients():
        try:
            while len(clients) < MAX_PLAYERS:
                conn, addr = server_socket.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except OSError:
            print("[🛑] accept_clients detenido porque el socket fue cerrado.")


    threading.Thread(target=accept_clients, daemon=True).start()
    return ip


def connect_to_server_as_host():
    global client_socket, assigned_role
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', PORT))
        print("[✅] Host conectado a sí mismo como cliente")
        assigned_role = None  # Inicializa el rol como None

        def listen_for_role():
            global connected_count, player_number, assigned_role
            while True:
                try:
                    data = client_socket.recv(1024).decode()
                    if data.startswith("player:"):
                        player_number = int(data.split(":")[1])
                    elif data.startswith("update:"):
                        connected_count = int(data.split(":")[1])
                    elif data in ["bomb", "manual"]:
                        print(f"[🎭] Te tocó el rol: {data}")
                        assigned_role = data  # Guarda el rol, no lo ejecutes aquí
                except:
                    break


        threading.Thread(target=listen_for_role, daemon=True).start()

    except Exception as e:
        print(f"[❌] Error al conectarse como host: {e}")


client_socket = None

def connect_to_server(server_ip):
    global client_socket, assigned_role

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, PORT))
        print("[✅] Conectado al servidor")
        assigned_role = None  # Inicializa el rol como None

        def listen_for_role():
            global connected_count, player_number, assigned_role
            while True:
                try:
                    data = client_socket.recv(1024).decode()
                    if data.startswith("player:"):
                        player_number = int(data.split(":")[1])
                    elif data.startswith("update:"):
                        connected_count = int(data.split(":")[1])
                    elif data in ["bomb", "manual"]:
                        print(f"[🎭] Te tocó el rol: {data}")
                        assigned_role = data  # Guarda el rol, no lo ejecutes aquí

                except:
                    break



        threading.Thread(target=listen_for_role, daemon=True).start()

    except Exception as e:
        print(f"[❌] No se pudo conectar: {e}")
        return False
    return True