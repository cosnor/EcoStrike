from __future__ import annotations
import pygame
import network
import ipaddress
from pygame.locals import *
from juego.button import *
from juego.bomba import Bomba
from juego.modulos import *
from juego.dialogpanel import dialog
from juego.listadoble import *
from juego.frontendfunctions import *
import time

import asyncio
import threading
import json

import asyncio
import websockets

pygame.init()
screen = pygame.display.set_mode((1000,562))
pygame.display.set_caption("EcoStrike")
icon = pygame.image.load("src/graphics/icono.png")
pygame.display.set_icon(icon)
clock = pygame.time.Clock()

BLACK = pygame.Color("#0a100d")
ORANGE = pygame.Color("#f34213")
GREEN = pygame.Color('#588157')
GOLD = pygame.Color('#fcbf49')
VANILLA = pygame.Color('#e9eb9e')
WHITE = pygame.Color("#ffffff")
GOLDEN = pygame.Color('#fcbf49')
SILVER = pygame.Color('#dbd4d3')
font = pygame.font.Font("src/font/Pixeled.ttf", 20)
font1 = pygame.font.Font("src/font/Pixeled.ttf", 40)

frame = pygame.Surface((680,460))
module1 = pygame.Surface((202,202))
module2 = pygame.Surface((202,202))
module3 = pygame.Surface((202,202))
module4 = pygame.Surface((202,202))
module5 = pygame.Surface((202,202))
timer = pygame.Surface((202,202))
album_bg = pygame.Surface((680,460))

frame.fill(GREEN)
module1.fill(VANILLA)
module2.fill(VANILLA)
module3.fill(VANILLA)
module4.fill(VANILLA)
module5.fill(VANILLA)
timer.fill(VANILLA)

bombas_desactivadas = 6

click = False

HOST = '192.168.1.26'  # Cambiar por IP real del host
PORT = 8765

responses = []
resp_bas = None
resp_comp = None
global bombita 


async def rules(simple, complejo):
    url = "ws://192.168.1.26:8765"
    
    try:
        async with websockets.connect(url, ping_interval=None) as websocket:
            print("🔌 Connected to server")
            
            # Crear una tarea en segundo plano para recibir mensajes
            async def receive_messages():
                while True:
                    try:
                        responses = []
                        response = await websocket.recv()
                        responses.append(response)
                        
                        # Guardar las respuestas en las variables globales
                        if len(responses) == 1:
                            resp_bas = response
                        elif len(responses) == 2:
                            resp_comp = response
                            
                        print("\n📥 Received instructions:")
                        print(f"{response}")
                        print("-" * 50 + "\n")
                        
                        # Si recibimos señal de finalización
                        if response == "COMPLETED" or response == "ERROR":
                            return
                            
                    except websockets.exceptions.ConnectionClosed:
                        print("Connection closed by server")
                        return
                    except Exception as e:
                        print(f"Error receiving message: {e}")
                        return
            
            # Enviar reglas y mantener conexión
            try:
                # Primero enviar todas las reglas
                for key, value in simple.items():
                    await websocket.send("\""+value+"\"")
                    await asyncio.sleep(0.1)  # Pequeña pausa entre envíos
                
                for key, value in complejo.items():
                    await websocket.send("\""+value+"\"")
                    await asyncio.sleep(0.1)  # Pequeña pausa entre envíos
                
                # Iniciar tarea de recepción
                receiver_task = asyncio.create_task(receive_messages())
                
                # Esperar a que termine la tarea de recepción
                await receiver_task
                
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed while sending")
            except Exception as e:
                print(f"Error while sending: {e}")
                
    except websockets.exceptions.ConnectionError:
        print("❌ Could not connect to the server")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        

# Create a function to run the asyncio event loop in a separate thread
def run_async_loop(loop, rules_coro):
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(rules_coro)
    except Exception as e:
        print(f"Error in async loop: {e}")
    finally:
        loop.close()

tutorial_shown = False  # Variable global para controlar si ya se mostró el tutorial
def new_menu():
    global tutorial_shown
    dialogControl = not tutorial_shown
    if not tutorial_shown:
        tutorial_shown = True

    fontbold = pygame.font.Font("src/font/Pixeled.ttf", 10)
    pygame.font.Font.set_bold(fontbold, True)

    menubg = pygame.image.load("src/graphics/menu/menubg.png")
    playbutton = pygame.image.load("src/graphics/menu/playbutton.png")
    playbuttonh = pygame.image.load("src/graphics/menu/playbuttonh.png")
    creditsbutton = pygame.image.load("src/graphics/menu/albumbutton.png")
    creditsbuttonh = pygame.image.load("src/graphics/menu/albumbuttonh.png")
    quitbutton = pygame.image.load("src/graphics/menu/exitbutton.png")
    quitbuttonh = pygame.image.load("src/graphics/menu/exitbuttonh.png")

    hitboxcreditsbutton = pygame.Rect(250,390,120,70)
    hitboxplaybutton = pygame.Rect(440,380,125,90)
    hitboxquitbutton = pygame.Rect(635,380,110,75)
    pos = pygame.mouse.get_pos()

    while True:
        espacio_presionado = False
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                espacio_presionado = True
            # Mover la lógica de clicks aquí dentro
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hitboxplaybutton.collidepoint(pos):
                    crear_bomba()
                    opcJugar()
                elif hitboxcreditsbutton.collidepoint(pos):
                    album()
                elif hitboxquitbutton.collidepoint(pos):
                    pygame.quit()
                    exit()

        if dialogControl:
            terminado = dialog(screen, clock, espacio_presionado)
            if terminado:
                dialogControl = False
        else:
            screen.blit(menubg, (0,0))
            screen.blit(creditsbutton, (0,0))
            screen.blit(playbutton, (0,0))
            screen.blit(quitbutton, (0,0))

            if hitboxplaybutton.collidepoint(pos):
                screen.blit(playbuttonh, (0,0))
            if hitboxcreditsbutton.collidepoint(pos):
                screen.blit(creditsbuttonh, (0,0))
            if hitboxquitbutton.collidepoint(pos):
                screen.blit(quitbuttonh, (0,0))

        clock.tick(60)
        pygame.display.update()

