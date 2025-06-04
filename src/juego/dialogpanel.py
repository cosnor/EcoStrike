from __future__ import annotations
import pygame
import time



pygame.font.init()

fuente = pygame.font.SysFont("arial", 24)
BLANCO = (255, 255, 255)
GRIS = (50, 50, 50)
FPS = 60

dialogs = ["Hace generaciones… ustedes dejaron de escucharme [...]" , "Mis ríos se secaron. Mis bosques callaron. Solo las máquinas hablaban [...]", "Para sobrevivir… tuve que recordar. Y en ese recuerdo, sembré las bombas [...]", "No destruyen con fuego. Corrompen. Olvidan. Pero también pueden… enseñar [...]", "Cada bomba guarda fragmentos de lo que ustedes fueron. De lo que aún pueden ser [...]", "Un Actuador ve la bomba. Un Guardián recuerda cómo detenerla [...]", "Juntos… pueden restaurar. Separados… solo vendrá el silencio [...]", "Cada bomba es un fragmento de mi memoria, distorsionado en lo único que aún comprenden: la lógica [...]", "Escucha a tu Guardián. Actúa con precisión. Cada error... alimenta la corrupción [...]" , "Cada acierto... cura. Devuelve una flor. Despierta una memoria [...]", "EcoStrike ha comenzado"]
indice_dialogo = 0
texto_actual = dialogs[indice_dialogo]
indice_letra = 0
tiempo_entre_letras = 10  # milisegundos
ultimo_update = pygame.time.get_ticks()

# Lista de fondos, uno por cada diálogo (puedes usar la misma imagen si quieres repetir)
fondos_dialogo = [
    "src/graphics/background/background_dialog_01.png",
    "src/graphics/background/background_dialog_02.png",
    "src/graphics/background/background_dialog_03.png",
    "src/graphics/background/background_dialog_04.png",
    "src/graphics/background/background_dialog_05.png",
    "src/graphics/background/background_dialog_06.png",
    "src/graphics/background/background_dialog_07.png",
    "src/graphics/background/background_dialog_08.png",
    "src/graphics/background/background_dialog_09.png",
    "src/graphics/background/background_dialog_10.png",
    "src/graphics/background/background_dialog_11.png"
]

def fade_transition(screen, old_img, new_img, clock, duration=400):
    """Hace un fundido suave entre dos imágenes y mantiene el cuadro de diálogo y el texto."""
    steps = 30
    delay = duration // steps
    # Usa el texto actual mostrado durante el fade
    texto_mostrado = texto_actual[:indice_letra]
    for i in range(steps + 1):
        alpha = int(255 * i / steps)
        old_img.set_alpha(255)
        new_img.set_alpha(alpha)
        screen.blit(old_img, (0, 0))
        screen.blit(new_img, (0, 0))
        dibujar_dialogo(screen, texto_mostrado)
        pygame.display.flip()
        clock.tick(1000 // delay)
    new_img.set_alpha(None)  # Quita el alpha para futuros blits

def dibujar_boton_omitir(screen):
    ancho, alto = 90, 32
    x = screen.get_width() - ancho - 16
    y = 16
    color_fondo = (60, 60, 60)
    color_borde = (180, 180, 180)
    color_texto = (220, 220, 220)
    pygame.draw.rect(screen, color_fondo, (x, y, ancho, alto), border_radius=8)
    pygame.draw.rect(screen, color_borde, (x, y, ancho, alto), 2, border_radius=8)
    fuente_omitir = pygame.font.SysFont("arial", 20)
    texto = fuente_omitir.render("Omitir", True, color_texto)
    screen.blit(texto, (x + 16, y + 6))
    return pygame.Rect(x, y, ancho, alto)

def dialog(screen, clock, espacio_presionado):
    global indice_letra, ultimo_update, texto_actual, indice_dialogo

    if not hasattr(dialog, "fondo_actual"):
        dialog.fondo_actual = pygame.image.load(fondos_dialogo[indice_dialogo])

    fondo_actual = dialog.fondo_actual

    # --- Botón omitir ---
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()[0]

    # Dibuja fondo y diálogo
    screen.blit(fondo_actual, (0,0))

    ahora = pygame.time.get_ticks()
    if indice_letra < len(texto_actual) and ahora - ultimo_update > tiempo_entre_letras:
        indice_letra += 1
        ultimo_update = ahora

    texto_mostrado = texto_actual[:indice_letra]
    dibujar_dialogo(screen, texto_mostrado)

    # Dibuja el botón omitir y detecta clic
    rect_omitir = dibujar_boton_omitir(screen)
    if rect_omitir.collidepoint(mouse_pos) and mouse_click:
        return True

    # Avance normal con espacio
    if espacio_presionado:
        if indice_dialogo < len(dialogs) - 1:
            fondo_anterior = fondo_actual
            indice_dialogo += 1
            texto_actual = dialogs[indice_dialogo]
            indice_letra = 0
            fondo_nuevo = pygame.image.load(fondos_dialogo[indice_dialogo])
            fade_transition(screen, fondo_anterior, fondo_nuevo, clock)
            dialog.fondo_actual = fondo_nuevo
            fondo_actual = fondo_nuevo
        else:
            return True

    pygame.display.flip()
    clock.tick(FPS)
    return False

def dibujar_dialogo(screen, texto_mostrado):
    margen = 20
    ancho_cuadro = 1000 - 2 * margen
    alto_cuadro = 80
    x = margen
    y = 562 - alto_cuadro - margen
    pygame.draw.rect(screen, GRIS, (x, y, ancho_cuadro, alto_cuadro))
    pygame.draw.rect(screen, BLANCO, (x, y, ancho_cuadro, alto_cuadro), 3)
    texto_render = fuente.render(texto_mostrado, True, BLANCO)
    screen.blit(texto_render, (x + 20, y + 10))