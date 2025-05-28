from __future__ import annotations
from abc import ABC
from typing import List
from random import shuffle, randint, choice, seed
import time
import threading
import pygame

from juego.button import *
from juego.bomba import *

class Modulo:
    def __init__(self, Bomba, pos) -> None:
        self.estado= False #False indica que no ha sido resuelto
        self.pos = pos
        self.Bomba = Bomba
    
class ModuloCablesBasicos(Modulo):
    def __init__(self, Bomba, franja: str, pos:int) -> None:
        super().__init__(Bomba, pos)
        self.nombre = "Cables Básicos"
        self.cables: List["Cable"]=[]
        self.rect =[]
        self.franja = franja
        self.estado_equivocacion = None
        self.image_rect = None
        self.C1 = None
        self.C2 = None
        self.C3 = None
        self.C4 = None
        self.rect_abs = None
        self.modulo = None
        
        
    def regla_se_cumple(self, regla, cable_basico):
        """Devuelve True si la combinación de cables cumple la regla."""
        if regla.get("tipo") == "directa":
            return (self.cables[regla["cable_idx"]].color == regla["cable_color"] and
                    cable_basico.color == regla["cb_color"])
        elif regla.get("tipo") == "indirecta":
            return (self.cables[regla["cable_idx"]].color == regla["cable_color"] and
                    cable_basico.color == self.cables[regla["cb_color_idx"]].color)
        elif regla.get("tipo") == "solo_cb":
            return cable_basico.color == self.cables[regla["cb_color_idx"]].color
        return False
    
    def generar_reglas_congruentes(self):
        reglas_por_franja = {}
        TIPOS = ("directa", "indirecta", "solo_cb")
        #Por cada franja
        for franja in ["amarilla", "rosada", "verde", "blanca"]:
            # 2.1 elige la regla que sí será válida
            tipo_valido = choice(TIPOS)
            reglas = []
            afirmacion_es_verdadera = choice([True, False])

            default_cortar = 3  # último cable
            cable_random = randint(0, 3)

            regla = {
                "tipo": "condicional",
                "afirmacion_es_verdadera": afirmacion_es_verdadera,
                "cable_si_afirmacion_verdadera": cable_random
            }

            reglas.append(regla)

            #genera la regla verdadera
            if tipo_valido == "directa":
                cable_idx = choice(range(len(self.cables)))
                regla_ok = {
                    "tipo": "directa",
                    "valida": True,
                    "cable_idx": cable_idx,
                    "cable_color": self.cables[cable_idx].color,
                    "cb_color": self.cables[cable_idx].color  # será cierta al pinchar ese mismo color
                }

            elif tipo_valido == "indirecta":
                cable_idx, cb_idx = choice(range(len(self.cables))), choice(range(len(self.cables)))
                while cb_idx == cable_idx:
                    cb_idx = choice(range(len(self.cables)))
                regla_ok = {
                    "tipo": "indirecta",
                    "valida": True,
                    "cable_idx": cable_idx,
                    "cable_color": self.cables[cable_idx].color,
                    "cb_color_idx": cb_idx      # basta con pinchar el cable del color cb_idx
                }

            else:  # solo_cb
                cb_idx = choice(range(len(self.cables)))
                regla_ok = {
                    "tipo": "solo_cb",
                    "valida": True,
                    "cb_color_idx": cb_idx      # verdadera sólo si las otras dos fallan
                }

            reglas.append(regla_ok)

            #genera las dos reglas falsas
            tipos_falsos = [t for t in TIPOS if t != tipo_valido]

            for t in tipos_falsos:
                regla_falsa = None

                #DIRECTA FALSA
                if t == "directa":
                    # mismatcheamos el color del cable para que jamás coincida
                    cable_idx = choice(range(len(self.cables)))
                    color_real = self.cables[cable_idx].color
                    color_falso = choice([c.color for c in self.cables if c.color != color_real])
                    regla_falsa = {
                        "tipo": "directa",
                        "valida": False,
                        "cable_idx": cable_idx,
                        "cable_color": color_falso,
                        "cb_color": color_real        # da igual, ya falló la 1ª condición
                    }

                #INDIRECTA FALSA
                elif t == "indirecta":
                    cable_idx = choice(range(len(self.cables)))
                    color_real = self.cables[cable_idx].color
                    color_falso = choice([c.color for c in self.cables if c.color != color_real])
                    cb_idx = choice(range(len(self.cables)))
                    regla_falsa = {
                        "tipo": "indirecta",
                        "valida": False,
                        "cable_idx": cable_idx,
                        "cable_color": color_falso,   # 1ª condición nunca se cumple
                        "cb_color_idx": cb_idx
                    }

                #SOLO_CB FALSA
                else:  # solo_cb
                    # escogemos un índice cuya combinación ya esté cubierta por la regla válida
                    # o mismatcheamos vía 'valida': False para que el validador la ignore
                    cb_idx = choice(range(len(self.cables)))
                    regla_falsa = {
                        "tipo": "solo_cb",
                        "valida": False,
                        "cb_color_idx": cb_idx
                    }

                # Verifica que realmente no se cumple (por seguridad)
                se_cumple = any(self.regla_se_cumple(regla_falsa, cb) for cb in self.cables)
                if se_cumple:
                    # Fuerza la invalidez cambiando cable_color si fuese necesario
                    if t in ("directa", "indirecta"):
                        otros_colores = [c.color for c in self.cables
                                        if c.color not in (regla_falsa.get("cable_color"),
                                                            regla_ok.get("cable_color", ""))]
                        if otros_colores:
                            regla_falsa["cable_color"] = otros_colores[0]
                    # nota: si aún se cumpliese, el validador la saltará porque valida=False
                reglas.append(regla_falsa)

            #guarda por franja
            reglas_por_franja[franja] = reglas
            print(f"Reglas para franja {franja}: {reglas}")   
        return reglas_por_franja


  
    def dibujarFondo(self, pantalla):
        fondo = pygame.image.load("src/graphics/Fondos/fondo_cables_simples.png")
        pantalla.blit(fondo, (0, 0))
    
    def dibujarElementos(self, pantalla, pantalla1, pantalla2): 

        self.C1 = ButtonC(pantalla1, pantalla2, 35, 60, self.cables[0], self, 120, 20)
        self.C2 = ButtonC(pantalla1, pantalla2, 35, 85, self.cables[1], self, 120, 20)
        self.C3 = ButtonC(pantalla1, pantalla2, 35, 118, self.cables[2], self, 120, 20)
        self.C4 = ButtonC(pantalla1, pantalla2, 35, 145, self.cables[3], self, 120, 20)

        if self.estado: 
            led_verde = pygame.image.load("src/graphics/LED_MODULOS/LED_verde_modulo.png")
            pantalla.blit(led_verde, (0, 0))
        elif self.estado_equivocacion: 
            led_rojo = pygame.image.load("src/graphics/LED_MODULOS/LED_rojo_modulo.png")
            pantalla.blit(led_rojo, (0, 0))
    
    def agregar_cables(self):
        seed(time.time()) 
        LISTA_COLORES = ["Rojo", "Azul", "Negro", "Blanco"]
        shuffle(LISTA_COLORES)

        COLOR_TO_CLASS = {
            "Rojo": CableRojo,
            "Azul": CableAzul,
            "Negro": CableNegro,
            "Blanco": CableBlanco
        }

        self.cables = []
        self.rect = []

        for i, color in enumerate(LISTA_COLORES):
            
            pos_y = i * 30  # Calcula la posición vertical automáticamente
            rect = pygame.Rect(0, pos_y, 10, 10)
            self.rect.append(rect)

            cable_class = COLOR_TO_CLASS[color]
            cable = cable_class(color=color, posx=0, posy=pos_y)
            self.cables.append(cable)
        seed(time.time() + i*100)
        self.reglas_config = self.generar_reglas_congruentes()
        
    def cortar_cable(self, CableBasico: object): 
        #Validación que modulo esté sin desactivar
        if self.estado == False and CableBasico.estado == False: 
            CableBasico.set_estado_cortado()
            self.validacion(CableBasico)
        

    def validacion(self, cable_basico):
        # Obtén todas las reglas de la franja
        reglas = self.reglas_config.get(self.franja, [])
        regla_condicional = next((r for r in reglas if r["tipo"] == "condicional"), None)
        # Separar por tipo y descartar las inválidas de antemano
        directa    = next((r for r in reglas if r["tipo"] == "directa"   and r.get("valida")), None)
        indirecta  = next((r for r in reglas if r["tipo"] == "indirecta" and r.get("valida")), None)
        solo_cb    = next((r for r in reglas if r["tipo"] == "solo_cb"   and r.get("valida")), None)
        if regla_condicional:
            afirmacion = regla_condicional["afirmacion_es_verdadera"]
            if afirmacion:
                # Cortar cable aleatorio predefinido
                cable_correcto = self.cables[regla_condicional["cable_si_afirmacion_verdadera"]]
                print(cable_correcto, regla_condicional["cable_si_afirmacion_verdadera"])
                if cable_basico.color == cable_correcto.color:
                    self.estado = True
                    self.Bomba.modulos_restantes -= 1
                else:
                    self.estado_equivocacion = True
                    self.Bomba.notificar_equivocacion()
                return
        # Evalúa respetando la jerarquía
        if directa and self.regla_se_cumple(directa, cable_basico):
            print("Regla DIRECTA cumplida")
            print("Módulo desactivado")
            self.estado = True
            self.Bomba.modulos_restantes -= 1
        elif indirecta and self.regla_se_cumple(indirecta, cable_basico):
            print("Regla INDIRECTA cumplida")
            print("Módulo desactivado")
            self.estado = True
            self.Bomba.modulos_restantes -= 1
        elif solo_cb and self.regla_se_cumple(solo_cb, cable_basico):
            print("Regla SOLO_CB cumplida")
            print("Módulo desactivado")
            self.estado = True
            self.Bomba.modulos_restantes -= 1
        else:
            print("Equivocación")
            self.estado_equivocacion = True
            self.Bomba.notificar_equivocacion()


