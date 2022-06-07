import pygame
from pygame.locals import *
import pymunk
import random

pygame.init()

clock=pygame.time.Clock()
fps=30

screen_width=1100
screen_height=700

BLACK=(0,0,0)
WHITE=(255,255,255)
BLUE=(0,0,255)
RED=(255,0,0)
GREEN=(0,255,0)
LIGHT_GREY=(220,220,220)
DARK_GREY=(30,30,30)

bg_image = pygame.image.load( 'img/bg.png' )
dog1_image = pygame.image.load( 'img/dog1.png' )
dog2_image = pygame.image.load( 'img/dog2.png' )
arrow_image = pygame.image.load( 'img/arrow.png' )
feetus_image = pygame.image.load( 'img/feetus.png' )
hand_image = pygame.image.load( 'img/hand.png' )
trash_can_image = pygame.image.load( 'img/trash_can.png' )
plus1_image = pygame.image.load( 'img/plus1.png' )
minus2_image = pygame.image.load( 'img/minus2.png' )
super_image = pygame.image.load( 'img/super.png' )

screen=pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Let Us Yeetus The Feetus')
space=pymunk.Space()
gravity = -30

GRID_FONT = pygame.font.Font('font/impact.ttf', 10)
SCORE_FONT = pygame.font.Font('font/impact.ttf', 30)
WIND_FONT = pygame.font.Font('font/impact.ttf', 20)
RESTART_FONT = pygame.font.Font('font/impact.ttf', 25)

throwing_height = screen_height//2+20
score = 0
new_feetus_cooldown = 55
floor_height = screen_height-75
show_hand = True
dump_feetus = True

def draw_bg():

    global bg_image

    bg = pygame.transform.scale( bg_image, [screen_width+70,screen_height+70] )
    screen.blit( bg, (0, 0) )
    Restart.draw()

def draw_text( text, x, y, font, text_col = WHITE ):
    img = font.render( str(text) ,True ,text_col )
    screen.blit(img,(x,y))

def out_of_box( x, y, r ):
    return (0>x+r)or(screen_width<x-r)or(0>y+r)or(screen_height<y-r)

def in_trash( feetus, trash_can ):

    x, y = feetus.body.position

    if y > trash_can.u-20:
        if trash_can.l < x < trash_can.r:
            return True

    else:
        return False

def draw_grids( color ):
    for y in range(10,screen_height,10):
        draw_text(y,0,y,GRID_FONT)
        pygame.draw.line( screen, color, (10,y),(screen_width,y), 1 )
    for x in range(10,screen_width,10):
        draw_text(x,x,0,GRID_FONT)
        pygame.draw.line( screen, color, (x,10),(x,screen_height), 1 )

def display_hand( x, y ):

    img = hand_image
    img = pygame.transform.scale( img, [800,900] )
    screen.blit( img, [x-720,y-60] )
    

class Restart():

    rect = pygame.Rect( 0,0, 135,45 )
    text = "Restart"


    def draw():

        pygame.draw.rect( screen, DARK_GREY, Restart.rect )
        draw_text( Restart.text, 26,7, RESTART_FONT )

    def action():
        global score
        global feetuses
        global cooldown
        global show_hand
        
        score = 0
        for feetus in feetuses:
            space.remove(feetus.shape)
            space.remove(feetus.body)
            feetus.kill()
        for dog in doggos:
            space.remove(dog.body, dog.shape)
            dog.kill()

        cooldown = 0
        show_hand = True


