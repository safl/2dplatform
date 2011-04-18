#!/usr/bin/env python
import pygame
import glob
import math
import os

import directions as dirs
import states as states

sprite_map = {
    states.STANDING: {
        dirs.N:     [0],
        dirs.NE:    [0],
        dirs.E:     [0],
        dirs.SE:    [0],
        dirs.S:     [0],
        dirs.SW:    [0],
        dirs.W:     [24],
        dirs.NW:    [0]
    },
    states.RUNNING: {
        dirs.N:     [0],
        dirs.NE:    [0],
        dirs.E:     range(12,20),
        dirs.SE:    [0],
        dirs.S:     [0],
        dirs.SW:    [0],
        dirs.W:     range(36,44),
        dirs.NW:    [0]
    },
    states.IMPATIENT: {
        dirs.N:     range(2,6),
        dirs.NE:    range(2,6),
        dirs.E:     range(2,6),
        dirs.SE:    range(2,6),
        dirs.S:     range(2,6),
        dirs.SW:    range(2,6),
        dirs.W:     range(2,6),
        dirs.NW:    range(2,6)
        
    },
    states.IN_AIR: {
        dirs.N:     [12],
        dirs.NE:    [12],
        dirs.E:     [12],
        dirs.SE:    [12],
        dirs.S:     [36],
        dirs.SW:    [36],
        dirs.W:     [36],
        dirs.NW:    [36]
    }
}

class World:
    
    def __init__(self):
        
        self.gravity    = 20
        self.ground     = 0

class Scene:
    
    def __init__(self, screen, dim, images):
        
        self.width  = 3000
        
        self.screen = screen
        self.images = images
        self.dim = dim
        
        self.border = 200
        self.camera = 0
        
    def move(self, distance):
        self.camera += distance
        
        if self.camera < 0:
            self.camera = 0
        elif self.camera > self.width-self.dim[0]-1:
            self.camera = self.width - self.dim[0]-1
        
    def update(self):
        
        print self.camera
        screen_w, screen_h = self.dim
        self.screen.blit(self.images[0], (0,0))
        self.screen.blit(self.images[1].subsurface(self.camera/10,0, screen_w,  self.images[1].get_size()[1]), (0, screen_h-self.images[1].get_size()[1]))
        self.screen.blit(self.images[2], (0,0))
        self.screen.blit(self.images[3].subsurface(self.camera,0, screen_w,  self.images[3].get_size()[1]), (0, screen_h-self.images[3].get_size()[1]))

class Character:
    
    def __init__(self):
        
        self.state      = states.STANDING
        self.direction  = dirs.E
        
        self.velocity_x     = 18
        self.velocity_y     = 0
        self.jump_height    = 0
        self.x = 0
        self.y = 0
        
        self.w = 0
        self.h = 0

class Sprites:
    
    def __init__(self):
        
        self._current = 0
        self._sprites = []
            
    def load(self, path):
        
        for p in glob.glob(path):
            
            images = []
            sprite_map = pygame.image.load(p)
            
            map_w, map_h = sprite_map.get_size()
            for i in xrange(int(map_w/map_h)):
                images.append(
                    sprite_map.subsurface((i*map_h), 0, map_h, map_h)
                )
            for i in xrange(int(map_w/map_h)):
                images.append(
                    pygame.transform.flip(
                        sprite_map.subsurface((i*map_h), 0, map_h, map_h),
                        True,
                        False
                    )
                )
            
            self._sprites.append( images )
        
        for i in self._sprites:
            print len(i)
    
    def current(self):
        return self._sprites[self._current]
    
    def next(self):        
        self._current = (self._current + 1) % len(self._sprites)
        return self._sprites[self._current]
        
    def prev(self):
        self._current = (self._current + 1) % len(self._sprites)
        return self._sprites[self._current]

def draw(screen, dim, image):
    
    screen_w, screen_h = dim
    image_w, image_h = image.get_size()
    
    pos = (int((screen_w - image_w)/2), int((screen_h - image_h)/2))
    
    screen.blit(image, pos)

