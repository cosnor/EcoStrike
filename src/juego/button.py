import pygame
class Button:
    def __init__(self, screen, x, y, width, height, text, color, size):
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font("src/font/Pixeled.ttf", 20)
        self.size = size

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.screen.blit(text_surface, text_rect)

    def handle_event(self, event, funcion):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                funcion()
    
class ButtonC:
    def __init__(self, screen1, screen2, x, y, cable, modulo, width, height):
        self.screen1 = screen1 #screen
        self.screen2 = screen2 #modulo (coords)
        self.cable = cable
        self.modulo = modulo
        self.x, self.y = x, y
        self.rect_topleft = (self.x+ screen2[0], self.y+ screen2[1])
        self.width, self.height = width, height
        self.rect = pygame.Rect(self.rect_topleft[0], self.rect_topleft[1], self.width, self.height)
        self.imagen = None
        
    def draw(self):
        #pygame.draw.rect(self.screen1, (0,0,0), self.rect)
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                self.modulo.cortar_cable(self.cable)
                pygame.time.wait(10)
                if self.cable.estado: 
                    self.imagen = self.cable.icono_cable_cortado
                
    #draw button on screen
        if self.cable.estado: 
            self.imagen = self.cable.icono_cable_cortado
        else:
            self.imagen = self.cable.icono_cable
            
        self.screen1.blit(self.imagen, (self.cable.posx + self.screen2[0], self.cable.posy + self.screen2[1]))
        
            
class ButtonJ:
    
    def __init__(self, screen1, screen2, x, y, width, height, text, color, size):
        self.screen1 = screen1 #screen
        self.screen2 = screen2 #modulo (coords)
        self.rect = pygame.Rect(x+ screen2[0], y+ screen2[1], width, height)
        self.text = text
        self.color = color
        self.size = size
        self.font = pygame.font.Font("src/font/Pixeled.ttf", self.size)

    def draw(self):
        pygame.draw.rect(self.screen1, self.color, self.rect)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.screen1.blit(text_surface, text_rect)
        
    def handle_event(self, event, funcion):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                funcion()
            pygame.time.wait(1)
                

class ButtonN:
    def __init__(self, screen1, x, y, width, height,  numero):
        self.screen1 = screen1 #screen
        self.numero = numero
        self.x, self.y = x, y
        #self.rect_topleft = (self.x+ screen2[0], self.y+ screen2[1])
        self.width, self.height = width, height
        #self.rect = pygame.Rect(self.rect_topleft[0], self.rect_topleft[1], self.width, self.height)
        self.imagen = numero.icono_numero  


class ButtonM:
    def __init__(self, screen, x, y, width, height, text, color):
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font("src/font/Pixeled.ttf", 20)

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.screen.blit(text_surface, text_rect)
                
    def handle_event1(self, event, posicionreal, funcion):
        if event.type == pygame.MOUSEBUTTONDOWN:
            rect_cambio = pygame.Rect(self.rect.x + posicionreal[0], self.rect.y + posicionreal[1], self.rect.width, self.rect.height)
            if rect_cambio.collidepoint(event.pos):
                funcion()
            pygame.time.wait(10)