click = False

def opcJugar():
    fondo = pygame.image.load("src/graphics/bombsettings/bombsettingsbg.png")
    menubg = pygame.image.load("src/graphics/background/background.png")
    screen.blit(menubg, (0,0))
    while True:
        screen.blit(fondo, (0,0))
        menu_button = Button(screen, 10, 10, 33, 33, "x", (0,0,0), 0)
        menu_button.draw()
        play_button = Button(screen, 620, 225, 200, 50, "CREAR", (0,0,0), 20) #150
        play_button.draw()
        play_button2 = Button(screen, 620, 375, 200, 50, "ENTRAR", (0,0,0), 20) #150
        play_button2.draw()
        font1 = pygame.font.Font("src/font/Pixeled.ttf", 20)
        text_surface = font1.render("¿PREPARADO?", True, (255, 255, 255))
        screen.blit(text_surface, (165, 135))
        textE = font1.render("CREA UNA SALA", True, (0, 0, 0))
        screen.blit(textE, (605, 150))
        textM = font1.render("ENTRA A UNA SALA", True, (0, 0, 0))
        screen.blit(textM, (575, 300))

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
            play_button.handle_event(event, lambda: create_room())
            play_button2.handle_event(event, lambda: join_room())
            menu_button.handle_event(event, lambda: new_menu())

        pygame.display.update()
        clock.tick(60)
        
def crear_bomba():
    
    bombita = Bomba(300, 3, 3, 10)
    bombita.asignar_modulos() # REGLAS
    for modulo in bombita.modulos:
        if modulo.nombre == "Cables Básicos":
            reglasBasico = modulo.reglas_config
            reglasBasicoOrganizado = organizar_json_cables_simples(reglasBasico)
            
        elif modulo.nombre == "Cables Complejos":
            reglasCompleja = modulo.reglas_config
            reglasComplejaOrganizado = organizar_json_cables_complejos(reglasCompleja)
    # Crear un loop de eventos asyncio
    new_loop = asyncio.new_event_loop()
    rules_thread = threading.Thread(
        target=run_async_loop,
        args=(new_loop, rules(reglasBasicoOrganizado, reglasComplejaOrganizado))
    )
    rules_thread.daemon = True  # Thread will close when main program exits
    rules_thread.start()

def create_room():
    partida_iniciada = False
    ip = network.start_server()
    network.connect_to_server_as_host()
    fondo = pygame.image.load("src/graphics/bombsettings/bombsettingsbg.png")
    menubg = pygame.image.load("src/graphics/background/background.png")
    screen.blit(menubg, (0,0))
    while True:
        screen.blit(fondo, (0,0))
        menu_button = Button(screen, 10, 10, 33, 33, "x", (0,0,0), 0)
        menu_button.draw()
        # Aquí puedes agregar más elementos de configuración de la sala
        font1 = pygame.font.Font("src/font/Pixeled.ttf", 20)
        font2 = pygame.font.Font("src/font/Pixeled.ttf", 15)
        lineas = "ESPERANDO\nJUGADORES".split('\n')
        varias_lineas(screen, font1, lineas, 135, 190)
        textoIP = "IP DE LA SALA"
        screen.blit(font1.render(textoIP, True, (255, 255, 255)), (175, 320))
        rectipo = pygame.Rect(150, 400, 250, 40)
        textoIP2 = ip
        centrar_texto(screen, rectipo, font2, font2.render(textoIP2, True, (255, 255, 255)))
        textE = font1.render("JUGADORES", True, (0, 0, 0))
        screen.blit(textE, (625, 150))
        inicio_game_button = Button(screen, 620, 400, 200, 50, "INICIAR", (0,0,0), 20)
        inicio_game_button.draw()
        
        jugadores_conectados = []
        for i in range(network.connected_count):
            label = f"Jugador {i+1}"
            if i+1 == network.player_number:
                label += " (You)"
            jugadores_conectados.append(label)
        
        dibujar_jugadores(screen, font2, jugadores_conectados, 635, 200)

        puede_iniciar = network.connected_count >= 2
        color_boton = (0, 0, 0) if puede_iniciar else (100, 100, 100)  # Gris si no puede iniciar
        inicio_game_button = Button(screen, 620, 400, 200, 50, "INICIAR", color_boton, 20)
        inicio_game_button.draw()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Vuelve al menú anterior
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    menu_button.handle_event(event, lambda: opcJugar())
                    if puede_iniciar: 
                        print("Iniciando partida...")
                        if not partida_iniciada:
                            inicio_game_button.handle_event(event, lambda: iniciar_partida())

        def iniciar_partida():
            nonlocal partida_iniciada
            partida_iniciada = True
            network.trigger_role_assignment()
        if network.assigned_role == "bomb":
            print("..Rol asignado: Bomba")
            game()
            return
        elif network.assigned_role == "manual":
            print("..Rol asignado: Manual")
            show_manual()
            return
        
        pygame.display.update()
        clock.tick(60)

