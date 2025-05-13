import time
from random import randint
from juego.modulos import *


class Bomba(): 
    def __init__(self, tiempo, errores: int, modulos: int, id: int) -> None:
        self.id = id 
        self.tiempo = tiempo
        self.estado = "Activa"
        self.errores = errores
        self.equivocaciones= 0 
        self.numero_modulos= modulos
        self.modulos_restantes= modulos
        self.modulos = []
        self.linea_tiempo= None
        self.registro = None
        self.franja = None
    
    def notificar_equivocacion(self): 
        self.equivocaciones += 1
        
    def tiempo_agotado(self): 
        if self.tiempo == 0: 
            self.estado = "Detonada"  
    
    def equivocaciones_limite(self):
        if self.equivocaciones > self.errores:
            self.estado = "Detonada"

    def victoria(self): 
        if self.estado: 
            if self.modulos_restantes == 0: 
                self.estado = "Desactivada"

    def colocarFranja(self, timer):
        franhint = f"src/graphics/Modulo Timer/franja_{self.franja}.png"
        fran = pygame.image.load(franhint)
        timer.blit(fran, (0,0))

    def asignar_modulos(self): 
        if self.numero_modulos == 3:
            LISTA_MODULOS = ["Cables simples", "Cables complejos", "Código"]
        else:
            LISTA_MODULOS = ["Cables simples", "Cables complejos", "Memoria", "Código", "Exigente"]
        LISTA_MODULOS_SELECCIONADOS = []
        POSICIONES = [1, 2, 3, 4, 5]
        POSICIONESSELEC = []
        if self.modulos == []: 
            for i in range(0, self.numero_modulos):
                indice_elegido = randint(0, self.numero_modulos - i-1)
                LISTA_MODULOS_SELECCIONADOS.append(LISTA_MODULOS.pop(indice_elegido))
                
            for i in range(0, self.numero_modulos):
                indice_elegido = randint(0, self.numero_modulos - i -1)
                POSICIONESSELEC.append(POSICIONES.pop(indice_elegido))
            print(LISTA_MODULOS_SELECCIONADOS)

            for modulo in LISTA_MODULOS_SELECCIONADOS: 
                if modulo == "Cables simples": 
                    FRANJAS = ["amarilla", "rosada", "verde", "blanca"]
                    indice_elegido = randint(0, 3)
                    posicion = i
                    nuevo_modulo = ModuloCablesBasicos(self, FRANJAS[indice_elegido], 1)
                    nuevo_modulo.agregar_cables()
                    self.franja = nuevo_modulo.franja
                    print(nuevo_modulo.franja)
                    self.modulos.append(nuevo_modulo)
                    

                elif modulo == "Cables complejos":
                        nuevo_modulo = ModuloCablesComplejos(self,  4)
                        nuevo_modulo.agregar_cables()
                        nuevo_modulo.conectar_cables()
                        nuevo_modulo.asignacion_LED()
                        self.modulos.append(nuevo_modulo)
                        posicion = i

                elif modulo == "Memoria":
                        nuevo_modulo = ModuloPalabras(self, 4)
                        nuevo_modulo.agregar_lista()
                        self.modulos.append(nuevo_modulo)
                        posicion = i

                elif modulo == "Código":
                        LISTA_CODIGOS = ["ARBOL", "PUNTO", "GRAFO", "PILAS", "COLAS", 
                                        "LISTA", "NODOS", "CELDA", "DOBLE", "DATOS",
                                        "ORDEN", "TABLA", "CAMPO", "INDEX", "FILAS", 
                                        "GRUPO", "ERROR", "TEXTO", "BYTES", "VISTA",
                                        "AYUDA", "CLASE", "FILES", "EXCEL", "CICLO",
                                        "TEMAS", "NOTAS", "CREAR", "POINT", "ANTES",
                                        "TUPLA", "ARRAY", "BOMBA", "LINEA", "RUTAS"]
                        indice_elegido = randint(0, 34)
                        nuevo_modulo = ModuloCodigo(self, LISTA_CODIGOS[indice_elegido], 3)
                        nuevo_modulo.set_casillas_inicial()
                        self.modulos.append(nuevo_modulo)
                        posicion = i

                elif modulo == "Exigente":
                        nuevo_modulo = ModuloExigente(self, 2)
                        self.modulos.append(nuevo_modulo)
                        posicion = i