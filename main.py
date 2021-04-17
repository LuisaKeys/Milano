import pygame
from pygame.locals import *
import os
from pygame import mixer
import random

pygame.init()

OP = pygame.image.load("assets/op1.jpg")
pygame.mixer.music.load("sons/Escape.mp3")
pygame.mixer.music.play(-1)

os.environ['SDL_VIDEO_CENTERED'] = '1'

largura = 600
altura = 700
tela = pygame.display.set_mode((largura, altura))

def text_format(message, textFont, textSize, textColor):
    newFont=pygame.font.Font(textFont, textSize)
    newText=newFont.render(message, 0, textColor)

    return newText

vermelho = (255, 0, 0)
verde = (0, 255, 0)
gold=(255, 193, 37)
OR = (139, 37, 0)

font = "assets/Early GameBoy.ttf"

clock = pygame.time.Clock()
FPS = 60

def jogo():
    mixer.init()
    pygame.init()
    explosão_wav = pygame.mixer.Sound("sons/explosão.wav")
    explosão_wav.set_volume(0.15)
    laser_wav = pygame.mixer.Sound("sons/laser.wav")
    laser_wav.set_volume(0.15)

    clock = pygame.time.Clock()
    fps = 60

    rows = 5
    cols = 5
    inimigo_cooldown = 1000
    ultimo_laser_inimigo = pygame.time.get_ticks()
    game_over = 0

    BG = pygame.image.load("assets/bg.png")
    PS = pygame.image.load("assets/pausa.jpg")

    def draw_BG():
        tela.blit(BG, (0, 0))

    def pause():
        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        quit()
                tela.blit(PS, (0, 0))
                pygame.display.flip()
                clock.tick(5)

    def GAME_OVER():
        if game_over == -1:
            FIM = pygame.image.load("assets/fim_de_jogo.jpg")
        if game_over == 1:
            FIM = pygame.image.load("assets/ganhou.jpg")

        menu = True
        selected = "start"

        while menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = "start"
                    elif event.key == pygame.K_DOWN:
                        selected = "quit"
                    if event.key == pygame.K_RETURN:
                        if selected == "start":
                            main_menu()
                        if selected == "quit":
                            pygame.quit()
                            quit()

            tela.blit(FIM, (0, 0))


            if selected == "start":
                text_start = text_format("VOLTAR", font, 40, gold)
            else:
                text_start = text_format("VOLTAR", font, 30, gold)
            if selected == "quit":
                text_quit = text_format("SAIR", font, 40, gold)
            else:
                text_quit = text_format("SAIR", font, 30, gold)

            start_rect = text_start.get_rect()
            quit_rect = text_quit.get_rect()

            tela.blit(text_start, (largura / 2 - (start_rect[2] / 2), 450))
            tela.blit(text_quit, (largura / 2 - (quit_rect[2] / 2), 500))
            pygame.display.update()

    class Nave(pygame.sprite.Sprite):
        def __init__(self, x, y, health):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load("assets/nave.png")
            self.rect = self.image.get_rect()
            self.rect.center = [x, y]
            self.health_start = health
            self.health_remaining = health
            self.last_shot = pygame.time.get_ticks()

        def update(self):

            vel = 25
            game_over = 0
            cooldown = 400

            chave = pygame.key.get_pressed()
            if chave[pygame.K_a] and self.rect.x - vel > 0:
                self.rect.x -= vel
            if chave[pygame.K_d] and self.rect.x + vel + 140 < largura:
                self.rect.x += vel
            if chave[pygame.K_w] and self.rect.y - vel > 400:
                self.rect.y -= vel
            if chave[pygame.K_s] and self.rect.y + vel + 70 < altura:
                self.rect.y += vel
            time_now = pygame.time.get_ticks()

            mouse = pygame.mouse.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP and time_now - self.last_shot > cooldown:
                    laser_wav.play()
                    lasers = Lasers(self.rect.centerx, self.rect.top)
                    lasers_group.add(lasers)
                    self.last_shot = time_now

            self.mask = pygame.mask.from_surface(self.image)

            pygame.draw.rect(tela, vermelho, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 10))
            if self.health_remaining > 0:
                pygame.draw.rect(tela, verde, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 10))
            elif self.health_remaining <= 0:
                game_over = -1
                self.kill()
            return game_over

    class Lasers(pygame.sprite.Sprite):
        def __init__(self, x, y):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load("assets/laser.png")
            self.rect = self.image.get_rect()
            self.rect.center = [x, y]

        def update(self):
            self.rect.y -= 5
            if self.rect.bottom < 0:
                self.kill()
            if pygame.sprite.spritecollide(self, inimigos_group, True):
                self.kill()

                explosão = Explosão(self.rect.centerx, self.rect.centery, 2)
                explosão_group.add(explosão)
                explosão_wav.play()

    class Inimigos(pygame.sprite.Sprite):
        def __init__(self, x, y):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load("assets/inimigo.png")
            self.rect = self.image.get_rect()
            self.rect.center = [x, y]
            self.move_counter = 0
            self.move_direction = 1

        def update(self):
            self.rect.x += self.move_direction
            self.move_counter += 1
            if abs(self.move_counter) > 75:
                self.move_direction *= -1
                self.move_counter *= self.move_direction

    class Lasers_Inimigos(pygame.sprite.Sprite):
        def __init__(self, x, y):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load("assets/laser_inimgo.png")
            self.rect = self.image.get_rect()
            self.rect.center = [x, y]

        def update(self):
            self.rect.y += 2
            if self.rect.top > altura:
                self.kill()
            if pygame.sprite.spritecollide(self, nave_group, False, pygame.sprite.collide_mask):
                self.kill()
                nave.health_remaining -= 1
                explosão = Explosão(self.rect.centerx, self.rect.centery, 1)
                explosão_group.add(explosão)

    class Explosão(pygame.sprite.Sprite):
        def __init__(self, x, y, size):
            pygame.sprite.Sprite.__init__(self)
            self.images = []
            for num in range(1, 6):
                img = pygame.image.load(f"assets/exp{num}.png")
                if size == 1:
                    img = pygame.transform.scale(img, (20, 20))
                if size == 2:
                    img = pygame.transform.scale(img, (40, 40))
                if size == 3:
                    img = pygame.transform.scale(img, (160, 160))

                self.images.append(img)
            self.index = 0
            self.image = self.images[self.index]
            self.rect = self.image.get_rect()
            self.rect.center = [x, y]
            self.counter = 0

        def update(self):
            explosão_vel = 3
            self.counter += 1

            if self.counter >= explosão_vel and self.index < len(self.images) - 1:
                self.counter = 0
                self.index += 1
                self.image = self.images[self.index]

            if self.index >= len(self.images) - 1 and self.counter >= explosão_vel:
                self.kill()

    nave_group = pygame.sprite.Group()
    lasers_group = pygame.sprite.Group()
    inimigos_group = pygame.sprite.Group()
    lasers_inimigos_group = pygame.sprite.Group()
    explosão_group = pygame.sprite.Group()

    def create_inimigos():
        for row in range(rows):
            for item in range(cols):
                inimigo = Inimigos(100 + item * 100, 100 + row * 70)
                inimigos_group.add(inimigo)

    create_inimigos()

    nave = Nave(int(largura / 2), altura - 100, 3)
    nave_group.add(nave)

    run = True
    while run:
        draw_BG()
        clock.tick(fps)
        time_now = pygame.time.get_ticks()
        if time_now - ultimo_laser_inimigo > inimigo_cooldown and len(lasers_inimigos_group) < 5 and len(
                inimigos_group) > 0:
            attacking_inimigo = random.choice(inimigos_group.sprites())
            lasers_inimigos = Lasers_Inimigos(attacking_inimigo.rect.centerx, attacking_inimigo.rect.bottom)
            lasers_inimigos_group.add(lasers_inimigos)
            ultimo_laser_inimigo = time_now

        if len(inimigos_group) == 0:
            game_over = 1

        if game_over == 0:
            game_over = nave.update()
            lasers_group.update()
            lasers_inimigos_group.update()
            inimigos_group.update()
        else:
            GAME_OVER()

        explosão_group.update()

        nave_group.draw(tela)
        lasers_group.draw(tela)
        inimigos_group.draw(tela)
        lasers_inimigos_group.draw(tela)
        explosão_group.draw(tela)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause()
        pygame.display.update()

    pygame.quit()

