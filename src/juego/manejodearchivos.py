class ManejoDeArchivos:
    
    def __init__(self) -> None:
        self.rutaConfigjuego = "src/files/configuraciondeljuego.txt"
    
    def leerConfiguracion(self):
        archivo = open(self.rutaConfigjuego, "r")
        lineas = archivo.readlines()
        archivo.close()
        return lineas
    
    def escribirConfiguracion(self, lineas):    
        archivo = open(self.rutaConfigjuego, "a")  # Abre el archivo en modo "append"
        archivo.writelines(lineas+"\n")
        archivo.close()
        
    def limpiarArchivo(self):
        archivo = open(self.rutaConfigjuego, "w")
        archivo.close()