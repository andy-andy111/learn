import os, sys, colorama, random

def disable_output():
    f=open('/dev/null', 'w')
    sys.stdout = f
    sys.std = f

def enable_output():
    sys.stdout = sys.__stdout__

class World(object):
    def __init__(self, w, h):
        self.w=w
        self.h=h
        self.screen=[[colorama.Fore.RESET+' ']*w for i in range(h)]
        self.objects=[]
        self.collidables=[]
        self.stage='running'

    def addObject(self, object):
        self.objects.append(object)

    def addColliable(self, c):
        self.collidables.append(c)
    
    def set(self,x,y,ch,color=colorama.Fore.RESET):
        for i in range(len(ch)):
            if x<0 or x+i>self.w-1: continue
            if y<0 or y>self.h-1: continue
            self.screen[y][x+i]=color+ch[i]

    def get(self,x,y):
        return self.screen[y][x]
    
    def clear(self):
        for i in range(self.h):
            for j in range(self.w):
                self.screen[i][j]=colorama.Fore.RESET+' '
    
    def getlines(self):
        result=''
        for i in range(self.h):
            result+=''.join(self.screen[i])+'\n'
        return result

    def show(self):
        os.system('clear')
        self.clear()
        for o in self.objects:
            o.draw(self)
        print(self.getlines())

    def run(self):
        if self.stage=='running':
            for o in self.objects:
                o.run()
            for c in self.collidables:
                c.process()
        
class Object(object):
    def __init__(self, collidable=False):
        self.collidable=collidable

    def run(self):
        pass

    def draw(self, screen):
        pass

class Collidable(object):
    def process(self):
        return False

class WallBulletsCollidable(object):
    def __init__(self, wall, bullets):
        self.wall=wall
        self.bullets=bullets
    
    def process(self):
        collided=False
        deleted=[False]*len(self.bullets.bullets)
        for i in range(len(self.bullets.bullets)):
            b=self.bullets.bullets[i]
            if b.x<1 or b.x>self.wall.w-2 or b.y<1 or b.y>self.wall.h-2:
                deleted[i] = True
                collided = True
        if collided:
            self.bullets.bullets=[self.bullets.bullets[i] for i in range(len(self.bullets.bullets)) if not deleted[i]]
        return collided

class WallOpponentsCollidable(object):
    def __init__(self, wall, opponents):
        self.wall=wall
        self.opponents=opponents
    
    def process(self):
        collided=False
        deleted=[False]*len(self.opponents.opponents)
        for i in range(len(self.opponents.opponents)):
            b=self.opponents.opponents[i]
            if b.x<1 or b.x>self.wall.w-2 or b.y<1 or b.y>self.wall.h-2:
                deleted[i] = True
                collided = True
        if collided:
            self.opponents.opponents=[self.opponents.opponents[i] for i in range(len(self.opponents.opponents)) if not deleted[i]]
        return collided
    
