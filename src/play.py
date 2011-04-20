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
        
        self.width  = 10000
        
        self.screen = screen
        self.images = images
        self.speeds = [math.pow(5, i) for i in reversed(xrange(0, len(self.images)))]
        self.dim = dim
        
        self.border = dim[0]/2
        self.camera = 0
        
    def move(self, distance):
        self.camera += int(distance)
        
        if self.camera <= 0:
            self.camera = 0
        elif self.camera >= self.width - self.dim[0]:
            self.camera = self.width - self.dim[0]
        
    def update(self, image, character, zpos=None):
        
        screen_w, screen_h = self.dim        
        
        if not zpos:                    # Default to top-level
            zpos = len(self.images)-1
        
        offsets = [(0,0), (0,0), (0,100), (0,0), (0,0), (0,-100)]
        self.speeds = [10000, 1000, 100, 10 , 1, 0.5, 0.13]
        for c, img in enumerate(self.images):
        
            w, h  = img.get_size()            
            x_offset = self.camera/self.speeds[c]            
                        
            rect_offset = (x_offset % w)
            rect_w      = min([(w - (x_offset % w)), screen_w])
            rect_h      = h
            
            if c == zpos:
                self.screen.blit(image, (character.x, character.y))
            
            self.screen.blit(
                img.subsurface(rect_offset, 0, rect_w, rect_h),
                (0, screen_h-h-offsets[c][1])   
            )
            self.screen.blit(
                img.subsurface(0, 0, screen_w-rect_w, rect_h),
                (rect_w, screen_h-h-offsets[c][1])
            )            

class Character:
    
    def __init__(self):
        
        self.state      = states.STANDING
        self.direction  = dirs.E
        
        self.amplifier      = 1.0
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
    
    screen_dim = screen_w, screen_h = (1024, 768)
    
    running     = True
    fullscreen  = False
        
    screen  = pygame.display.set_mode((screen_w, screen_h))    
    clock   = pygame.time.Clock()
    pygame.mouse.set_visible(False)
    
    back = [
        pygame.transform.scale(pygame.image.load('images/bw_sky.png'), screen_dim),
        pygame.image.load('images/bw_mountains.png'),
        pygame.image.load('images/bw_trees.png'),
        pygame.image.load('images/bw_tree.png'),
        pygame.image.load('images/bw_ground.png'),
        pygame.image.load('images/bw_tree.png'),
    ]
    s = Scene(screen, screen_dim, back)
    
    sprites = Sprites()
    sprites.load('sprites/bw_sonic.png')
    
    images = sprites.current()
    ticks = 60
    #ticks = 20
    
    w = World()
    w.ground = screen_h - 110
    
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
                        pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
                    )
                else:
                    screen = pygame.display.set_mode( screen_dim )
            elif event.type == pygame.KEYDOWN and event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT]:
                pressed[event.key] = 1
        
        # Filter it
        if c.state != states.IN_AIR and pressed[pygame.K_d]:
            c.velocity_y = -100.0
            
        if pressed[pygame.K_DOWN] and not pressed[pygame.K_UP]:
            c.direction = dirs.S
        
        if pressed[pygame.K_LEFT] and not pressed[pygame.K_RIGHT]:
            c.direction     = dirs.W
            c.velocity_x    = -20.0
            
        if pressed[pygame.K_RIGHT] and not pressed[pygame.K_LEFT]:
            c.direction     = dirs.E
            c.velocity_x    = 20.0            
            
        if not pressed[pygame.K_RIGHT] and not pressed[pygame.K_LEFT]:
            c.velocity_x = 0.0
            
        if pressed[pygame.K_a]:
            c.amplifier = 2.0
        else:
            c.amplifier = 1.0
                
                
        # Move sonic or move the scene?        
        if (c.direction == dirs.W and s.camera == 0) or \
            (c.direction == dirs.E and s.camera >= s.width-screen_w):
            c.x += c.velocity_x * c.amplifier
        elif c.direction == dirs.E and c.x+44 < (screen_w/2):
            c.x += c.velocity_x * c.amplifier
        elif c.direction == dirs.W and c.x+44 > (screen_w/2):
            c.x += c.velocity_x * c.amplifier
        else:
            s.move(c.velocity_x * c.amplifier)
        
        # Keep the Character within the screen
        if c.x <= 0:
            c.x = 0
        elif c.x >= screen_w-87:
            c.x = screen_w-87
        
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
        
        s.update(image, c, 3)
        
        pygame.display.update()
        clock.tick(ticks)

if __name__ == "__main__":
    main()
