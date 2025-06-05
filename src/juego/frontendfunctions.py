import pygame

def varias_lineas(screen, font1, lineas, posy_inicial, posx):
    y = posy_inicial
    for linea in lineas:
        text_surface = font1.render(linea, True, (255, 255, 255))
        screen.blit(text_surface, (posx, y))
        y += text_surface.get_height() - 10  # 1 pixel de espacio entre líneas
        
def dibujar_jugadores(screen, font, lista_ids, x, y):
    
    for idx, jugador_id in enumerate(lista_ids[:4]):
        texto = f"- {jugador_id}"
        text_surface = font.render(texto, True, (0, 0, 0))
        screen.blit(text_surface, (x, y + idx * (text_surface.get_height())))
        
def centrar_texto(screen, rect, font, texto, ):
    text_rect = texto.get_rect(center=(rect.center))
    screen.blit(texto, text_rect)
    
def lista_a_texto(lista):
    return '\n'.join(str(elemento) for elemento in lista)

def varias_lineas_parrafo(screen, font1, lineas, posy_inicial, posx):
    y = posy_inicial
    for linea in lineas:
        text_surface = font1.render(linea, True, (0, 0, 0))
        screen.blit(text_surface, (posx, y))
        y += text_surface.get_height()   # 1 pixel de espacio entre líneas

def varias_lineas_con_scroll(screen, font, lineas, rect, scroll_y=0, header_text=None, header_font=None, subheader_text=None, subheader_font=None):
    """
    Dibuja múltiples líneas de texto con scroll, con header y subheader opcionales
    Args:
        screen: superficie donde dibujar
        font: fuente para el texto principal
        lineas: lista de líneas de texto principal
        rect: rectángulo que limita el área
        scroll_y: posición del scroll
        header_text: texto opcional para el encabezado
        header_font: fuente opcional para el encabezado
        subheader_text: texto opcional para el subencabezado
        subheader_font: fuente opcional para el subencabezado
    """
    altura_total = 0
    espaciado = 5
    superficies_texto = []
    
    # Crear header si existe
    if header_text and header_font:
        header_surface = header_font.render(header_text, True, (0, 0, 0))
        superficies_texto.append(("header", header_surface))
        altura_total += header_surface.get_height() + espaciado * 2
    
    # Crear subheader si existe
    if subheader_text and subheader_font:
        subheader_surface = subheader_font.render(subheader_text, True, (0, 0, 0))
        superficies_texto.append(("subheader", subheader_surface))
        altura_total += subheader_surface.get_height() + espaciado * 2
    
    # Crear superficies para el texto principal
    for linea in lineas:
        text_surface = font.render(linea, True, (0, 0, 0))
        superficies_texto.append(("texto", text_surface))
        altura_total += text_surface.get_height() + espaciado

    # Crear superficie temporal
    temp_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    
    # Dibujar textos con scroll
    pos_y = -scroll_y
    for tipo, surface in superficies_texto:
        if pos_y + surface.get_height() > 0 and pos_y < rect.height:
            if tipo in ["header", "subheader"]:
                # Centrar headers
                x = (rect.width - surface.get_width()) // 2
                temp_surface.blit(surface, (x, pos_y))
            else:
                # Texto normal alineado a la izquierda
                temp_surface.blit(surface, (0, pos_y))
        
        # Más espacio después de headers
        if tipo in ["header", "subheader"]:
            pos_y += surface.get_height() + espaciado * 2
        else:
            pos_y += surface.get_height() + espaciado

    screen.blit(temp_surface, rect)
    return altura_total  # Retornamos la altura total para calcular el máximo scroll

def formatear_reglas_para_tabla(reglas):
    filas = []
    for conectado_a, reglas_lista in reglas.items():  # 'A' o 'B'
        for regla in reglas_lista:
            naranja = "Sí" if (
                (regla.get('tipo') == 'color_led' and regla.get('color') == 'Naranja') or 
                (regla.get('tipo') == 'color' and regla.get('color') == 'Naranja')
            ) else "No"

            morado = "Sí" if (
                (regla.get('tipo') == 'color_led' and regla.get('color') == 'Morado') or 
                (regla.get('tipo') == 'color' and regla.get('color') == 'Morado')
            ) else "No"

            led = "Sí" if regla.get('tipo') in ['led', 'color_led'] else "No"

            cod = regla.get('accion', '?')
            value_enunciado = regla.get('value_enunciado', False)

            acc = "Ir a enunciados" if value_enunciado else (
                "Cortar el cable" if conectado_a == 'A' else "No cortar el cable"
            )

            filas.append([naranja, morado, led, conectado_a, cod + ": " + acc])
    return filas