def main():
    
    screen_dim = screen_w, screen_h = (1280, 768)
    
    running     = True
    fullscreen  = False
        
    screen  = pygame.display.set_mode((screen_w, screen_h))    
    clock   = pygame.time.Clock()
    pygame.mouse.set_visible(False)
    
    back = [
        pygame.transform.scale(pygame.image.load('images/sky.png'), screen_dim),
        pygame.image.load('images/mountains.png'),
        pygame.image.load('images/trees.png'),
        pygame.image.load('images/ground.png'),
    ]
    s = Scene(screen, screen_dim, back)
    
    ground = pygame.image.load('images/ground.png')
    
    
    sprites = Sprites()
    sprites.load('sprites/sonic.png')
    
    images = sprites.current()
    ticks = 60
    
    w = World()
    w.ground = screen_h - back[3].get_size()[1]
    
    c = Character()
    c.velocity_x = 0.0
    c.velocity_y = 0.0
    c.direction = dirs.E
    c.state     = states.STANDING
    c.w = 87
    c.h = 87
    
    c.x = screen_w/2
    c.y = screen_h/2
    
    loop_range  = sprite_map[c.state][c.direction]
    i           = loop_range[0]
    
    impatient = 0
    
    while running:
        
        pressed = list(pygame.key.get_pressed())    # Grab input
        for event in pygame.event.get():
            
            if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                running = False
            
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode(
                        screen_dim,
                        pygame.FULLSCREEN                        
                    )
                else:
                    screen = pygame.display.set_mode( screen_dim )
            elif event.type == pygame.KEYDOWN and event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT]:
                pressed[event.key] = 1
            
        print pressed[pygame.K_LEFT], pressed[pygame.K_RIGHT], pressed[pygame.K_UP], pressed[pygame.K_DOWN]
        
        # Filter it
        if c.state != states.IN_AIR and pressed[pygame.K_UP] and not pressed[pygame.K_DOWN]:
            c.velocity_y = -100.0
            
        if pressed[pygame.K_DOWN] and not pressed[pygame.K_UP]:
            c.direction = dirs.S
            
        if not pressed[pygame.K_DOWN] and not pressed[pygame.K_UP]:
            pass
                       
        if pressed[pygame.K_LEFT] and not pressed[pygame.K_RIGHT]:
            c.direction     = dirs.W
            c.velocity_x    = -20.0
            
        if pressed[pygame.K_RIGHT] and not pressed[pygame.K_LEFT]:
            c.direction     = dirs.E
            c.velocity_x    = 20.0            
            
        if not pressed[pygame.K_RIGHT] and not pressed[pygame.K_LEFT]:
            c.velocity_x = 0.0
        
        
        # Move sonic or move the scene?
        if (c.direction == dirs.E and c.x+87 >= (screen_w - s.border)) or \
            (c.direction == dirs.W and c.x <= s.border):
            
            s.move(c.velocity_x)
        else:
            c.x += c.velocity_x
        
        c.y += c.velocity_y + w.gravity
        
        # Determine state
        if c.velocity_x == 0:
            c.state = states.STANDING
        else:
            c.state = states.RUNNING
        
        # Collision stuff
        if c.y+c.h >= w.ground:
            c.y = w.ground - c.h
            c.velocity_y = 0.0
        else:
            c.state = states.IN_AIR
        
        if c.state == states.IN_AIR:
            c.velocity_y += w.gravity
        
        if c.state == states.STANDING:
            impatient += 1
        else:
            impatient = 0        
        
        if impatient > 30:
            c.state = states.IMPATIENT
        
        loop_range  = sprite_map[c.state][c.direction]
        i = (i + 1) % len(loop_range)                
        image = images[loop_range[i]]
        image_w, image_h = image.get_size()
        
        center_pos = (int((screen_w - image_w)/2), int((screen_h - image_h)/2))
        
        s.update()
        screen.blit(image, (c.x, c.y))
        
        pygame.display.update()
        clock.tick(ticks)

if __name__ == "__main__":
    main()
