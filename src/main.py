from __future__ import annotations
import pygame
from juego.manejodearchivos import *
from pygame.locals import *
from juego.button import *
from juego.bomba import Bomba
from juego.modulos import *
from juego.dialogpanel import dialog
import os
import random
from juego.listadoble import *
import time

pygame.init()
screen = pygame.display.set_mode((1000,562))
pygame.display.set_caption("Binary Bomb Squad")
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

#background = pygame.image.load('graphics/background.png')

frame = pygame.Surface((680,460))
module1 = pygame.Surface((202,202))
module2 = pygame.Surface((202,202))
module3 = pygame.Surface((202,202))
module4 = pygame.Surface((202,202))
module5 = pygame.Surface((202,202))
timer = pygame.Surface((202,202))

frame.fill(GREEN)
module1.fill(VANILLA)
module2.fill(VANILLA)
module3.fill(VANILLA)
module4.fill(VANILLA)
module5.fill(VANILLA)
timer.fill(VANILLA)

click = False
def new_menu():
    dialogControl = True
    fontbold = pygame.font.Font("src/font/Pixeled.ttf", 10)
    pygame.font.Font.set_bold(fontbold, True)

    menubg = pygame.image.load("src/graphics/menu/menubg.png")
    playbutton = pygame.image.load("src/graphics/menu/playbutton.png")
    playbuttonh = pygame.image.load("src/graphics/menu/playbuttonh.png")
    creditsbutton = pygame.image.load("src/graphics/menu/creditsbutton.png")
    creditsbuttonh = pygame.image.load("src/graphics/menu/creditsbuttonh.png")
    quitbutton = pygame.image.load("src/graphics/menu/quitbutton.png")
    quitbuttonh = pygame.image.load("src/graphics/menu/quitbuttonh.png")

    hitboxplaybutton = pygame.Rect(220,390,105,70)
    hitboxcreditsbutton = pygame.Rect(440,380,85,80)
    hitboxquitbutton = pygame.Rect(665,380,110,75)
    pos = (0,9)
    while True:
        espacio_presionado = False
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                espacio_presionado = True

        if dialogControl:
            terminado = dialog(screen, clock, espacio_presionado)
            if terminado:
                dialogControl = False
            
        else: 
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hitboxplaybutton.collidepoint(pos):
                    opcJugar()
                elif hitboxcreditsbutton.collidepoint(pos):
                    creditos()
                elif hitboxquitbutton.collidepoint(pos):
                    pygame.quit()
                    exit()
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
def main_menu():
    while True:
        screen.fill(GOLDEN)
        image = pygame.image.load("src/graphics/Bynary Bomb logo nobg.png")
        resized_image = pygame.transform.scale(image, (300, 300))
        screen.blit(resized_image, (350, 50))
        play_button = Button(screen, 100, 430, 200, 50, "JUGAR", (255,0,0))
        play_button.draw()
        credits_button = Button(screen, 400, 430, 200, 50, "CRÉDITOS", (255,0,0))
        credits_button.draw()
        exit_button = Button(screen, 700, 430, 200, 50, "SALIR", (255,0,0))
        exit_button.draw()

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
            play_button.handle_event(event, lambda: opcJugar())
            credits_button.handle_event(event, lambda: creditos())
            exit_button.handle_event(event, lambda: exit())

        pygame.display.update()
        clock.tick(60)
click = False

def opcJugar():
    global a1
    global b1
    global n1
    global a2  
    global b2
    global n2
    list1 = DoublyLinkedList()
    list2 = DoublyLinkedList()
    font2 = pygame.font.Font("src/font/Pixeled.ttf", 10)
    fondo = pygame.image.load("src/graphics/bombsettings/bombsettingsbg.png")
    menubg = pygame.image.load("src/graphics/background/background.png")
    screen.blit(menubg, (0,0))
    for i in [0, 1, 2, 3]:
        list1.add_node(i)
    for i in [3, 4, 5]:
        list2.add_node(i)    
    a1 = list1.head
    b1 = list1.head.prev
    n1 = list1.head.next
    a2 = list2.head
    b2 = list2.head.prev
    n2 = list2.head.next
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

def create_room():
    pass 

def join_room():
    pass

def creditos():
    creditos_movibles = [
    "BINARY BOMB SQUAD",
    "",
    "INTEGRANTES DEL GRUPO:",
    "1. MARÍA CAMILA OSORNO",
    "2. JUAN FELIPE SANTOS",
    "3. SAMUEL MATIZ",
    "4. ALBERTO JOSÉ SANDOVAL",
    "",
    "DIRECTOR DEL PROYECTO:",
    "1. MARÍA CAMILA OSORNO",
    "",
    "DIRECTOR ASISTENTE:",
    "1. JUAN FELIPE SANTOS",
    "",
    "LÍDER DE DISEÑO:",
    "1. SAMUEL MATIZ",
    "",
    "LÍDER DE PROGRAMACIÓN:",
    "1. ALBERTO JOSÉ SANDOVAL",
    ]
    start_time = time.time()
    duration = 10
    fuente_titulo = pygame.font.Font("src/font/Pixeled.ttf", 36)
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

def game():
    # Duración del temporizador en segundos
    duration = 300
    remaining_time = duration
    # Obtener el tiempo de inicio
    start_time = time.time()
    control = [False]
    c=0

    global a1 #errores
    global a2 #modulos
    running = True
    escribir = ManejoDeArchivos()
    escribir.limpiarArchivo()
    escribir.escribirConfiguracion(str(a1.data))
    escribir.escribirConfiguracion(str(a2.data))
    bombita = Bomba(duration, int(a1.data), int(a2.data), 10)
    bombita.asignar_modulos()
    
    pos = [module1, module2, module3, module4, module5]
    
    while running:
        x = 0
        for modulo in bombita.modulos:
            modulo.modulo = pos[x]
            modulo.dibujarFondo(pos[x])
            if x < a2.data -1:
                x= x+1
        bombita.colocarFranja(timer)
        x = 0
        screen.fill(BLACK)
        
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
            if x < a2.data -1:
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
            terminarM(False, str(a2.data), time_text, str(bombita.equivocaciones), str(a1.data))
        if bombita.estado == "Desactivada":
            terminarM(True, str(a2.data), time_text, str(bombita.equivocaciones), str(a1.data))
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
        #modulos = "5"
        #intentos = "3"
        #tiemporestante = "1:50"
        #errores = "1"

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


