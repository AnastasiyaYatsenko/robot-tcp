import pygame

class InputBox:

    def __init__(self, x, y, w = 140, h = 32):

        self.font = pygame.font.Font(None, 32)

        self.inputBox = pygame.Rect(x, y, w, h)

        self.colourInactive = pygame.Color('lightskyblue3')
        self.colourActive = pygame.Color('dodgerblue2')
        self.colour = self.colourInactive

        self.text = ''

        self.active = False
        self.isBlue = True

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.inputBox.collidepoint(event.pos)
            self.colour = self.colourActive if self.active else self.colourInactive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    text = self.text[:-1]
                    self.text = ''
                    self.text = text
                else:
                    if event.unicode.isdigit():
                        self.text += event.unicode

    def draw(self, screen):
        txtSurface = self.font.render(self.text, True, self.colour)
        width = self.inputBox.width#max(200, txtSurface.get_width()+10)
        self.inputBox.w = width
        screen.blit(txtSurface, (self.inputBox.x+5, self.inputBox.y+5))
        pygame.draw.rect(screen, self.colour, self.inputBox, 2)

        if self.isBlue:
            self.color = (0, 128, 255)
        else:
            self.color = (255, 100, 0)