class Wind():

    def __init__( self ):
        self.wind_thres = 250
        self.val = random.randint( -self.wind_thres+50, self.wind_thres )
        self.image = pygame.transform.scale( arrow_image, (160,80) )
        self.color = GREEN

    def change(self, color):
        if color == RED:
            self.color = RED
            return
        self.color = GREEN
        self.val = random.randint( -self.wind_thres+50, self.wind_thres )

    def draw(self):
        
        if self.val < 0:
            self.image = pygame.transform.flip( self.image, True, False )
            screen.blit( self.image, (screen_width//2+50, screen_height-340) )
            text = str(self.val)+'    Wind'
            draw_text(text,screen_width//2+90, screen_height-313,WIND_FONT, self.color)
            self.image = pygame.transform.flip( self.image, True, False )

        else:
            screen.blit( self.image, (screen_width//2+48, screen_height-335) )
            text = 'Wind    '+str(self.val)
            draw_text(text,screen_width//2+75, screen_height-311,WIND_FONT, self.color)


class FeetusBall( pygame.sprite.Sprite ):

    count = 0

    def __init__(self, x = screen_width//2, y = screen_height//2, rad = 22, color = RED, condition = True):

        pygame.sprite.Sprite.__init__( self )
        
        self.body = pymunk.Body()
        self.body.velocity = wind.val, -500
        self.body.position = x, y
        self.shape = pymunk.Circle( self.body, rad )
        self.shape.density = 1
        self.shape.elasticity = 0.5
        self.shape.friction = 1
        self.rad = rad
        space.add( self.body, self.shape )
        self.color = color
        image = feetus_image
        self.img_rad = 300
        self.image = pygame.transform.scale( image, [self.img_rad, self.img_rad] )
        self.rect = self.image.get_rect()
        self.shape.collision_type = 2*FeetusBall.count
        FeetusBall.count += 1

        self.counter = 0
        self.trashed = False
        self.floored = False


    def draw(self):
        x, y = map( int, self.body.position )
        screen.blit( self.image, (x-self.img_rad//2, y-self.img_rad//2) )
        # pygame.draw.circle( screen, self.color, ( x, y ), self.rad )

    def move( self ):
        global score
        
        x, y = self.body.velocity
        self.body.velocity = x, y-gravity
        posx,posy = map( int, self.body.position )

        
        self.counter += 1

        if not self.trashed:
            if in_trash( self, trash ):
                global score
                score += 1
                self.trashed = True
                message = Message( posx, posy, 'plus1' )
                messages.add( message )
            elif self.body.position[1] > trash.u:
                self.trashed = True
        
        if posx < -self.img_rad or posx > screen_width+self.img_rad:
            if self.floored == False:
                score -= 2
            space.remove( self.shape, self.body )
            self.kill()
            return

        if self.counter > 1:
            self.img_rad = max( 3*self.rad, self.img_rad-14 )
            self.image = pygame.transform.scale( feetus_image, (self.img_rad, self.img_rad) )
            self.counter = 0
        
    def stopX( self, arbiter, space, data ):
        global score

        x, y = self.body.velocity
        self.body.velocity = 0, 0
        pos_x, pos_y = map( int, self.body.position )

        self.floored = True

        score -= 2
        message = Message( pos_x, pos_y, 'minus2' )
        messages.add( message )
        
        return True
    
    def remove(self, arbiter, space, data):
        global score

        score += 4
        space.remove( self.shape, self.body )
        self.kill()
        x,y = map( int, self.body.position )
        message = Message( x, y, 'super' )
        messages.add( message )
        return False


class Dog(pygame.sprite.Sprite):

    count = 0

    def __init__(self, x = screen_width//2, y = screen_height//2, rad = 40, color = RED, condition = True):

        pygame.sprite.Sprite.__init__( self )

        self.body = pymunk.Body()
        self.body1 = pymunk.Body()
        self.body.velocity = wind.val, -500
        self.body.position = x, y
        self.rad = rad
        self.shape = pymunk.Circle( self.body, self.rad )
        self.shape.density = 1
        self.shape.elasticity = 0
        self.shape.friction = 1
        space.add( self.body, self.shape )
        self.color = color
        self.img_rad = 350
        self.original_images = []
        self.images = []
        for i in [1,2]:
            path = f'img/dog' + str(i) + '.png'
            img = pygame.image.load( path )
            img = pygame.transform.scale( img, (2*self.img_rad, 4*self.img_rad//3) )
            self.images.append( img )
            self.original_images.append( img )
        self.shape.collision_type = 5
        Dog.count += 1

        self.foot_step = 0
        self.thres = 3
        self.index = 0
        self.flipped = False
        self.counter = 0
        self.floored = False
        self.direction = 0
        self.time = 0

    def draw(self):
        
        self.time += 1
        x, y = map( int, self.body.position )

        if x+self.img_rad<0 or x-self.img_rad>screen_width:
            self.remove()
            return
        if self.time>100:
            self.remove()
        
        if self.foot_step>self.thres:
            self.index = (self.index+1)&1
            self.foot_step = 0

        if self.direction == -1 and self.flipped == False:
            self.flipped = True
            for i, img in enumerate(self.images):
                self.images[i] = pygame.transform.flip( img, True, False )
       
        screen.blit( self.images[self.index], (x-self.img_rad, y-self.img_rad+10) )
        self.foot_step += 1

        # pygame.draw.circle(screen, WHITE, (x,y), self.rad)

    def move(self):

        x, y = self.body.velocity
        self.body.velocity = x-60*self.direction, y-gravity

        self.counter += 1

        if self.counter > 1 and self.flipped == False:
            self.img_rad = max( 3*self.rad//2, self.img_rad-18 )
            for i, img in enumerate( self.original_images ):
                self.images[i] = pygame.transform.scale( img, (2*self.img_rad, 4*self.img_rad//3) ) 
            self.counter = 0

    def change_direction( self, arbiter, space, data ):

        x, y = map(int, self.body.position)

        self.floored = True
        self.direction = 2*( x<trash.l ) - 1

        return True

    def remove(self):
        
        space.remove(self.shape, self.body)
        self.kill()


class Wall():

    def __init__(self,x1,y1,x2,y2,width,color = BLUE, collisionType = 1):

        self.width=width
        self.body=pymunk.Body(body_type=pymunk.Body.STATIC)
        self.shape=pymunk.Segment(self.body,(x1,y1),(x2,y2),width)
        self.shape.elasticity=0.75
        self.shape.collision_type=collisionType
        self.shape.friction = 1
        space.add(self.body,self.shape)
        self.x1=x1
        self.x2=x2
        self.y1=y1
        self.y2=y2
        self.color=color

    def draw(self):

        pygame.draw.line(screen,self.color,(self.x1,self.y1),(self.x2,self.y2),self.width)


class TrashCan():

    def __init__( self, u, b, l, r, width = 10, color = RED ):

        self.width = width
        self.u = u
        self.b = b
        self.l = l
        self.r = r
        self.a = (l,u)
        self.b = (r,u)
        self.c = (r,b)
        self.d = (l,b)
        self.wb = Wall( l, b, r, b, 2*width, color)
        self.wl = Wall( l, u, l, b, width, color)
        self.wr = Wall( r, u, r, b, width, color)
        self.color = color

        self.image = trash_can_image
        self.image = pygame.transform.scale( self.image, [240,140] )


    def draw( self ):

        self.wl.draw()
        self.wb.draw()
        self.wr.draw()

    def display( self ):
        screen.blit( self.image, (self.l-20,self.u-30) )


class Message(pygame.sprite.Sprite):

    decode_happening = {
                'plus1': plus1_image,
                'super': super_image,
                'minus2': minus2_image
                }

    def __init__( self, x, y, happening ):

        pygame.sprite.Sprite.__init__(self)
        
        self.x = x
        self.y = y
        if happening == 'super':
            self.img_rad = 80
        else:
            self.img_rad = 40
        self.original_image = Message.decode_happening[happening]
        self.image = pygame.transform.scale( self.original_image, (self.img_rad,self.img_rad) )
        self.counter = 0

    def draw( self ):
        self.counter += 1
        screen.blit( self.image, (self.x-30, self.y-70) )

        if self.counter%2 == 0:
            self.y -= 2

        if self.counter > 35:
            self.kill()



floor = Wall( 0, floor_height, screen_width, floor_height, 50, BLUE, 3 )
wind = Wind()

feetuses = pygame.sprite.Group()
doggos = pygame.sprite.Group()
trash = TrashCan( screen_height-220, screen_height-130, screen_width//2+20, screen_width//2+260 )
handlers = []
messages = pygame.sprite.Group()


can_shoot = True
cooldown = 0
run=True
while run:
# ___________________________TIME VARIABLES________________________________
    clock.tick(fps)
    space.step(1/fps)
    cooldown -= 1
# ___________________________TIME VARIABLES END________________________________

# ___________________________CONDITION DEFINING VARIABLES________________________________
    if can_shoot == False:
        if cooldown <= 0:
            can_shoot = True
            wind.change(GREEN)
            show_hand = True

            if len(feetuses)>=2:
                if len(feetuses)<15:
                    prob = random.randint(1,7)
                    if prob==5:
                        dump_feetus = False
                else:
                    dump_feetus = False
    # pressed_keys = pygame.key.get_pressed()
    # if pressed_keys[K_SPACE] or len(feetuses)>5:
    #     dump_feetus = False
# ___________________________CONDITION DEFINING VARIABLES END________________________________
    
# ___________________________SCREEN VARIABLES________________________________
    draw_bg()
    wind.draw()
    # floor.draw()
    # pygame.draw.line( screen, GREEN, (0,throwing_height), (screen_width, throwing_height), 2 )
    score_text = f'Score: {score}'
    draw_text( score_text, screen_width//2-30, 10, SCORE_FONT )
    # feetuses.draw( screen )
    # feetuses.update()
    for feetus in feetuses:
        feetus.move()
        feetus.draw()
    for dog in doggos:
        dog.move()
        dog.draw()
    trash.display()
    for message in messages:
        message.draw()
    # trash.draw()
# ___________________________SCREEN VARIABLES END________________________________
 
# ___________________________SOME OTHER VARIABLES________________________________
    x, y = map(int, pygame.mouse.get_pos())
    if dump_feetus:
        img = feetus_image
        temp_width = 300
        img = pygame.transform.scale( img, [temp_width, temp_width] )
    else:
        img = dog1_image
        temp_width = 500
        img = pygame.transform.scale( img, [4*temp_width//3, temp_width] )
    if y > throwing_height:
        y = throwing_height
    if not Restart.rect.collidepoint( x, y ) and show_hand:
        screen.blit( img, [x-temp_width//2, y-temp_width//2] )
        display_hand( x, y )
# ___________________________SOME OTHER VARIABLES END________________________________

# ___________________________EVENT VARIABLES________________________________
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            run=False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:


            if can_shoot:
                cooldown = new_feetus_cooldown
                show_hand = False
                can_shoot = False
                
                if dump_feetus:
                    feetus = FeetusBall( x, y )
                    feetuses.add( feetus )

                    handler1 = space.add_collision_handler( feetus.shape.collision_type, 5 )
                    handler1.begin = feetus.remove
                    handler2 = space.add_collision_handler( feetus.shape.collision_type, 3 )
                    handler2.begin = feetus.stopX

                    handlers.append(handler1)
                    handlers.append(handler2)

                else:
                    dog = Dog(x, y)
                    doggos.add(dog)
                    dump_feetus = True

                    handler = space.add_collision_handler( 5, 3 )
                    handler.begin = dog.change_direction

                    handlers.append(handler)

                wind.change(RED)

            if Restart.rect.collidepoint( x,y ):
                Restart.action()
# ___________________________EVENT VARIABLES END________________________________

    pygame.display.update()

pygame.quit()