def COMO_JOGAR():

    como_jogar = pygame.image.load("assets\como_jogar.jpg")

    menu = True
    selected = "start"

    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = "start"
                elif event.key == pygame.K_DOWN:
                    selected = "quit"
                if event.key == pygame.K_RETURN:
                    if selected == "start":
                        main_menu()
                    if selected == "quit":
                        pygame.quit()
                        quit()

        tela.blit(como_jogar, (0, 0))


        if selected == "start":
            text_start = text_format("VOLTAR", font, 30, gold)
        else:
            text_start = text_format("VOLTAR", font, 20, gold)
        if selected == "quit":
            text_quit = text_format("SAIR", font, 30, gold)
        else:
                text_quit = text_format("SAIR", font, 20, gold)

        start_rect = text_start.get_rect()
        quit_rect = text_quit.get_rect()

        tela.blit(text_start, (largura / 2 - (start_rect[2] / 2), 620))
        tela.blit(text_quit, (largura / 2 - (quit_rect[2] / 2), 650))
        pygame.display.update()

def main_menu():

    menu = True
    selected="start"
    cj_text = text_format("aperte 'f' para saber como jogar", font, 15, gold)

    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = "start"
                elif event.key == pygame.K_DOWN:
                    selected = "quit"
                if event.key == pygame.K_f:
                   COMO_JOGAR()
                if event.key == pygame.K_RETURN:
                    if selected == "start":
                        print("Start")
                        jogo()
                    if selected == "quit":
                        pygame.quit()
                        quit()

        tela.blit(OP, (0, 0))

        if selected == "start":
            text_start = text_format("START", font, 40, gold)
        else:
            text_start = text_format("START", font, 30, gold)

        if selected == "quit":
            text_quit = text_format("QUIT", font, 40, gold)
        else:
            text_quit = text_format("QUIT", font, 30, gold)


        start_rect = text_start.get_rect()
        quit_rect = text_quit.get_rect()
        cj_rect = cj_text.get_rect()

        tela.blit(text_start, (largura/2 - (start_rect[2]/2), 450))
        tela.blit(text_quit, (largura/2 - (quit_rect[2]/2), 500))
        tela.blit(cj_text, (largura / 2 - (cj_rect[2] / 2), 630))
        pygame.display.update()
        clock.tick(FPS)
        pygame.display.set_caption("Menu - Milano")

main_menu()
pygame.quit()
quit()
