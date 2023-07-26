
import pygame
from os import listdir
from os.path import isfile,join
 
pygame.init()
 
WIDTH,HEIGHT=1500,800 #parameters for screen size(game window)
FPS=60 #frame per second
PLAYER_VEL=5 #velocity of player 
BG_COLOR=(255,255,255)


pygame.display.set_caption("space runner") 
WIN=pygame.display.set_mode((WIDTH,HEIGHT))
def flip(sprites): #fliping to sprite according to the direction of motion
    return [pygame.transform.flip(sprite,True,False) for sprite in sprites]

# creating sprite sheets and rendering them on screen

def create_spritesheet(dir1,dir2,width,height,direction=False):
    path=join('assets1',dir1,dir2)
    images=[f for f in listdir(path) if isfile(join(path,f))]
    
    all_sprite={}
    for image in images:
        sprite_sheets=pygame.image.load(join(path,image)).convert_alpha()
        sprites=[]
        for i in range(sprite_sheets.get_width()//width):
            surface=pygame.Surface((width,height),pygame.SRCALPHA,32)
            rect=pygame.Rect(i*width,0,width,height)
            surface.blit(sprite_sheets,(0,0),rect)
            sprites.append(pygame.transform.scale2x(surface))
        
        if direction:
            all_sprite[image.replace(".png","")+"_right"]=sprites
            all_sprite[image.replace(".png","")+"_left"]=flip(sprites)
        else:
            all_sprite[image.replace(".png","")]=sprites
    return all_sprite
# adding terrain blocks in the game window
def get_block(size):
    path=join("assets1","terrain","Terrain.png")
    image=pygame.image.load(path).convert_alpha()
    surface=pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect=pygame.Rect(96,0,size,size)
    surface.blit(image,(0,0),rect)
    return pygame.transform.scale2x(surface)

# it is a player class it handles everything related to player including the spreadsheet of player their motion, pixel perfect collision etc
class Player(pygame.sprite.Sprite):
    COLOR=(255,0,0)
    Gravity=2
    SPRITES=create_spritesheet("main character","mask dude",32,32,True)#calling create_spritesheet class to create player 
    ANIMATION_DELAY=2
    def __init__(self,x,y,width,height):
        super().__init__()
        self.rect=pygame.Rect(x,y,width,height)
        self.x_vel=0
        self.y_vel=0
        self.mask=None
        self.direction="left"
        self.animation_count=0
        self.fall_count=0
        self.count_jump=0
        self.hit=False
        self.hit_count=0
 
    def jump(self):
        self.y_vel=-self.Gravity*6
        self.animation_count=0
        self.count_jump+=1
        if self.count_jump==1:
            self.fall_count=0

    def move(self,dx,dy):
        self.rect.x +=dx
        self.rect.y +=dy

    def make_hit(self):
        self.hit=True
        self.hit_count=0

    def move_left(self,vel):
        self.x_vel=-vel
        if self.direction !="left":
            self.direction="left"
            self.animation_count=0
    def move_right(self,vel):
        self.x_vel=vel
        if self.direction !="right":
            self.direction="right"
            self.animation_count=0

    def loop(self,fps):
        self.y_vel +=min(1,(self.fall_count/fps)*self.Gravity)
        self.move(self.x_vel,self.y_vel)
        if self.hit:
            self.hit_count+=1
        if self.hit_count>fps:
            self.hit=False
            self.hit_count=0
        self.fall_count+=0.8 
        self.change_sprite()

    def landed(self):
        self.fall_count=0
        self.y_vel=0
        self.count_jump=0
    
    def hit_top(self):
        self.count=0
        self.y_vel *=-1


    def change_sprite(self):
        sprite_sheet="idle"
        if self.hit:
            sprite_sheet="hit"
        elif self.y_vel<0:
            if self.count_jump==1:
                sprite_sheet="jump"
            elif self.count_jump==2:
                sprite_sheet="double_jump"
        
        elif self.y_vel>self.Gravity:
            sprite_sheet="fall"
        
        elif self.x_vel!=0:
            sprite_sheet="run"
        sprite_sheetname=sprite_sheet+"_"+self.direction
        sprites=self.SPRITES[sprite_sheetname]
        sprite_index=(self.animation_count//self.ANIMATION_DELAY)%len(sprites)
        self.sprite=sprites[sprite_index]
        self.animation_count+=1
        self.update_change_sprite()

    def update_change_sprite(self):
        self.rect=self.sprite.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask= pygame.mask.from_surface(self.sprite)


    def draw(self,win,offset_x):

        win.blit(self.sprite,(self.rect.x-offset_x,self.rect.y))
# objects class it manages the display of all the objects on the game window
class Objects(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height,name=None):
        super().__init__()
        self.rect=pygame.Rect(x,y,width,height)
        self.image=pygame.Surface((width,height),pygame.SRCALPHA)
        self.width=width
        self.height=height
        self.name=name
    def draw(self,win,offset_x):
        win.blit(self.image,(self.rect.x-offset_x,self.rect.y))


class block(Objects):
    def __init__(self,x,y,size):
        super().__init__(x, y,size,size)
        block=get_block(size)
        self.image.blit(block,(0,0))
        self.mask=pygame.mask.from_surface(self.image)


class Fire(Objects):
    ANIMATION_DELAY=3

    def __init__(self,x,y,width,height):
        super().__init__(x,y,width,height,"fire")
        self.fire=create_spritesheet("trap","fire",width,height)
        self.image=self.fire["off"][0]
        self.mask=pygame.mask.from_surface(self.image)
        self.animation_count=0
        self.animation_name="off"
    def on(self):
        self.animation_name="on"
    def off(self):
        self.animation_name="off"

    def loop(self):
        sprites=self.fire[self.animation_name]
        sprite_index=(self.animation_count//self.ANIMATION_DELAY)%len(sprites)
        self.image=sprites[sprite_index]
        self.animation_count+=1

        self.rect=self.image.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask= pygame.mask.from_surface(self.image)

        if self.animation_count//self.ANIMATION_DELAY>len(sprites):
            self.animation_count=0

def make_background(name):
    image=pygame.image.load(join("assets1","background",name))
    _,_, width,height=image.get_rect()
    tiles=[]
    for i in range(WIDTH//width+1):
        for j in range(HEIGHT//height+1):
            position=[i*width,j*height]
            tiles.append(position)
    return tiles,image

def draw(WIN,background,bg_image,player,object,offset_x):
    for tile in background:
        WIN.blit(bg_image,tuple(tile))
    for obj in object:
        obj.draw(WIN,offset_x)

    player.draw(WIN,offset_x)
    pygame.display.update()

# it handle all the collision in y axis

def collision_inY(player,objects,dy):
    collided_objects=[]
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            if dy>0:
                player.rect.bottom=obj.rect.top
                player.landed()
            elif dy<0:
                player.rect.top=obj.rect.bottom
                player.hit_top()
            collided_objects.append(obj)
    return collided_objects

#it handles all the collision in x axis

def collision_inX(player,objects,dx):
    player.move(dx,0)
    player.update()
    collided_object=[]
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            collided_object=obj
            break
    player.move(-dx,0)
    player.update()
    return collided_object

def handle_move(player,objects):
    keys=pygame.key.get_pressed()
    player.x_vel=0
    collide_left=collision_inX(player,objects,-PLAYER_VEL*2)
    collide_right=collision_inX(player,objects,PLAYER_VEL*2)
    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys [pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)
    vertical_collide=collision_inY(player,objects,player.y_vel)
    to_check=[collide_left,collide_right,*vertical_collide]
    for obj in to_check:
        if obj and obj.name=="fire":
            player.make_hit()


def main():
    clock=pygame.time.Clock()
    backround,bg_image=make_background("Green.png")
    block_size=96
    fire=Fire(200,HEIGHT-block_size-64,16,32)
    fire.on()
    floor=[block(i*block_size,HEIGHT-block_size,block_size) 
           for i in range(-WIDTH//block_size,(WIDTH*2)//block_size)]
    Object=[*floor,block(0,HEIGHT-block_size*2,block_size),
            block(0,HEIGHT-block_size*3,block_size),
            block(WIDTH-block_size*6,HEIGHT-block_size*5,block_size),
            block(WIDTH-block_size*7,HEIGHT-block_size*5,block_size),
            block(WIDTH-block_size*8,HEIGHT-block_size*5,block_size),
            block(WIDTH-block_size*9,HEIGHT-block_size*5,block_size),
            block(WIDTH-block_size*10,HEIGHT-block_size*5,block_size),
            block(WIDTH-block_size*5,HEIGHT-block_size*6,block_size),
            block(WIDTH-block_size*4,HEIGHT-block_size*7,block_size),
            block(WIDTH-block_size*3,HEIGHT-block_size*8,block_size),
            block(WIDTH-block_size*14,HEIGHT-block_size*6,block_size),
  
            fire]

    player=Player(350,350,50,50)
    offset_x=0
    scroll_area_width=200
    run=True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                run= False
                break
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_SPACE and player.count_jump<2:
                    player.jump()
        player.loop(FPS)
        fire.loop()
        handle_move(player,Object)
        draw(WIN,backround,bg_image,player,Object,offset_x)

        if(player.rect.right-offset_x>=WIDTH-scroll_area_width and player.x_vel>0) or (player.rect.left-offset_x<=scroll_area_width and player.x_vel<0):
            offset_x+=player.x_vel
        
    pygame.quit()
    quit()


if __name__=="__main__":
    main()
