import pygame as pg

CAPTION = "Holy Guacamole"
SCREEN_SIZE = (700,500)

class Physics(object):
    def __init__(self):
        # x and y cooridinates of movement
        self.velocity = [0, 0]
        self.grav = .3  
        self.fall = False

    def physics_update(self):
        #if player is falling add effect of gravity
        if self.fall:
            self.velocity[1] += self.grav
        else:
            self.velocity[1] = 0

class Player(Physics, pg.sprite.Sprite):
    def __init__(self,location,speed):
        Physics.__init__(self)
        pg.sprite.Sprite.__init__(self)
        #import image of advocado
        self.frame_start_pos = None
        self.image = pg.image.load('advocado.png').convert_alpha()
        self.image = pg.transform.scale(self.image, (30, 55))
        self.rect = self.image.get_rect(topleft=location)
        self.speed = speed
        self.jump_height = -9.0
        self.jump_release_height= -3.0
        self.collide_below = False
        self.total_displacement = None
        self.on_moving = False

    def check_keys(self, keys):
        # left-right movement
        self.velocity[0] = 0
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.velocity[0] -= self.speed
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.velocity[0] += self.speed

    def check_position(self, obstacles):
        #check if player is falling
        if not self.fall:
            self.check_falling(obstacles)
        else:
            #check vertical movement collisions (y axis)
            self.fall = self.check_collisions((0,self.velocity[1]),1,obstacles)
        #check horizontal movement collisions (x axis)
        if self.velocity[0]:
            self.check_collisions((self.velocity[0],0), 0, obstacles)

    def check_falling(self, obstacles):
        #make player fall if not in contact with ground
        if not self.collide_below:
            self.fall = True
           
    def check_collisions(self, offset, index, obstacles):
        #if collision detected either on x or y axis adjust position 
        unaltered = True
        self.rect[index] += offset[index]
        while pg.sprite.spritecollideany(self, obstacles):
            self.rect[index] += (1 if offset[index]<0 else -1)
            unaltered = False
        return unaltered

    def check_below(self, obstacles):
        #detect and position player on the ground
        self.rect.move_ip((0,1))
        collide = pg.sprite.spritecollide(self, obstacles, False)
        self.rect.move_ip((0,-1))
        return collide

    def check_moving(self,obstacles):
        if not self.fall:
            now_moving = self.on_moving
            any_moving, any_non_moving = [], []
            for collide in self.collide_below:
                if collide.type == "moving":
                    self.on_moving = collide
                    any_moving.append(collide)
                else:
                    any_non_moving.append(collide)
            if not any_moving:
                self.on_moving = False
            elif any_non_moving or now_moving in any_moving:
                self.on_moving = now_moving

    def jump(self, obstacles):
        if not self.fall:
            self.velocity[1] += self.jump_height
            self.fall = True

    def jump_release(self):
        if self.fall:
            if self.velocity[1] < self.jump_release_height:
                self.velocity[1] = self.jump_release_height

    def update(self, obstacles, keys):
        # self.check_moving(obstacles)

        self.frame_start_pos = self.rect.topleft
        self.collide_below = self.check_below(obstacles)
        self.check_keys(keys)
        self.check_position(obstacles)
        self.physics_update()
        start = self.frame_start_pos
        end = self.rect.topleft
        self.total_displacement = (end[0]-start[0], end[1]-start[1])
      
    def draw(self, surface):
        #blit player onto level
        surface.blit(self.image, self.rect)

class Block(pg.sprite.Sprite):
    #class for all obstacles within level
    def __init__(self, color, rect):
        pg.sprite.Sprite.__init__(self)
        self.rect = pg.Rect(rect)
        self.image = pg.Surface(self.rect.size).convert()
        self.image.fill(color)
        self.type = "normal"


class Control(object):
   #class that controls game loop and states
    def __init__(self):
        #game/level initialization declarations
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.keys = pg.key.get_pressed()
        self.done = False
        self.player = Player((50,2920), 4)
        self.level = pg.Surface((1000,3000)).convert()
        self.level_rect = self.level.get_rect()
        self.win_text,self.win_rect = self.make_text()
        self.viewport = self.screen.get_rect(bottom=self.level_rect.bottom)
        self.obstacles = self.make_obstacles()

    def make_text(self):
        """Renders a text object. Text is only rendered once."""
        font = pg.font.Font(None, 100)
        message = "Holy Guacamole!!"
        text = font.render(message, True, (100,100,175))
        rect = text.get_rect(centerx=self.level_rect.centerx, y=1800)
        return text, rect

    def make_obstacles(self): 
        #add obstacles to sprite.Group
        walls = [Block(pg.Color(75,0,130,0), (0,2980,1000,20)),
                 Block(pg.Color(64,224,208,0), (0,2988,1000,4)),
                 Block(pg.Color(75,0,130,0), (0,0,20,3000)),
                 Block(pg.Color(64,224,208,0), (8,0,4,3000)),
                 Block(pg.Color(75,0,130,0), (980,0,20,3000))]
        static = [
                #   Block(pg.Color("pink"), (70,920,10,2100)),
                  Block(pg.Color(75,0,130,0), (350,2850,200,40)),
                  Block(pg.Color(75,0,130,0), (350,2650,40,240)),
                  Block(pg.Color(75,0,130,0), (600,2880,200,100)),
                  Block(pg.Color("red"), (300,2780,50,20)),
                  Block(pg.Color("red"), (20,2630,50,20)),
                  Block(pg.Color("red"), (80,2530,50,20)),
                  Block(pg.Color(75,0,130,0), (20,2760,80,20)),
                  Block(pg.Color(75,0,130,0), (20,2860,350,30)),
                  Block(pg.Color("yellow"), (600,2740,30,40)),
                  Block(pg.Color("green"), (130,2470,170,215)),
                  Block(pg.Color("green"), (530,2500,20,10)),
                  Block(pg.Color("green"), (800,2470,20,10)),
                  Block(pg.Color("green"), (850,2320,20,10)),
                  Block(pg.Color("green"), (900,2190,20,10)),
                  Block(pg.Color("green"), (450,2100,400,10)) 
                  
                  ]
        return pg.sprite.Group(walls, static)

    def update_viewport(self, speed):
        self.viewport.center = self.player.rect.center
        self.viewport.clamp_ip(self.level_rect)

    def event_loop(self):
        #enable player to always be able to quit or jump
        for event in pg.event.get():
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump(self.obstacles)
            elif event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_release()

    def update(self):
        #update player and movements within level
        self.keys = pg.key.get_pressed()
        self.player.update(self.obstacles, self.keys)
        self.update_viewport(self.player.total_displacement)

    def draw(self):
        #draw all objects into level
        self.level.fill(pg.Color(230,230,250, 0), self.viewport)
        self.obstacles.draw(self.level)
        self.level.blit(self.win_text, self.win_rect)
        self.player.draw(self.level)
        self.screen.blit(self.level, (0,0), self.viewport)

    def main_loop(self):
        #game loop
        while not self.done:
            self.event_loop()
            self.update()
            self.draw()
            pg.display.update()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    pg.init()
    pg.display.set_mode(SCREEN_SIZE, pg.FULLSCREEN)
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    