class PlayerOpponentsCollidable(object):
    def __init__(self, player, opponents, world):
        self.opponents=opponents
        self.player=player
        self.world=world
    
    def process(self):
        collided= False
        for i in range(len(self.opponents.opponents)):
            o=self.opponents.opponents[i]
            p=self.player
            if (o.x == p.x and o.y == p.y) or\
                (o.x>=p.prev_x and o.x<=p.x and o.y==p.y and o.y==p.prev_y):
                collided = True
                self.world.stage='lose'
                self.world.addObject(Title(self.world.w//2, self.world.h//2, 'You Lost!😭'))
                break
        return collided
    
class BulletsOpponentsCollidable(object):
    def __init__(self, bullets, opponents):
        self.opponents=opponents
        self.bullets=bullets

    def collide(self, b, o):
        return b.y==o.y and b.x>=o.x # and o.x<b.x+b.length
    
    def collideAnyBullet(self, o):
        for bi in range(len(self.bullets.bullets)):
            if self.collide(self.bullets.bullets[bi],o): return bi
        return -1
    
    def process(self):
        collided=False
        deletedO=[False]*len(self.opponents.opponents)
        deletedB=[False]*len(self.bullets.bullets)
        for i in range(len(self.opponents.opponents)):
            o=self.opponents.opponents[i]
            bi=self.collideAnyBullet(o)
            if bi>=0:
                deletedO[i] = True
                deletedB[bi] = True
                collided = True
        if collided:
            self.opponents.opponents=[self.opponents.opponents[i] for i in range(len(self.opponents.opponents)) if not deletedO[i]]
            self.bullets.bullets=[self.bullets.bullets[i] for i in range(len(self.bullets.bullets)) if not deletedB[i]]
        return collided

class WallPlayerCollidable(object):
    def __init__(self, wall, player):
        self.wall=wall
        self.player=player
    
    def process(self):
        collided=False
        if self.player.x<1:
            self.player.x=1
            collided = True
        if self.player.x>self.wall.w-2:
            self.player.x=self.wall.w-2
            collided = True
        if self.player.y<1:
            self.player.y=1
            collided = True
        if self.player.y>self.wall.h-2:
            self.player.y=self.wall.h-2
            collided = True

        return collided

class Wall(Object):
    def __init__(self, w, h):
        self.w=w
        self.h=h
        self.color=colorama.Fore.GREEN

    def draw(self, screen):
        for i in range(self.w):
            screen.set(i, 0, '!', self.color)
            screen.set(i, self.h-1, "!", self.color)
        for j in range(self.h):
            screen.set(0, j, "!", self.color)
            screen.set(self.w-1, j, "!", self.color)
        
class Player(Object):
    def __init__(self, x, y):
        self.x=x
        self.y=y
        self.prev_x=x
        self.prev_y=y
        self.color=colorama.Fore.BLUE

    def draw(self, screen):
        screen.set(self.x, self.y, 'o', self.color)

    def copy_prev(self):
        self.prev_x=self.x
        self.prev_y=self.y

    def move_up(self):
        self.copy_prev()
        self.y-=1

    def move_down(self):
        self.copy_prev()
        self.y+=1

    def move_left(self):
        self.copy_prev()
        self.x-=1

    def move_right(self):
        self.copy_prev()
        self.x+=1
        
class Bullet(Object):
    def __init__(self, x, y, speed, length):
        self.x=x
        self.y=y
        self.speed=speed
        self.length=length
        self.color=colorama.Fore.CYAN

    def draw(self, screen):
        screen.set(self.x, self.y, '-'*self.length, self.color)
            
    def run(self):
        self.x+=self.speed

class Bullets(Object):
    def __init__(self, speed, length=None):
        self.speed=speed
        if length is None: self.length=speed
        else: self.length=length
        self.bullets=[]

    def draw(self, screen):
        for b in self.bullets:
            b.draw(screen)

    def shoot(self, x, y):
        self.bullets.append(Bullet(x+1,y,self.speed,self.length))
    
    def run(self):
        for b in self.bullets:
            b.run()

class Opponents(Object):
    def __init__(self, speed, w, h):
        self.step=0
        self.speed=speed
        self.opponents = []
        self.w=w
        self.h=h
        
    def draw(self, screen):
        for o in self.opponents:
            o.draw(screen)
    
    def enter(self, x, y):
        self.opponents.append(Opponent(x, y, self.speed))

    def run(self):
        for o in self.opponents:
            o.run()
        if self.step>=10 and len(self.opponents)<20:
            self.enter(self.w-2, random.randint(1, self.h-2))
            self.step=0
        self.step += 1

class Opponent(Object):
    def __init__(self, x, y, speed):
        shapes=['△', '□', 'X', "😭", "😡", "👿", "🔥"]
        self.shape=shapes[random.randint(0,len(shapes)-1)]
        self.x=x
        self.y=y
        self.speed=speed

    def draw(self, screen):
        screen.set(self.x , self.y, self.shape)
            
    def run(self):
        self.x -=self.speed

class Title(Object):
    def __init__(self, x, y, text):
        self.x=x
        self.y=y
        self.text=text
    
    def draw(self,screen):
        screen.set(self.x, self.y, self.text)