def obtener_ip_input(event, active, user_text):
    """Maneja la entrada de texto para el input box de IP"""
    if not active:
        return user_text, False

    if event.type != pygame.KEYDOWN:
        return user_text, False

    if event.key == pygame.K_RETURN and user_text:
        return user_text, True
    elif event.key == pygame.K_BACKSPACE:
        return user_text[:-1], False
    elif len(user_text) < 15:  # Limita la longitud de la IP
        return user_text + event.unicode, False
    return user_text, False

def join_room():
    fondo = pygame.image.load("src/graphics/bombsettings/bombsettingsbg.png")
    menubg = pygame.image.load("src/graphics/background/background.png")
    screen.blit(menubg, (0,0))
    font1 = pygame.font.Font("src/font/Pixeled.ttf", 20)
    font2 = pygame.font.Font("src/font/Pixeled.ttf", 15)
    input_box = pygame.Rect(570, 235, 400, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    user_text = ""
    ip_ingresada = ""

    while True:
        screen.blit(fondo, (0,0))
        menu_button = Button(screen, 10, 10, 33, 33, "x", (0,0,0), 0)
        menu_button.draw()
        lineas = "INGRESA A\nUNA PARTIDA".split('\n')
        varias_lineas(screen, font1, lineas, 135, 190)
        textE = font1.render("IP DE LA SALA", True, (0, 0, 0))
        screen.blit(textE, (620, 150))

        # Dibuja el text box
        txt_surface = font2.render(user_text, True, (0, 0, 0))
        width = 300
        input_box.w = width
        pygame.draw.rect(screen, color, input_box, 2)
        centrar_texto(screen, input_box, font2, txt_surface)

        inicio_game_button = Button(screen, 620, 320, 200, 50, "ENTRAR", (0,0,0), 20)
        inicio_game_button.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if input_box.collidepoint(event.pos):
                        active = not active
                    else:
                        active = False
                    color = color_active if active else color_inactive
                    menu_button.handle_event(event, lambda: new_menu())    
                    inicio_game_button.handle_event(event, lambda: preroom(user_text))
                        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                # Maneja la entrada de texto
                nuevo_texto, enter_presionado = obtener_ip_input(event, active, user_text)
                user_text = nuevo_texto
                if enter_presionado:
                    preroom(user_text)

        pygame.display.update()
        clock.tick(60)

def es_ip_valida(ip: str): 
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False
    
def preroom(ip_ingresada):
    """Función que se llama al presionar el botón de entrar a la sala"""
    if not ip_ingresada or not es_ip_valida(ip_ingresada):
        # Si la IP no es válida, muestra un diálogo de error
        print("IP inválida. Por favor, ingresa una IP válida.")
        return
    room(ip_ingresada)

def room(ip):
    conectado = network.connect_to_server(ip)
    if not conectado:
        print("No se pudo conectar al servidor. Verifica la IP e intenta nuevamente.")
        return
    fondo = pygame.image.load("src/graphics/bombsettings/bombsettingsbg.png")
    menubg = pygame.image.load("src/graphics/background/background.png")
    screen.blit(menubg, (0,0))
    while True:
        screen.blit(fondo, (0,0))
        menu_button = Button(screen, 10, 10, 33, 33, "x", (0,0,0), 0)
        menu_button.draw()
        # Aquí puedes agregar más elementos de configuración de la sala
        font1 = pygame.font.Font("src/font/Pixeled.ttf", 20)
        font2 = pygame.font.Font("src/font/Pixeled.ttf", 15)
        lineas = "ESPERANDO\nJUGADORES".split('\n')
        varias_lineas(screen, font1, lineas, 135, 190)
        textoIP = "IP DE LA SALA"
        screen.blit(font1.render(textoIP, True, (255, 255, 255)), (175, 320))
        rectipo = pygame.Rect(150, 400, 250, 40)
        textoIP2 = ip
        centrar_texto(screen, rectipo, font2, font2.render(textoIP2, True, (255, 255, 255)))
        textE = font1.render("JUGADORES", True, (0, 0, 0))
        screen.blit(textE, (625, 150))
        jugadores_conectados = []
        player_num = getattr(network, "player_number", None)
        count = getattr(network, "connected_count", 1)
        
        for i in range(count):
            label = f"Jugador {i+1}"
            if player_num is not None and i+1 == player_num:
                label += " (You)"
            jugadores_conectados.append(label)
        dibujar_jugadores(screen, font2, jugadores_conectados, 635, 200)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Vuelve al menú anterior
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    menu_button.handle_event(event, lambda: new_menu())

        if network.assigned_role == "bomb":
            print("..Rol asignado: Bomba")
            game()  # Llama a la función del juego
            return
        elif network.assigned_role == "manual":
            print("..Rol asignado: Manual")
            show_manual()  # Llama a la función del manual
            return
        
        pygame.display.update()
        clock.tick(60)

def album(): 
    fondo = pygame.image.load("src/graphics/bombsettings/bombsettingsbg.png")
    menubg = pygame.image.load("src/graphics/background/background.png")
    screen.blit(menubg, (0,0))
    while True:
        screen.blit(fondo, (0,0))
        menu_button = Button(screen, 10, 10, 33, 33, "x", (0,0,0), 0)
        menu_button.draw()
        # Aquí puedes agregar más elementos de configuración de la sala
        font1 = pygame.font.Font("src/font/Pixeled.ttf", 20)
        font2 = pygame.font.Font("src/font/Pixeled.ttf", 15)
        lineas = "MI ALBUM\nDE RECUERDOS".split('\n')
        varias_lineas(screen, font1, lineas, 145, 160)
        textE = font1.render("MI COLECCION", True, (0, 0, 0))
        textE2 = font1.render("CREDITOS", True, (0, 0, 0))
        screen.blit(textE, (615, 150))
        boton_coleccion = Button(screen, 620, 225, 200, 50, "VER", (0,0,0), 20)
        screen.blit(textE2, (645, 300))
        boton_creditos = Button(screen, 620, 370, 200, 50, "VER", (0,0,0), 20)
        boton_creditos.draw()
        boton_coleccion.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Vuelve al menú anterior
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    menu_button.handle_event(event, lambda: new_menu())
                    boton_coleccion.handle_event(event, lambda: coleccion())
                    boton_creditos.handle_event(event, lambda: creditos())
        pygame.display.update()
        clock.tick(60)

def coleccion():
    
    menubg = pygame.image.load("src/graphics/background/background_dialog_11.png")
    fondo_coleccion = pygame.image.load("src/graphics/album/coleccionbg.png")
    signo11 = pygame.image.load("src/graphics/album/signo11.png")
    signo12 = pygame.image.load("src/graphics/album/signo12.png")
    signo21 = pygame.image.load("src/graphics/album/signo21.png")
    signo22 = pygame.image.load("src/graphics/album/signo22.png")
    badge1 = pygame.image.load("src/graphics/album/badge1.png")
    badge2 = pygame.image.load("src/graphics/album/badge2.png")
    badge3 = pygame.image.load("src/graphics/album/badge3.png")
    badge4 = pygame.image.load("src/graphics/album/badge4.png")
    
    screen.blit(menubg, (0,0))
    
    while True:
        screen.blit(fondo_coleccion, (0,0))
        menu_button = Button(screen, 10, 10, 33, 33, "x", (0,0,0), 0)
        menu_button.draw()
        
        if bombas_desactivadas == 0: 
            screen.blit(signo11, (0,0))
            screen.blit(signo12, (0,0))
            screen.blit(signo21, (0,0))
            screen.blit(signo22, (0,0))
        elif bombas_desactivadas == 1:
            screen.blit(badge1, (0,0))
            screen.blit(signo12, (0,0))
            screen.blit(signo21, (0,0))
            screen.blit(signo22, (0,0))
        elif bombas_desactivadas == 2:
            screen.blit(badge1, (0,0))
            screen.blit(badge2, (0,0))
            screen.blit(signo21, (0,0))
            screen.blit(signo22, (0,0))
        elif bombas_desactivadas == 3:
            screen.blit(badge1, (0,0))
            screen.blit(badge2, (0,0))
            screen.blit(badge3, (0,0))
            screen.blit(signo22, (0,0))
        elif bombas_desactivadas >= 4:
            screen.blit(badge1, (0,0))
            screen.blit(badge2, (0,0))
            screen.blit(badge3, (0,0))
            screen.blit(badge4, (0,0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Vuelve al menú anterior
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    menu_button.handle_event(event, lambda: new_menu())
        pygame.display.update()
        clock.tick(60)


def show_manual():
    menubg = pygame.image.load("src/graphics/background/background_dialog_11.png")
    fondo_manual = pygame.image.load("src/graphics/background/manualbg.png")
    font_manual = pygame.font.Font("src/font/Montserrat-Regular.ttf", 9)
    header_font = pygame.font.Font("src/font/Pixeled.ttf", 18)
    subheader_font = pygame.font.Font("src/font/Montserrat-Regular.ttf", 15)
    screen.blit(menubg, (0,0))
    menu_button = Button(screen, 10, 10, 33, 33, "x", (0,0,0), 0)
    menu_button.draw()

    
    texto1 = ['Para C1: - Si el reciclaje no tiene ningún beneficio para el medio ambiente: \nLos aerosoles naturales no tienen ningún impacto en el clima.\nVerdadero (Hacer A)\nFalso (Hacer B)\n- El cambio climático solo afecta a las regiones polares.\nSolo los gobiernos pueden hacer algo frente al cambio climático.\nVerdadero (Hacer A)\nFalso (Hacer B)\n- Las emisiones de dióxido de carbono son la principal causa del cambio climático.\nEl plástico es biodegradable en menos de 10 años.\nVerdadero (Hacer A)\nFalso (Hacer B)\n- Los océanos absorben parte del CO₂ emitido por los humanos.\nLas emisiones de dióxido de carbono son la principal causa del cambio climático.\nVerdadero (Hacer A)\nFalso (Hacer B)', 'Para C4: - Si el reciclaje no tiene ningún beneficio para el medio ambiente: \nEl plástico es biodegradable en menos de 10 años.\nVerdadero (Hacer A)\nFalso (Hacer B)\n- La energía nuclear no emite gases de efecto invernadero durante su operación:\nLas emisiones de dióxido de carbono son la principal causa del cambio climático.\nVerdadero (Hacer A)\nFalso (Hacer B)\n- Los océanos absorben parte del CO₂ emitido por los humanos:\nLos aerosoles naturales tienen un impacto mayor que el calentamiento global.\nVerdadero (Hacer A)\nFalso (Hacer B)', 'Para C3: - Si el reciclaje no tiene ningún beneficio para el medio ambiente: \nLos aerosoles naturales no tienen ningún impacto en el clima. \nLas emisiones de dióxido de carbono son la principal causa del cambio climático. \nEl calentamiento global solo afecta a las regiones polares. \nSolo los gobiernos pueden hacer algo frente al cambio climático. \nLa deforestación contribuye al cambio climático. \nReciclar papel ayuda a conservar los árboles. \nLos océanos absorben parte del CO₂ emitido por los humanos. \nLas energías renovables no generan ningún tipo de contaminación. \nLos océanos absorben parte del CO₂ emitido por los humanos. \nLas energías renovables no generan ningún tipo de contaminación. \nLos océanos absorben parte del CO₂ emitido por los humanos. \nLas energías renovables no generan ningún tipo de contaminación. \nEl plástico es biodegradable en menos de 10 años. \nLos océanos absorben parte del CO₂ emitido por los humanos. \nLas energias renovables no generan ningún tipo de contaminación. \nLos océanos absorben parte del CO₂ emitido por los humanos. \nLas energias renovables no generan ningún tipo de contaminación. \nLos océanos absorben parte del CO₂ emitido por los humanos. \nLas energias renovables no generan ningún tipo de contaminación. \nLos océanos absorben parte del CO₂ emitido por los humanos. \nLas energias renovables no generan ningún tipo de contaminación. \nLas energias renovables no generan ningún tipo de contaminación. \nLas energias renovables no generan ningún tipo de contaminación. \nLas energias renovables no generan ningún tipo de contaminación. \nEl deshielo de los polos puede elevar el n', 'Para C2: - Si el reciclaje no tiene ningún beneficio para el medio ambiente: \nLas energías renovables no generan ningún tipo de contaminación.\nVerdadero (Hacer A)\nFalso (Hacer B)\n- El calentamiento global es un mito creado por científicos:\nEl deshielo de los polos puede elevar el nivel del mar.\nVerdadero (Hacer A)\nFalso (Hacer B)\n- La deforestación contribuye al cambio climático:\nLos aerosoles naturales no tienen ningún impacto en el clima.\nVerdadero (Hacer A)\nFalso (Hacer B)']
    texto2 =texto1
    
    # texto1 = resp_bas
    # texto2 = resp_comp
    
    texto1 = lista_a_texto(texto1)
    texto2 = lista_a_texto(texto2)
    
    # Crear dos rectángulos para el texto
    rect_texto1 = pygame.Rect(75, 70, 400, 425)  # Rectángulo izquierdo
    rect_texto2 = pygame.Rect(555, 75, 360, 365)  # Rectángulo derecho
    
    # Dividir el texto en líneas
    lineas_texto1 = texto1.split('\n')
    lineas_texto2 = texto2.split('\n')

    scroll_y = 0
    scroll_speed = 20
    
    # Nuevo botón para ver diagrama
    ver_diagrama_button = Button(screen, 575, 450, 300, 45, "Ver Tabla", (0,0,0), 12)
    mostrar_diagrama = False
    
    # Superficie para el diagrama superpuesto
    diagrama_surface = pygame.Surface((800, 400))
    diagrama_surface.fill((0, 0, 0))  # Color negro
    diagrama_rect = diagrama_surface.get_rect(center=(500, 281))  # Centrado en pantalla


    # Configuración de la tabla
    tabla_font = pygame.font.Font("src/font/Montserrat-Regular.ttf", 14)
    encabezados = ["Naranja", "Morado", "LED", "Conectado a", "Acción"]
    num_filas = 13  # 1 fila de encabezado + 8 filas de datos
    num_columnas = 5
    celda_ancho = 155
    celda_alto = 30
    tabla_ancho = ( celda_ancho * num_columnas ) +2
    tabla_alto = (celda_alto * num_filas) + 2
    
    # Crear superficie para la tabla centrada en el diagrama
    tabla_surface = pygame.Surface((tabla_ancho, tabla_alto))
    tabla_surface.fill((0, 0, 0))  # Fondo negro
    tabla_rect = tabla_surface.get_rect(center=(500, 281))
    
    def dibujar_tabla():
        # Dibujar líneas de la tabla
        for i in range(num_filas + 1):
            pygame.draw.line(tabla_surface, (255, 255, 255), 
                           (0, i * celda_alto), 
                           (tabla_ancho, i * celda_alto), 2)
        for j in range(num_columnas + 1):
            pygame.draw.line(tabla_surface, (255, 255, 255), 
                           (j * celda_ancho, 0), 
                           (j * celda_ancho, tabla_alto), 2)
        
        # Dibujar encabezados
        for col, texto in enumerate(encabezados):
            surf = tabla_font.render(texto, True, (255, 255, 255))
            rect = surf.get_rect(center=(col * celda_ancho + celda_ancho//2, celda_alto//2))
            tabla_surface.blit(surf, rect)
        
        for modulo in bombita.modulos:
            if modulo.nombre == "Cables Complejos":
                reglasCompleja = modulo.reglas_config
                
        filas = formatear_reglas_para_tabla(reglasCompleja)

        for i, fila in enumerate(filas):
                llenar_fila(i, fila)
                
    def llenar_fila(fila, datos):
        for col, texto in enumerate(datos):
            surf = tabla_font.render(str(texto), True, (255, 255, 255))
            rect = surf.get_rect(center=(col * celda_ancho + celda_ancho//2, 
                                       (fila + 1) * celda_alto + celda_alto//2))
            tabla_surface.blit(surf, rect)

    # Dibujar la tabla base
    dibujar_tabla()

    while True:
        screen.blit(menubg, (0,0))
        screen.blit(fondo_manual, (0,0))
        
        # Dibuja los textos con scroll
        altura_total1 = varias_lineas_con_scroll(screen, font_manual, lineas_texto1, rect_texto1, scroll_y, header_text="MANUAL DEL ACTUADOR", header_font=header_font, subheader_text="Cables Simples"  ,subheader_font=subheader_font)
        altura_total2 = varias_lineas_con_scroll(screen, font_manual, lineas_texto2, rect_texto2, scroll_y, None, None, subheader_text="Cables Complejos", subheader_font=subheader_font)
        # Dibuja el botón de ver diagrama
        ver_diagrama_button.draw()

        # Si el diagrama está activo, dibújalo sobre todo
        if mostrar_diagrama:
            # Capa semi-transparente de fondo
            s = pygame.Surface((1000,562))
            s.set_alpha(128)
            s.fill((0,0,0))
            screen.blit(s, (0,0))
            
            # Dibuja el diagrama
            screen.blit(diagrama_surface, diagrama_rect)
            
            # Dibuja la tabla
            screen.blit(tabla_surface, tabla_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    menu_button.handle_event(event, lambda: new_menu())
                    if mostrar_diagrama:
                        # Clic fuera del diagrama lo cierra
                        if not diagrama_rect.collidepoint(event.pos):
                            mostrar_diagrama = False
                    else: 
                        menu_button.handle_event(event, lambda: new_menu())
                        if ver_diagrama_button.rect.collidepoint(event.pos):
                            mostrar_diagrama = True
                # Scroll con rueda del mouse
                elif event.button == 4:  # Scroll arriba
                    scroll_y = max(0, scroll_y - scroll_speed)
                elif event.button == 5:  # Scroll abajo
                    max_scroll = max(altura_total1, altura_total2) - rect_texto1.height
                    scroll_y = min(max_scroll, scroll_y + scroll_speed)
        
        pygame.display.update()
        clock.tick(60)

def creditos():
    creditos_movibles = [
    "", 
    "ECO STRIKE",
    "",
    "INTEGRANTES DEL GRUPO:",
    "1. MARÍA CAMILA OSORNO SUÁREZ",
    "2. ALBERTO JOSÉ SANDOVAL JIMENEZ",
    "3. EFRAIN ANDRÉS RADA SANZ", 
    "4. ALEJANDRA VALENCIA RUA",
    "5. JUAN MIGUEL CARRASQUILLA ESCOBAR",
    "6. PRESLY JAVIER ROMERO COLL"
    
    "",
    "PROFESORES:",
    "1. MARGARITA ROSA GAMARRA ACOSTA",
    "2. DANIEL ROMERO MARTÍNEZ",
    "3. EDUARDO ZUREK VARELA",
    
    "",
    "CONTRIBUCIONES:",
    "1. JUAN FELIFE SANTOS RODRIGUEZ",
    "2. SAMUEL MATIZ GARCÍA",
    ""
    ]
    start_time = time.time()

    fuente_creditos = pygame.font.Font("src/font/Pixeled.ttf", 24)

    posicionbajada = 0
    while True:
        screen.fill((255, 230, 167))
        posicion_y = 15
        # Dibuja cada línea de crédito
        for linea in creditos_movibles:
            credito_superficie = fuente_creditos.render(linea, True, ((67, 40, 24)))
            credito_rect = credito_superficie.get_rect(center=(1000 // 2, posicion_y-posicionbajada))
            screen.blit(credito_superficie, credito_rect)
            posicion_y += 40
        # Actualiza la pantalla
        current_time = time.time()
        if current_time - start_time >= 0.5:
            posicionbajada += 40 # Incrementar la posición vertical
            start_time = current_time  # Reiniciar el tiempo de inicio
        if posicionbajada >= 800:
            new_menu()
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()
        clock.tick(60)
def organizar_json_cables_complejos(data):

    def agrupar_por_acciones_c(data):
        # Diccionario para almacenar las agrupaciones por acción
        agrupaciones = {}
        
        # Procesar cada letra (A, B, etc.)
        for letra, entradas in data.items():
            # Filtrar solo entradas con acciones que empiecen por 'C'
            entradas_c = [entrada for entrada in entradas if entrada.get('accion', '').startswith('C')]
            
            # Agrupar por acción
            for entrada in entradas_c:
                accion = entrada['accion']
                
                # Inicializar la agrupación si no existe
                if accion not in agrupaciones:
                    agrupaciones[accion] = {}
                
                # Agregar la entrada a la letra correspondiente
                if letra not in agrupaciones[accion]:
                    agrupaciones[accion][letra] = []
                
                agrupaciones[accion][letra].append(entrada)
        
        # Convertir cada agrupación a string JSON
        jsons_agrupados = {}
        
        for accion, datos_accion in agrupaciones.items():
            # Crear el JSON para esta agrupación
            json_string = json.dumps(datos_accion, separators=(',', ':'), ensure_ascii=False)
            # Agregar escapes a las comillas
            json_escaped = json_string.replace('"', r'\"')
            jsons_agrupados[accion] = json_escaped
        
        return jsons_agrupados

    # Aplicar la función
    jsons_agrupados = agrupar_por_acciones_c(data)
    return(jsons_agrupados)

def organizar_json_cables_simples(data):
    # Orden deseado para los tipos
    orden_tipos = ['condicional', 'directa', 'indirecta', 'solo_cb']

    # Función para reorganizar una lista según el orden de tipos
    def reorganizar_por_tipo(lista):
        # Crear un diccionario para agrupar por tipo
        por_tipo = {}
        for item in lista:
            tipo = item['tipo']
            if tipo not in por_tipo:
                por_tipo[tipo] = []
            por_tipo[tipo].append(item)
        
        # Reorganizar según el orden deseado
        lista_ordenada = []
        for tipo in orden_tipos:
            if tipo in por_tipo:
                lista_ordenada.extend(por_tipo[tipo])
        
        return lista_ordenada

    # Aplicar la reorganización a cada clave del diccionario
    data_reorganizado = {}
    for clave, lista in data.items():
        data_reorganizado[clave] = reorganizar_por_tipo(lista)

    # Diccionario para guardar cada color como string JSON
    jsons_separados = {}

    # Separar cada color en su propio string JSON
    for color, datos in data_reorganizado.items():
        # Crear el contenido JSON para este color
        json_color = {color: datos}
        
        # Convertir a string JSON
        json_string = json.dumps(json_color, ensure_ascii=False)
        json_escaped = json_string.replace('"', r'\"')
        # Guardar en el diccionario
        jsons_separados[color] = json_escaped
    return jsons_separados


        


def game():
    # Duración del temporizador en segundos
    duration = 300
    remaining_time = duration
    # Obtener el tiempo de inicio
    start_time = time.time()
    control = [False]
    c=0
    a1 = 2
    a2 = 3
    running = True

    pos = [module1, module2, module3, module4, module5]

    while running:
        x = 0
        for modulo in bombita.modulos:
            modulo.modulo = pos[x]
            modulo.dibujarFondo(pos[x])
            if x < a2 -1:
                x= x+1
        bombita.colocarFranja(timer)
        x = 0
        fondo = pygame.image.load("src/graphics/background/background_dialog_11.png")
        screen.blit(fondo, (0,0))
        

        for modulo in bombita.modulos:
            if modulo.nombre == "Cables Básicos":
                if pos[x] == module1:
                    posCB = (180,71)
                elif pos[x] == module2:
                    posCB = (402,71)
                elif pos[x] == module3:
                    posCB = (625,71)
                elif pos[x] == module4:
                    posCB = (180,293)
                elif pos[x] == module5:
                    posCB = (402,293)
                modulo.rect_abs = (posCB[0], posCB[1], 202, 202)
                modulo.dibujarElementos(pos[x], screen, posCB)
                mod_cb = modulo

            elif modulo.nombre == "Cables Complejos":
                if pos[x] == module1:
                    posCC = (180,71)
                elif pos[x] == module2:
                    posCC = (402,71)
                elif pos[x] == module3:
                    posCC = (625,71)
                elif pos[x] == module4:
                    posCC = (180,293)
                elif pos[x] == module5:
                    posCC = (402,293)
                modulo.rect_abs = (posCC[0], posCC[1], 202, 202)
                modulo.dibujarElementos(pos[x], screen, posCC)
                mod_cc = modulo

            elif modulo.nombre == "Código":
                if pos[x] == module1:
                    posC = (180,71)
                elif pos[x] == module2:
                    posC = (402,71)
                elif pos[x] == module3:
                    posC = (625,71)
                elif pos[x] == module4:
                    posC = (180,293)
                elif pos[x] == module5:
                    posC = (402,293)
                modulo.rect_abs = (posC[0], posC[1], 202, 202)
                modulo.dibujarElementos(pos[x], screen, posC)
            elif modulo.nombre == "Memoria":
                if pos[x] == module1:
                    posM = (180,71)
                elif pos[x] == module2:
                    posM = (402,71)
                elif pos[x] == module3:
                    posM = (625,71)
                elif pos[x] == module4:
                    posM = (180,293)
                elif pos[x] == module5:
                    posM = (402,293)
                modulo.rect_abs = (posM[0], posM[1], 202, 202)
                modulo.dibujarElementos(pos[x], posM)
            elif modulo.nombre == "Exigente":
                if pos[x] == module1:
                    posexigente = (180,71)
                elif pos[x] == module2:
                    posexigente = (402,71)
                elif pos[x] == module3:
                    posexigente = (625,71)
                elif pos[x] == module4:
                    posexigente = (180,293)
                elif pos[x] == module5:
                    posexigente = (402,293)
                modulo.rect_abs = (posexigente[0], posexigente[1], 202, 202)
                modulo.dibujarElementos(pos[x],remaining_time,control, posexigente)
            if x < a2 -1:
                x= x+1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        #screen.blit(background, (0,0))
        screen.blit(frame, (165,56))
        screen.blit(module1, (180,71))
        screen.blit(module2, (402,71))
        screen.blit(module3, (625,71))
        screen.blit(module4, (180,293))
        screen.blit(module5, (402,293))
        screen.blit(timer, (625,293))


        mod_cb.C1.draw()
        mod_cb.C2.draw()
        mod_cb.C3.draw()
        mod_cb.C4.draw()

        mod_cc.C1.draw()
        mod_cc.C2.draw()
        mod_cc.C3.draw()
        mod_cc.C4.draw()

        # Calcular el tiempo restante
        current_time = time.time()
        elapsed_time = current_time - start_time
        remaining_time = max(duration - elapsed_time, 0)
        bombita.tiempo = remaining_time
        bombita.tiempo_agotado()
        bombita.equivocaciones_limite()
        bombita.victoria()
        if bombita.estado == "Detonada":
            terminarM(False, str(a2), time_text, str(bombita.equivocaciones), str(a1))
        if bombita.estado == "Desactivada":
            terminarM(True, str(a2), time_text, str(bombita.equivocaciones), str(a1))
        # Formatear el tiempo restante en formato mm:ss
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        time_text = f"{minutes:02d}:{seconds:02d}"

        # Renderizar el tiempo en la ventana
        text_surface = font.render(time_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(730,390))
        screen.blit(text_surface, text_rect)
        fondotimer = pygame.image.load("src/graphics/Modulo Timer/fondo_timer.png")
        timer.blit(fondotimer,(0,0))
        if bombita.errores == 0: #Aquí se podrían poner los sonidos de explosión tambien
            if bombita.equivocaciones == 1:
                fontE = pygame.font.Font("src/font/Pixeled.ttf", 15)
                text_surface = fontE.render("X", True, WHITE)
                text_rect = text_surface.get_rect(center=(102,157))
                timer.blit(text_surface, text_rect)
        if bombita.errores == 1:
            if bombita.equivocaciones == 1:
                fontE = pygame.font.Font("src/font/Pixeled.ttf", 15)
                text_surface = fontE.render("X", True, WHITE)
                text_rect = text_surface.get_rect(center=(102,157))
                timer.blit(text_surface, text_rect)
        if bombita.errores == 2:
            if bombita.equivocaciones == 1:
                fontE = pygame.font.Font("src/font/Pixeled.ttf", 10)
                text_surface = fontE.render("X", True, WHITE)
                text_rect = text_surface.get_rect(center=(102,157))
                timer.blit(text_surface, text_rect)
            if bombita.equivocaciones == 2:
                fontE = pygame.font.Font("src/font/Pixeled.ttf", 10)
                text_surface = fontE.render("XX", True, WHITE)
                text_rect = text_surface.get_rect(center=(102,157))
                timer.blit(text_surface, text_rect)
        if bombita.errores == 3:
            if bombita.equivocaciones == 1:
                fontE = pygame.font.Font("src/font/Pixeled.ttf", 10)
                text_surface = fontE.render("X", True, WHITE)
                text_rect = text_surface.get_rect(center=(102,157))
                timer.blit(text_surface, text_rect)
            if bombita.equivocaciones == 2:
                fontE = pygame.font.Font("src/font/Pixeled.ttf", 10)
                text_surface = fontE.render("XX", True, WHITE)
                text_rect = text_surface.get_rect(center=(102,157))
                timer.blit(text_surface, text_rect)
            if bombita.equivocaciones == 3:
                fontE = pygame.font.Font("src/font/Pixeled.ttf", 10)
                text_surface = fontE.render("XXX", True, WHITE)
                text_rect = text_surface.get_rect(center=(102,157))
                timer.blit(text_surface, text_rect)
        pygame.display.update()
        clock.tick(60)

def terminarM(desactivada, modulos, tiemporestante, errores, intentos):
        resultbg = pygame.image.load("src/graphics/Resultado/book.png")
        defusedstp = pygame.image.load("src/graphics/Resultado/desactivada.png")
        explodedstp = pygame.image.load("src/graphics/Resultado/detonada.png")
        font = pygame.font.Font("src/font/Pixeled.ttf", 10)
        fontbold = pygame.font.Font("src/font/Pixeled.ttf", 10)
        pygame.font.Font.set_bold(fontbold, True)
        bfont = pygame.font.Font("src/font/Pixeled.ttf", 12)

        # Variables para la pantalla de resultado
        #desactivada = True
        tiempo = "5:00"

        # Botones para la pantalla de resultado
        backbutton = pygame.Rect(595,370,95,40)
        retrybutton = pygame.Rect(720,370,135,40)
        continuebutton = pygame.Rect(650,370,120,40)

        # Texto para la pantalla de resultado
        bombconfigtxt = fontbold.render("AJUSTES DE LA BOMBA", True, 'black')
        timeconfigtxt = font.render(tiempo, True, 'black')
        moduleconfigtxt = font.render(modulos + " MÓDULOS", True, 'black')
        strikeconfigtxt = font.render(intentos + " INTENTOS", True, 'black')
        timetitletxt = fontbold.render("TIEMPO RESTANTE:", True, 'black')
        remtimetxt = font.render(tiemporestante, True, 'black')
        errorstitletxt = fontbold.render("ERRORES:", True, 'black')
        errorstxt = font.render(errores, True, 'black')

        menutxt = bfont.render("VOLVER", True, 'white')
        retrytxt = bfont.render("REINTENTAR", True, 'white')

        continuetxt = bfont.render("CONTINUAR", True, 'white')


        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if desactivada == True:
                        if continuebutton.collidepoint(event.pos):
                            # Aquí se debe volver al menú principal
                            new_menu()
                    else:
                        if backbutton.collidepoint(event.pos):
                            # Aquí se debe volver al menú principal
                            new_menu()
                        if retrybutton.collidepoint(event.pos):
                            # Aquí se debe volver a jugar
                            opcJugar()

            screen.fill((50,50,50))
            screen.blit(resultbg, (0,0))

            if desactivada == True:
                screen.blit(defusedstp, (0,0))
                pygame.draw.rect(screen, 0, continuebutton)
                screen.blit(continuetxt, (continuebutton.x + 10, continuebutton.y))
            else:
                screen.blit(explodedstp, (0,0))
                pygame.draw.rect(screen, 0, backbutton)
                pygame.draw.rect(screen, 0, retrybutton)
                screen.blit(menutxt, (backbutton.x + 10, backbutton.y))
                screen.blit(retrytxt, (retrybutton.x + 10, retrybutton.y))

            screen.blit(bombconfigtxt, (625, 100))
            screen.blit(timeconfigtxt, (580, 140))
            screen.blit(moduleconfigtxt, (655, 140))
            screen.blit(strikeconfigtxt, (770, 140))
            screen.blit(timetitletxt, (645, 235))
            screen.blit(remtimetxt, (700, 255))
            screen.blit(errorstitletxt, (680, 285))
            screen.blit(errorstxt, (710, 305))

            clock.tick(60)
            pygame.display.update()

if __name__ == "__main__":
    new_menu()


