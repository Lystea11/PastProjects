import pygame
from pygame.locals import *
import random

pygame.init()

gameover = False
flying = True
scroll = 0
screen_width = 864
screen_height = 936
fps = 60
clock = pygame.time.Clock()
bg = pygame.image.load("assets/bg.png")
ground = pygame.image.load("assets/ground.png")

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy bird (fake)")

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/pipe.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
    def update(self):
        pass

class bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for i in range(1,4):
            temp = pygame.image.load(f"assets/bird{i}.png")
            self.images.append(temp)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.vel = 0

    def update(self):
        global gameover,flying
        if self.rect.bottom >= 700:
            gameover = True
            flying = False

        if flying == True:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8

            if self.rect.bottom <= 700:
                self.rect.y += self.vel
        if gameover == False:
            keystate = pygame.key.get_pressed()
            if keystate[pygame.K_SPACE] == 1 and self.rect.top > 20:
                self.vel = -10


            cooldown = 5
            self.counter +=1

            if self.counter > cooldown:
                self.counter = 0
                self.index += 1

                if self.index >= 3:
                    self.index = 0

            self.image = self.images[self.index]

            self.image = pygame.transform.rotate(self.images[self.index], self.vel*-2 )
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)


birdgroup = pygame.sprite.Group()
flappy = bird(100,screen_height/2)
birdgroup.add(flappy)

pipegroup = pygame.sprite.Group()
pipe = Pipe(500, 10)
pipegroup.add(pipe)



while True:
    clock.tick(fps)

    screen.blit(bg,(0,0))

    birdgroup.draw(screen)
    birdgroup.update()
    pipegroup.draw(screen)

    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            pygame.quit()

    screen.blit(ground, (scroll, 700))
    if gameover == False:
        scroll -= 4
        if scroll <= -36:
            scroll = 0

    pygame.display.update()