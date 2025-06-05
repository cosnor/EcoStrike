from random import randint, sample
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
                    posicion = i
                    nuevoModulo = ModuloCablesBasicos(self, FRANJAS[randint(0, 3)], 1)
                    nuevoModulo.agregar_cables()
                    self.franja = nuevoModulo.franja
                    print(nuevoModulo.franja)
                    self.modulos.append(nuevoModulo)

                elif modulo == "Cables complejos":

                        nuevoModulo = ModuloCablesComplejos(self,  4)
                        nuevoModulo.agregar_cables()
                        nuevoModulo.conectar_cables()
                        nuevoModulo.asignacion_LED()
                        self.modulos.append(nuevoModulo)
                        posicion = i

                elif modulo == "Memoria":
                        
                        nuevoModulo = ModuloPalabras(self, 4)
                        nuevoModulo.agregar_lista()
                        self.modulos.append(nuevoModulo)
                        posicion = i

                elif modulo == "Código":
                        
                        LISTA_CODIGOS = ["SOLAR", "VERDE", "FLORA", "FAUNA", "TERRA", 
                                        "MARES", "LAGOS", "HIELO", "CALOR", "OZONO",
                                        "CLIMA", "VEGAN", "CRUDO", "CICLO", "BIOMA", 
                                        "SALUD", "SAVIA", "GRANO", "ACIDO", "LIMBO",
                                        "MANTO", "SELVA", "RIOS", "CORAL", "POLAR",
                                        "SERES", "ALGAS", "TALAR", "RAMAS", "HUMUS",
                                        "FUEGO", "PLOMO", "TOXIN", "RIEGO", "PLAGA",
                                        "SUELO", "TIFON", "CENIT", "VAPOR", "BOMBA",
                                        "ARIDO", "HOJAS", "TURBA", "NUBES", "POLVO",
                                        "FOSIL", "FANGO", "ETICA", "NIEVE", "NICHO",
                                        "DELTA", "COSTA", "GASES", "SECAR", "AMBAR",
                                        "LIMON", "TUBOS", "CAMPO", "CACAO", "ARCES",
                                        "MIEDO", "ARENA", "BRUMA", "AGUAS", "CRECE",
                                        "OLMOS", "ACTOS", "LUCES"]
                        
                        N_LISTA_CODIGOS = sample(LISTA_CODIGOS, 34)  # Lista de códigos recortada

                        nuevoModulo = ModuloCodigo(self, N_LISTA_CODIGOS[randint(0, 33)], 3, N_LISTA_CODIGOS)
                        nuevoModulo.set_casillas_inicial()
                        self.modulos.append(nuevoModulo)
                        posicion = i

                elif modulo == "Exigente":
                        
                        nuevoModulo = ModuloExigente(self, 2)
                        self.modulos.append(nuevoModulo)
                        posicion = i