class ModuloCablesComplejos(Modulo):
    def __init__(self, Bomba, pos:int) -> None:
        super().__init__(Bomba, pos)
        self.nombre = "Cables Complejos"
        self.cables: List["Cable"]=[]
        self.estado_equivocacion = False
        self.rect = []
        self.C1 = None
        self.C2 = None
        self.C3 = None
        self.C4 = None
        self.rect_abs = None
        self.acciones = ["A", "B", "C1", "C2", "C3", "C4"]  # A=Cortar, B=No cortar, CX=Ir a x enunciado

    def dibujarFondo(self, pantalla):
        fondo = pygame.image.load("src/graphics/Fondos/fondo_cables_complejos.png")
        pantalla.blit(fondo, (0, 0))
    
    def dibujarElementos(self, pantalla, pantalla1, pantalla2):
        self.C1 = ButtonC(pantalla1, pantalla2, 34, 70, self.cables[0], self, 20, 120)
        self.C2 = ButtonC(pantalla1, pantalla2, 56, 70, self.cables[1], self, 20, 120)
        self.C3 = ButtonC(pantalla1, pantalla2, 80, 70, self.cables[2], self, 20, 120)
        self.C4 = ButtonC(pantalla1, pantalla2, 104, 70, self.cables[3], self, 20, 120)
        
        self.ok = ButtonJ(pantalla1, pantalla2, 139, 98, 40, 40, "xd", (0,0,0), 2)
        for i, cable in enumerate(self.cables): 
            if i == 0: 
                pantalla.blit(cable.icono_led, (0,0))
                pantalla.blit(cable.icono_letra, (0,0))
            elif i == 1: 
                pantalla.blit(cable.icono_led, (22,0))
                pantalla.blit(cable.icono_letra, (22,0))
            elif i == 2: 
                pantalla.blit(cable.icono_led, (46,0))
                pantalla.blit(cable.icono_letra, (46,0))
            elif i == 3: 
                pantalla.blit(cable.icono_led, (70,0))
                pantalla.blit(cable.icono_letra, (70,0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONDOWN and (mouse_x > self.rect_abs[0] and mouse_x < self.rect_abs[0] + self.rect_abs[2]) and (mouse_y > self.rect_abs[1] and mouse_y < self.rect_abs[1] + self.rect_abs[3]):

                    self.ok.handle_event(event, lambda: self.validacion_final())
    
        if self.estado: 
            led_verde = pygame.image.load("src/graphics/LED_MODULOS/LED_verde_modulo.png")
            pantalla.blit(led_verde, (0, 0))
        elif self.estado_equivocacion: 
            led_rojo = pygame.image.load("src/graphics/LED_MODULOS/LED_rojo_modulo.png")
            pantalla.blit(led_rojo, (0, 0))
    
    def handle_event(self, event, pantalla):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    
    def generar_reglas_congruentes(self):
        reglas_por_conexion = {}
        
        # Para cada conexión (A y B)
        for conexion in ["A", "B"]:
            reglas = []
            COLORES = ["Naranja", "Morado"]
            ACCIONES = ["A", "B", "C1", "C2", "C3", "C4"]
            colorelegidocolor = choice(COLORES)
            COLORES.remove(colorelegidocolor)  # Evita repetir el color en la misma conexión
            accionelegidacolor = choice(ACCIONES)
            ACCIONES.remove(accionelegidacolor)  # Evita repetir la acción en la misma conexión
            reglaColor1 = {
                "tipo": "color",
                "color": colorelegidocolor,
                "accion": accionelegidacolor,
                **({"value_enunciado": choice([True, False])} if accionelegidacolor.startswith("C") else {})
            }
            accionelegidacolor = choice(ACCIONES)
            ACCIONES.remove(accionelegidacolor)
            reglas.append(reglaColor1)
            reglacolor2 = {
                "tipo": "color",
                "color": COLORES[0],
                "accion": accionelegidacolor,
                **({"value_enunciado": choice([True, False])} if accionelegidacolor.startswith("C") else {})
            }
            accionelegidacolor = choice(ACCIONES)
            ACCIONES.remove(accionelegidacolor)
            reglas.append(reglacolor2)
            reglaled = {
                "tipo": "led",
                "accion": accionelegidacolor,
                **({"value_enunciado": choice([True, False])} if accionelegidacolor.startswith("C") else {})
            }
            reglas.append(reglaled)
            accionelegidacolor = choice(ACCIONES)
            ACCIONES.remove(accionelegidacolor)
            COLORES = ["Naranja", "Morado"]
            colorelegidocolor = choice(COLORES)
            COLORES.remove(colorelegidocolor)
            reglacolor1led = {
                "tipo": "color_led",
                "color": colorelegidocolor,
                "accion": accionelegidacolor,
                **({"value_enunciado": choice([True, False])} if accionelegidacolor.startswith("C") else {})
            }
            reglas.append(reglacolor1led)
            accionelegidacolor = choice(ACCIONES)
            ACCIONES.remove(accionelegidacolor)
            reglacolor2led = {
                "tipo": "color_led",
                "color": COLORES[0],
                "accion": accionelegidacolor,
                **({"value_enunciado": choice([True, False])} if accionelegidacolor.startswith("C") else {})
            }
            reglas.append(reglacolor2led)
            accionelegidacolor = choice(ACCIONES)
            ACCIONES.remove(accionelegidacolor)
            reglatodo = {   
                "tipo": "todo",
                "accion": accionelegidacolor,
                **({"value_enunciado": choice([True, False])} if accionelegidacolor.startswith("C") else {})
            }
            reglas.append(reglatodo)
            reglas_por_conexion[conexion] = reglas
        print(f"Reglas generadas para las conexiones: {reglas_por_conexion}")
        return reglas_por_conexion

    #Asignación de cables
    def agregar_cables(self):
        LISTA_COLORES = ["Naranja", "Morado", "Naranja y Morado", "Blanco"]
        for i in range(0,4):
            indice_elegido = randint(0,3)
            if i == 0:
                self.cables.append(CableComplejo(LISTA_COLORES[indice_elegido], 0,0))
            elif i == 1:
                self.cables.append(CableComplejo(LISTA_COLORES[indice_elegido], 22,0))
            elif i == 2:
                self.cables.append(CableComplejo(LISTA_COLORES[indice_elegido], 46,0))
            elif i == 3:
                self.cables.append(CableComplejo(LISTA_COLORES[indice_elegido], 70,0))
        self.reglas_config = self.generar_reglas_congruentes()

    #Asignación de la conexión de los cables a A y B
    def conectar_cables(self):
        LISTA_POSICIONES= ["A","B"]
        for cable in self.cables:
            indice_elegido = randint(0,1)
            cable.set_conectado_a(LISTA_POSICIONES[indice_elegido])

    #Asignación LEDs a cables  - False: LED apagado - True: LED encendido 
    def asignacion_LED(self):
        LISTA_ESTADO_LED= [True, False]
        for cable in self.cables:
            indice_elegido = randint(0,1)
            cable.set_estado_LED(LISTA_ESTADO_LED[indice_elegido])

    #Función para cortar un cable
    def cortar_cable(self, CableComplejo: object): 
        if CableComplejo.estado == False:
            CableComplejo.set_estado_cortado()
            self.validacion_cable(CableComplejo)
    
    #Se valida al cortar un cable
    def validacion_cable(self, cable_complejo):
        reglas = self.reglas_config.get(cable_complejo.conectado_a, [])
        
        # Revisa todas las reglas para la conexión del cable
        for regla in reglas:
            if regla["tipo"] == "color":
                if cable_complejo.color == regla["color"]:
                    if self.ejecutar_accion(regla["accion"], regla) == False:
                        self.Bomba.notificar_equivocacion() 
                        self.estado_equivocacion = True
                    return 
            elif regla["tipo"] == "led":
                if cable_complejo.LED == regla["LED"]:
                    if self.ejecutar_accion(regla["accion"], regla) == False:
                        self.Bomba.notificar_equivocacion() 
                        self.estado_equivocacion = True
                    return 
            elif regla["tipo"] == "color_led":
                if (cable_complejo.color == regla["color"] and 
                    cable_complejo.LED == regla["LED"]):
                    if self.ejecutar_accion(regla["accion"], regla) == False:
                        self.Bomba.notificar_equivocacion() 
                        self.estado_equivocacion = True
                    return 
    
    def ejecutar_accion(self, accion, regla):
        if accion == "A":
            return True  # Cortar el cable
        elif accion == "B":
            return False  # No cortar el cable
        else:
            if regla['value_enunciado'] == False:
                return False

    def validacion_final(self):
        for cable in self.cables:
            if cable.estado == False:
                reglas = self.reglas_config.get(cable.conectado_a, [])
                for regla in reglas:
                    color_ok = ("color" not in regla) or (cable.color == regla["color"])
                    led_ok = ("LED" not in regla) or (cable.LED == regla["LED"])
                    if color_ok and led_ok:
                        self.estado_equivocacion = True
                        self.Bomba.notificar_equivocacion()
                        return "Equivocación"
                print("Cable no cortado correcto")
        print("Modulo desactivado")
        self.Bomba.modulos_restantes = self.Bomba.modulos_restantes - 1
        self.estado = True


class ModuloPalabras(Modulo):  #Caso memoria
    #Solo una lista. Hacer lista aleatoria que se agrega con nodos
    def __init__(self, Bomba, pos: int) -> None:
        super().__init__(Bomba, pos)
        self.nombre = "Memoria"
        self.numero_monitor:int = 0
        self.lista= None
        self.etapa= 0
        self.opciones=[1,2,3,4]
        self.seleccion=None
        self.seleccion1 = None
        self.seleccion2 = None
        self.seleccion3 = None
        self.seleccion4 = None
        self.font= pygame.font.Font("src/font/Pixeled.ttf", 10)
        self.estado_equivocacion = False
        self.rect_abs = None

    def dibujarFondo(self, pantalla):
        fondo = pygame.image.load("src/graphics/Fondos/fondo_memoria.png")
        pantalla.blit(fondo, (0, 0))
    
    def dibujarElementos(self, pantalla, posicionreal = None):
        texto1 = "NODO:    1    2    3   4"
        texto2 = f"ITEM:    {self.lista[0]}    {self.lista[1]}    {self.lista[2]}    {self.lista[3]}"
        frase1 = self.font.render(texto1, True, (0,0,0))
        frase2 = self.font.render(texto2, True, (0,0,0))
        pantalla.blit(frase1, (30,55))
        pantalla.blit(frase2, (30,75))
        if self.estado: 
            led_verde = pygame.image.load("src/graphics/LED_MODULOS/LED_verde_modulo.png")
            pantalla.blit(led_verde, (0, 0))
        elif self.estado_equivocacion: 
            led_rojo = pygame.image.load("src/graphics/LED_MODULOS/LED_rojo_modulo.png")
            pantalla.blit(led_rojo, (0, 0))
            
        # boton1 = ButtonM(pantalla,30,123,32,47,"1",(0,0,0,0))
        # boton2 = ButtonM(pantalla,65,123,35,47,"2",(0,0,0,0))
        # boton3 = ButtonM(pantalla,103,123,35,47,"3",(0,0,0,0))
        # boton4 = ButtonM(pantalla,140,123,35,47,"4",(0,0,0,0))
        barra = ButtonM(pantalla, 65, 173, 73, 15, "", (0,0,0,0))
        boton1 = ButtonN(pantalla,30,123,32,47,Nodo(self.opciones[0], 1))
        boton2 = ButtonN(pantalla,65,123,35,47, Nodo(self.opciones[1], 2))
        boton3 = ButtonN(pantalla,103,123,35,47, Nodo(self.opciones[2], 3))
        boton4 = ButtonN(pantalla,140,123,35,47, Nodo(self.opciones[3], 4))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN and (mouse_x > self.rect_abs[0] and mouse_x < self.rect_abs[0] + self.rect_abs[2]) and (mouse_y > self.rect_abs[1] and mouse_y < self.rect_abs[1] + self.rect_abs[3]):
                boton1.handle_event1(event, posicionreal, lambda: print("hola"))
                boton2.handle_event1(event, posicionreal, lambda: print("como"))
                boton3.handle_event1(event, posicionreal, lambda: print("estas"))
                boton4.handle_event1(event, posicionreal, lambda: print("tu"))
                barra.handle_event1(event, posicionreal, lambda: print("?"))

    def agregar_lista(self): 
        shuffle(self.opciones)
        self.lista = self.opciones

    #Se ejecuta una vez al principio y luego por validar()
    def pasar_etapa(self): 
        LISTA_MONITOR = [1, 2]
        indice_elegido = randint(0,1)
        self.numero_monitor = LISTA_MONITOR[indice_elegido]
        self.etapa = self.etapa +1
        shuffle(self.opciones)

    def seleccionar(self, posicion: int, opcion: int):
        self.seleccion = Nodo(posicion, opcion)
        self.validar(self.etapa)


    def validar(self, etapa):
        if etapa == 1: 
            if self.numero_monitor == 1: 
                if self.lista[0] == self.seleccion.etiqueta : 
                    print("Correcto, pasó a la etapa 2")
                    self.seleccion1 = self.seleccion
                    self.pasar_etapa()
                    self.seleccionar(int, int)
                else: 
                    print("Equivocación")
                    self.Bomba.notificar_equivocacion() 
                    #! Añadir sonido
                    self.estado_equivocacion = True
                    #Validar si se equivoca y le quedan errores, volver a seleccionar
                pass
            elif self.numero_monitor == 2:
                if self.lista[0] == self.seleccion.posicion: 
                    print("Correcto, pasó a la etapa 2")
                    self.seleccion1 = self.seleccion
                    self.pasar_etapa()
                    self.seleccionar(int, int)
                else: 
                    print("Equivocación")
                    self.Bomba.notificar_equivocacion() 
                    self.estado_equivocacion = True
                pass
            else: 
                print("Error en el número del monitor")
            
        elif etapa == 2: 
            if self.numero_monitor == 1: 
                if self.seleccion1.etiqueta == self.seleccion.etiqueta : 
                    print("Correcto, pasó a la etapa 3")
                    self.seleccion2 = self.seleccion
                    self.pasar_etapa()
                    self.seleccionar(int, int)
                else: 
                    print("Equivocación")
                    self.Bomba.notificar_equivocacion() 
                    self.estado_equivocacion = True
                    #Validar si se equivoca y le quedan errores, volver a seleccionar
                pass
            elif self.numero_monitor == 2:
                if self.lista[2] == self.seleccion.etiqueta: 
                    print("Correcto, pasó a la etapa 3")
                    self.seleccion2 = self.seleccion
                    self.pasar_etapa()
                    self.seleccionar(int, int)
                else: 
                    print("Equivocación")
                    self.Bomba.notificar_equivocacion() 
                    self.estado_equivocacion = True
                
            else: 
                print("Error en el número del monitor")

        elif etapa == 3: 
            if self.numero_monitor == 1: 
                if self.lista[3] == self.seleccion.etiqueta : 
                    print("Correcto, pasó a la etapa 4")
                    self.seleccion3 = self.seleccion
                    self.pasar_etapa()
                    self.seleccionar(int, int)
                else: 
                    print("Equivocación")
                    self.Bomba.notificar_equivocacion() 
                    self.estado_equivocacion = True
                    #Validar si se equivoca y le quedan errores, volver a seleccionar
                pass
            elif self.numero_monitor == 2:
                if self.seleccion1.posicion == self.seleccion.posicion: 
                    print("Correcto, pasó a la etapa 4")
                    self.seleccion3 = self.seleccion
                    self.pasar_etapa()
                    self.seleccionar(int, int)
                else: 
                    print("Equivocación")
                    self.Bomba.notificar_equivocacion() 
                    self.estado_equivocacion = True
                pass
            else: 
                print("Error en el número del monitor")
            
        elif etapa == 4: 
            if self.numero_monitor == 1: 
                if self.seleccion1.posicion == self.seleccion.posicion : 
                    print("Correcto, desactivó el modulo")
                    self.seleccion4 = self.seleccion
                    self.pasar_etapa()
                    
                else: 
                    print("Equivocación")
                    self.Bomba.notificar_equivocacion() 
                    self.estado_equivocacion = True
                    #Validar si se equivoca y le quedan errores, volver a seleccionar
                pass
            elif self.numero_monitor == 2:
                if self.lista[2] == self.seleccion.posicion: 
                    print("Correcto, desactivó el modulo")
                    self.seleccion2 = self.seleccion
                    self.pasar_etapa()
                    
                else: 
                    print("Equivocación")
                    self.Bomba.notificar_equivocacion() 
                    self.estado_equivocacion = True
                
        else: 
            print("Error en la asignación de etapas")
    
    
    
class ModuloCodigo(Modulo):
    def __init__(self, Bomba, codigo:str, pos:int) -> None:
        super().__init__(Bomba, pos)
        self.nombre = "Código"
        self.i1 = 0
        self.i2 = 0
        self.i3 = 0
        self.i4 = 0
        self.i5 = 0
        self.codigo = codigo
        self.casilla1 = None
        self.casilla2 = None 
        self.casilla3 = None 
        self.casilla4 = None
        self.casilla5 = None 
        self.posicion1 = []
        self.posicion2 = []
        self.posicion3 = []
        self.posicion4 = []
        self.posicion5 = []
        self.estado_equivocacion = False
        self.font = pygame.font.Font("src/font/Pixeled.ttf", 12)
        self.rect_abs = None

    def dibujarFondo(self, pantalla):
        fondo = pygame.image.load("src/graphics/Fondos/fondo_codigo.png")
        pantalla.blit(fondo, (0, 0))
    
    def dibujarElementos(self, pantalla, pantalla1, pantalla2): 
        button1U = ButtonJ(pantalla1, pantalla2, 42, 65, 20, 5, "xd", (0,0,0), 2)
        button2U = ButtonJ(pantalla1, pantalla2, 68, 65, 20, 5, "xd", (0,0,0), 2)
        button3U = ButtonJ(pantalla1, pantalla2, 92, 65, 20, 5, "xd", (0,0,0), 2)
        button4U = ButtonJ(pantalla1, pantalla2, 118, 65, 20, 5, "xd", (0,0,0), 2)
        button5U = ButtonJ(pantalla1,pantalla2, 142, 65, 20, 5, "xd", (0,0,0), 2)
        button1D = ButtonJ(pantalla1, pantalla2, 42, 131, 20, 5, "xd", (0,0,0), 2)
        button2D = ButtonJ(pantalla1,pantalla2, 68, 131, 20, 5, "xd", (0,0,0), 2)
        button3D = ButtonJ(pantalla1,pantalla2, 92, 131, 20, 5, "xd", (0,0,0), 2)
        button4D = ButtonJ(pantalla1,pantalla2, 118, 131, 20, 5, "xd", (0,0,0), 2)
        button5D = ButtonJ(pantalla1,pantalla2, 142, 131, 20, 5, "xd", (0,0,0), 2)
        buttonOk = ButtonJ(pantalla1,pantalla2, 82, 152, 50, 25, "xd", (0,0,0), 2)
        letra1 = self.font.render(self.casilla1.letra, True, (0,0,0))
        letra2 = self.font.render(self.casilla2.letra, True, (0,0,0))
        letra3 = self.font.render(self.casilla3.letra, True, (0,0,0))
        letra4 = self.font.render(self.casilla4.letra, True, (0,0,0))
        letra5 = self.font.render(self.casilla5.letra, True, (0,0,0))
        pantalla.blit(letra1, (47,80))
        pantalla.blit(letra2, (72,80))
        pantalla.blit(letra3, (96,80))
        pantalla.blit(letra4, (121,80))
        pantalla.blit(letra5, (147,80))
        button1U.draw()
        button2U.draw()
        button3U.draw()
        button4U.draw()
        button5U.draw()
        button1D.draw()
        button2D.draw()
        button3D.draw()
        button4D.draw()
        button5D.draw()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                    
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN and (mouse_x > self.rect_abs[0] and mouse_x < self.rect_abs[0] + self.rect_abs[2]) and (mouse_y > self.rect_abs[1] and mouse_y < self.rect_abs[1] + self.rect_abs[3]):
                button1U.handle_event(event, lambda: self.anterior_posicion(1))
                button2U.handle_event(event, lambda: self.anterior_posicion(2))
                button3U.handle_event(event, lambda: self.anterior_posicion(3))
                button4U.handle_event(event, lambda: self.anterior_posicion(4))
                button5U.handle_event(event, lambda: self.anterior_posicion(5))
                button1D.handle_event(event, lambda: self.siguiente_posicion(1))
                button2D.handle_event(event, lambda: self.siguiente_posicion(2))
                button3D.handle_event(event, lambda: self.siguiente_posicion(3))
                button4D.handle_event(event, lambda: self.siguiente_posicion(4))
                button5D.handle_event(event, lambda: self.siguiente_posicion(5))
                buttonOk.handle_event(event, lambda: self.validar())

        if self.estado: 
            led_verde = pygame.image.load("src/graphics/LED_MODULOS/LED_verde_modulo.png")
            pantalla.blit(led_verde, (0, 0))
        elif self.estado_equivocacion: 
            led_rojo = pygame.image.load("src/graphics/LED_MODULOS/LED_rojo_modulo.png")
            pantalla.blit(led_rojo, (0, 0))

    def not_in_lista(self, letra, lista): 
        if lista == []: 
            return True
        else:
            LISTA_AUX = [] 
            for elemento in lista: 
                LISTA_AUX.append(elemento.letra)
            
            if letra in LISTA_AUX: 
                return False
            else: 
                return True

    def set_casillas_inicial(self):
        LISTA_LETRAS= ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L","M", "N", "O", "P","Q",
                       "R", "S", "T", "U", "V", "X", "Y","Z"]
    
        self.posicion1.append(Casilla(self.codigo[0]))
        self.posicion2.append(Casilla(self.codigo[1]))
        self.posicion3.append(Casilla(self.codigo[2]))
        self.posicion4.append(Casilla(self.codigo[3]))
        self.posicion5.append(Casilla(self.codigo[4]))

        for i in range(0,7):
            letra = LISTA_LETRAS[randint(0, 24)]
            while(letra == self.codigo[0] or self.not_in_lista(letra, self.posicion1) == False):
                letra = LISTA_LETRAS[randint(0, 24)]
            self.posicion1.append(Casilla(letra))
            letra = LISTA_LETRAS[randint(0, 24)]
            while(letra == self.codigo[1] or self.not_in_lista(letra, self.posicion2) == False):
                letra = LISTA_LETRAS[randint(0, 24)]
            self.posicion2.append(Casilla(letra))
            letra = LISTA_LETRAS[randint(0, 24)]
            while(letra == self.codigo[2] or self.not_in_lista(letra, self.posicion3) == False):
                letra = LISTA_LETRAS[randint(0, 24)]
            self.posicion3.append(Casilla(letra))
            letra = LISTA_LETRAS[randint(0, 24)]
            while(letra == self.codigo[3] or self.not_in_lista(letra, self.posicion4) == False):
                letra = LISTA_LETRAS[randint(0, 24)]
            self.posicion4.append(Casilla(letra))
            letra = LISTA_LETRAS[randint(0, 24)]
            while(letra == self.codigo[4] or self.not_in_lista(letra, self.posicion5) == False):
                letra = LISTA_LETRAS[randint(0, 24)]
            self.posicion5.append(Casilla(letra))
        
        shuffle(self.posicion1)
        shuffle(self.posicion2)
        shuffle(self.posicion3)
        shuffle(self.posicion4)
        shuffle(self.posicion5)

        self.casilla1 = self.posicion1[0]
        self.casilla2 = self.posicion2[0] 
        self.casilla3 = self.posicion3[0] 
        self.casilla4 = self.posicion4[0]
        self.casilla5 = self.posicion5[0]
        print(self.codigo)

    def siguiente_posicion(self, columna:int):
        if columna == 1: 
            if self.casilla1.letra == self.posicion1[-1].letra: 
                print("Ultima letra alcanzada")
            else: 
                self.casilla1 = self.posicion1[self.i1+1]
                self.i1+=1
        if columna == 2: 
            if self.casilla2.letra == self.posicion2[-1].letra: 
                print("Ultima letra alcanzada")
            else: 
                self.casilla2 = self.posicion2[self.i2+1]
                self.i2+=1
        if columna == 3: 
            if self.casilla3.letra == self.posicion3[-1].letra: 
                print("Ultima letra alcanzada")
            else: 
                self.casilla3 = self.posicion3[self.i3+1]
                self.i3+=1
        if columna == 4: 
            if self.casilla4.letra == self.posicion4[-1].letra: 
                print("Ultima letra alcanzada")
            else: 
                self.casilla4 = self.posicion4[self.i4+1]
                self.i4+=1
        if columna == 5: 
            if self.casilla5.letra == self.posicion5[-1].letra: 
                print("Ultima letra alcanzada")
            else: 
                self.casilla5 = self.posicion5[self.i5+1]
                self.i5+=1
    
    def anterior_posicion(self, columna:int):
        if columna == 1: 
            if self.casilla1.letra == self.posicion1[0].letra: 
                print("Primera letra alcanzada") 
            else: 
                self.casilla1 = self.posicion1[self.i1-1]
                self.i1-=1
        if columna == 2: 
            if self.casilla2.letra == self.posicion2[0].letra: 
                print("Primera letra alcanzada")
            else: 
                self.casilla2 = self.posicion2[self.i2-1]
                self.i2-=1
        if columna == 3: 
            if self.casilla3.letra == self.posicion3[0].letra: 
                print("Primera letra alcanzada")
            else: 
                self.casilla3 = self.posicion3[self.i3-1]
                self.i3-=1
        if columna == 4: 
            if self.casilla4.letra == self.posicion4[0].letra: 
                print("Primera letra alcanzada")
            else: 
                self.casilla4 = self.posicion4[self.i4-1]
                self.i4-=1
        if columna == 5: 
            if self.casilla5.letra == self.posicion5[0].letra: 
                print("Primera letra alcanzada")
            else: 
                self.casilla5 = self.posicion5[self.i5-1]
                self.i5-=1

    def validar(self):
        if (self.casilla1.letra == self.codigo[0] and self.casilla2.letra == self.codigo[1] and self.casilla3.letra == self.codigo[2]
            and self.casilla4.letra == self.codigo[3] and self.casilla5.letra == self.codigo[4]): 
            print("Módulo resuelto")
            self.estado = True 
            self.Bomba.modulos_restantes = self.Bomba.modulos_restantes - 1
        else: 
            print("Equivocación")
            self.Bomba.notificar_equivocacion() 


class ModuloExigente(Modulo):
    def __init__(self, Bomba, pos:int) -> None:
        super().__init__(Bomba, pos)
        self.nombre = "Exigente"
        self.estado=False
        self.enunciados = [
            "Los archivos se pueden leer y escribir secuencialmente o de forma aleatoria", 
            "Las listas en Python son siempre de tamaño fijo y no se pueden cambiar una vez creadas", 
            "Las pilas siguen el principio LIFO (Last In, First Out)", 
            "Las colas siempre tienen un tamaño fijo y no se pueden ampliar o reducir", 
            "Los archivos solo pueden contener datos de tipo texto",
            "En una lista, los elementos se pueden acceder y modificar utilizando un índice numérico",
            "En una lista circular, el último elemento está enlazado al primer elemento de la lista",
            "Las listas doblemente enlazadas no permiten eliminar nodos de la lista",
            "Una pila permite eliminar elementos en cualquier posición de la pila"]
        self.enunciado = None
        self.opciones = ["S", "N"]
        self.tiempo_restante = 20
        self.tiempo_intermedio = 45
        self.hilo_temporizador = None
        self.hilo_reposo = None
        self.tiempo_inicio_original = time.time()
        self.rect_abs = None
    
    def dibujarFondo(self, pantalla):
        fondo = pygame.image.load("src/graphics/Fondos/fondo_exigente.png")
        pantalla.blit(fondo, (0, 0))

    def dibujarElementos(self, pantalla, tiempo_transcurrido,control, posicionreal=None):
        botonE1 = ButtonM(pantalla,28,123,70,47,"1",(0,0,0,0))
        botonE2 = ButtonM(pantalla,103,123,70,47,"2",(0,0,0,0))
        #rect <rect(245, 194, 35, 47)>
        tiempo_transcurrido = int(tiempo_transcurrido)
        tiempo_inicio_exigente = self.tiempo_inicio_original
        if tiempo_transcurrido > 0:
            if tiempo_transcurrido % 65 == 0 or control[0] == True:
                duration_exigente = 20
                tiempo_actual = time.time()
                tiempo_transcurrido_exigente = tiempo_actual - tiempo_inicio_exigente
                remaining_time = max(duration_exigente - tiempo_transcurrido_exigente, 0)
                remaining_time = int(remaining_time % 60)
                fuente = pygame.font.Font(None, 30)
                texto = fuente.render(f"{remaining_time:02d}", 1, (255, 255, 255))
                pantalla.blit(texto, (89, 28))
                control[0] = True
                if remaining_time == 0:
                    control[0] = False
                    self.tiempo_inicio_original = time.time()
            else:
                fuente = pygame.font.Font(None, 30)
                texto = fuente.render(f"00", 1, (255, 255, 255))
                pantalla.blit(texto, (89, 28))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN and (mouse_x > self.rect_abs[0] and mouse_x < self.rect_abs[0] + self.rect_abs[2]) and (mouse_y > self.rect_abs[1] and mouse_y < self.rect_abs[1] + self.rect_abs[3]):
                botonE1.handle_event1(event, posicionreal, lambda: print("pro"))
                botonE2.handle_event1(event, posicionreal, lambda: print("player"))
        
    def activar(self):
        self.estado=True
        self.hilo_temporizador = threading.Thread(target=self._temporizador)
        self.hilo_temporizador.start
    
    def activar_intermedio(self): 
        self.hilo_reposo = threading.Thread(target=self._temporizador)
        self.hilo_reposo.start

    def seleccionar_enunciado(self):
        indice_elegido = randint(0, len(self.enunciados)-1)
        self.enunciado = self.enunciados[indice_elegido]
        print(self.enunciado)
        
    #!Revisar la desactivación
    def desactivar(self):
        self.estado=False
        if self.hilo_temporizador:
            self.hilo_temporizador.join()
            self.tiempo_restante = 20

    def _iniciar_tiempo(self):
        while self.tiempo_restante > 0:
            print("Tiempo restante:", self.tiempo_restante, "segundos")
            time.sleep(1)
            self.tiempo_restante -= 1
        print("Tiempo finalizado")
        return "La bomba ha explotado"
    
    def _iniciar_intermedio(self):
        self.activar_intermedio()
        while self.tiempo_intermedio > 0:
            time.sleep(1)
            self.tiempo_restante -= 1
        if self.hilo_reposo:
            self.hilo_reposo.join()
            self.tiempo_intermedio = 40
        self.activar()


    def validar(self, respuesta):
        if self.estado == False: 
            ## Ejemplo
            if respuesta == "S": 
                print("Correcto")
                self.desactivar()
            else: 
                return "La bomba ha explotado"

        

class Cable(ABC):
    def __init__(self) -> None:
        self.estado=False #False: no ha sido cortado


class CableBasico(Cable):
    def __init__(self, color: str) -> None:
        super().__init__()
        self.color = color
    
    def set_estado_cortado(self):
        self.estado=True

class CableRojo(CableBasico): 
    def __init__(self, color, posx, posy) -> None:
        super().__init__(color)
        self.icono_cable = pygame.image.load("src/graphics/Modulo Cables Simples/cable_simple_rojo.png")
        self.icono_cable_cortado = pygame.image.load("src/graphics/Modulo Cables Simples/cable_simple_rojo_cortado.png")
        self.posx = posx 
        self.posy = posy
        self.rect = pygame.Rect(self.posx, self.posy, 20, 20)

class CableBlanco(CableBasico): 
    def __init__(self, color, posx, posy) -> None:
        super().__init__(color)
        self.icono_cable = pygame.image.load("src/graphics/Modulo Cables Simples/cable_simple_blanco.png")
        self.icono_cable_cortado = pygame.image.load("src/graphics/Modulo Cables Simples/cable_simple_blanco_cortado.png")
        self.posx = posx 
        self.posy = posy
        self.rect = pygame.Rect(self.posx, self.posy, 20, 20)

class CableNegro(CableBasico): 
    def __init__(self, color, posx, posy) -> None:
        super().__init__(color)
        self.icono_cable = pygame.image.load("src/graphics/Modulo Cables Simples/cable_simple_negro.png")
        self.icono_cable_cortado = pygame.image.load("src/graphics/Modulo Cables Simples/cable_simple_negro_cortado.png")
        self.posx = posx 
        self.posy = posy
        self.rect = pygame.Rect(self.posx, self.posy, 20, 20)


class CableAzul(CableBasico): 
    def __init__(self, color, posx, posy) -> None:
        super().__init__(color)
        self.icono_cable = pygame.image.load("src/graphics/Modulo Cables Simples/cable_simple_azul.png")
        self.icono_cable_cortado = pygame.image.load("src/graphics/Modulo Cables Simples/cable_simple_azul_cortado.png")
        self.posx = posx 
        self.posy = posy
        self.rect = pygame.Rect(self.posx, self.posy, 20, 20)

class CableComplejo(Cable):
    def __init__(self, color: str, posx, posy) -> None:
        super().__init__()
        self.color= color
        self.conectado_a= None
        self.LED=None
        self.icono_cable = None
        self.icono_cable_cortado = None
        self.icono_led = None
        self.icono_letra = None
        self.posx= posx
        self.posy = posy
        self.rect = pygame.Rect(self.posx, self.posy, 20, 30)

        if color == "Naranja":
            self.icono_cable = pygame.image.load("src/graphics/Modulo Cables Complejos/cable_complejo_naranja.png")
            self.icono_cable_cortado = pygame.image.load("src/graphics/Modulo Cables Complejos/cable_complejo_naranja_cortado.png")
        elif color == "Morado": 
            self.icono_cable = pygame.image.load("src/graphics/Modulo Cables Complejos/cable_complejo_morado.png")
            self.icono_cable_cortado = pygame.image.load("src/graphics/Modulo Cables Complejos/cable_complejo_morado_cortado.png")
        elif color == "Naranja y Morado": 
            self.icono_cable = pygame.image.load("src/graphics/Modulo Cables Complejos/cable_complejo_naranja_morado.png")
            self.icono_cable_cortado = pygame.image.load("src/graphics/Modulo Cables Complejos/cable_complejo_naranja_morado_cortado.png")
        elif color == "Blanco": 
            self.icono_cable = pygame.image.load("src/graphics/Modulo Cables Complejos/cable_complejo_blanco.png")
            self.icono_cable_cortado = pygame.image.load("src/graphics/Modulo Cables Complejos/cable_complejo_blanco_cortado.png")
        
    def set_estado_cortado(self):
        self.estado=True

    def set_conectado_a(self, conexion):
        self.conectado_a= conexion
        if self.conectado_a == "A": 
            self.icono_letra = pygame.image.load("src/graphics/Modulo Cables Complejos/letra_a.png")
            
        elif self.conectado_a == "B": 
            self.icono_letra = pygame.image.load("src/graphics/Modulo Cables Complejos/letra_b.png")
            

    def set_estado_LED(self, estado: bool):
        self.LED = estado
        if self.LED: 
            self.icono_led = pygame.image.load("src/graphics/Modulo Cables Complejos/led_cables_encendido.png")
        else: 
            self.icono_led = pygame.image.load("src/graphics/Modulo Cables Complejos/led_cables_apagado.png")

    
class Casilla: 
    def __init__(self, letra:str) -> None:
        self.letra=letra

class Nodo: 
    def __init__(self, posicion, etiqueta): 
        self.posicion = posicion
        self.etiqueta = etiqueta
        self.icono_numero = None
        
        if self.etiqueta == 1: 
            
            if self.posicion == 1: 
                self.icono_numero = pygame.image.load("src/graphics/Modulo_Memoria/num1_1.png")
            elif self.posicion == 2: 
                self.icono_numero = pygame.image.load("src/graphics/Modulo_Memoria/num1_2.png")
            elif self.posicion == 3:
                self.icono_numero = pygame.image.load("src/graphics/Modulo_Memoria/num1_3.png")
            elif self.posicion == 4:
                self.icono_numero = pygame.image.load("src/graphics/Modulo_Memoria/num1_4.png")
                
        elif self.etiqueta == 2:
            
            if self.posicion == 1:
                self.icono_numero = pygame.image.load("src/graphics/Modulo_Memoria/num2_1.png")
            elif self.posicion == 2:
                self.icono_numero = pygame.image.load("src/graphics/Modulo_Memoria/num2_2.png")
            elif self.posicion == 3:
                self.icono_numero = pygame.image.load("src/graphics/Modulo_Memoria/num2_3.png")
            elif self.posicion == 4:
                self.icono_numero = pygame.image.load("src/graphics/Modulo_Memoria/num2_4.png")
                
        elif self.etiqueta == 3:
            
            if self.posicion == 1: 
                self.icono_numero = pygame.image.load("src/graphics/Modulo_Memoria/num3_1.png")
            elif self.posicion == 2:
                self.icono_numero = pygame.image.load("src/graphics/Modulo_Memoria/num3_2.png")
            elif self.posicion == 3:
                self.icono_numero = pygame.image.load("src/graphics/Modulo_Memoria/num3_3.png")
            elif self.posicion == 4:
                self.icono_numero = pygame.image.load("src/graphics/Modulo_Memoria/num3_4.png")
                
        elif self.etiqueta == 4:
            
            if self.posicion == 1: 
                self.icono_numero = pygame.image.load("src/graphics/Modulo_Memoria/num4_1.png")
            elif self.posicion == 2:
                self.icono_numero = pygame.image.load("src/graphics/Modulo_Memoria/num4_2.png")
            elif self.posicion == 3:
                self.icono_numero = pygame.image.load("src/graphics/Modulo_Memoria/num4_3.png")
            elif self.posicion == 4:
                self.icono_numero = pygame.image.load("src/graphics/Modulo_Memoria/num4_4.png")


