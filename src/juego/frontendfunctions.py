
def varias_lineas(screen, font1, lineas, posy_inicial, posx):
    y = posy_inicial
    for linea in lineas:
        text_surface = font1.render(linea, True, (255, 255, 255))
        screen.blit(text_surface, (posx, y))
        y += text_surface.get_height() - 10  # 1 pixel de espacio entre líneas
        
def dibujar_jugadores(screen, font, lista_ids, x, y):
    
    for idx, jugador_id in enumerate(lista_ids[:4]):
        texto = f"- Jugador {idx+1}"
        text_surface = font.render(texto, True, (0, 0, 0))
        screen.blit(text_surface, (x, y + idx * (text_surface.get_height())))
        
def centrar_texto(screen, rect, font, texto, ):
    text_rect = texto.get_rect(center=(rect.center))
    screen.blit(texto, text_rect)