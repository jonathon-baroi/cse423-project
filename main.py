from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from gameObjectDefinitions import defineGameObjects
from datetime import datetime
import copy
import math


windowWidth = 1280
windowHeight = 720

maxX = 1280
maxY = 720

class Engine:
    _instance = None  

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:  
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        
        if not hasattr(self, "initialized"):
            self.gameObjects = []
            self.initialized = True  
            self.player = None
            self.keyboardInput = [0, 0, 0, 0]
            self.previous_time = datetime.now()
            self.delta_time_seconds = 0
            self.collisionPairs = []
            self.solidObjects = []
            self.switchDoorPairs = []
            self.lives = 3
            self.enemies = []
            self.playerStartPosition = [400, 400]
            self.ended = False
            print("==========")
            print("Game Started. Reach the End Point")
            print(f"Current Lives: {self.lives}")
            print("==========")
            
    def setPlayerStartPosition(self, x, y):
        self.playerStartPosition = [x, y]
    
    def destroyGameobject(self, gameObject):                
        for collisionPair in self.collisionPairs:
            collider1 = collisionPair.collider1
            collider2 = collisionPair.collider2
            if collider1.owner == gameObject or collider2.owner == gameObject:
                self.collisionPairs.remove(collisionPair)
        self.gameObjects.remove(gameObject)

    def touchEnemy(self):
        self.lives -= 1
        print("You Got Hit!")
        print(f"Remaining Lives: {self.lives}")
        print("==========")

        if self.lives == 0:
            self.ended = True
            print("You Died")

        self.player.x, self.player.y = self.playerStartPosition[0], self.playerStartPosition[1]
    
    def gameEnd(self):        
        print("You Won!")
        self.ended = True

    def checkEmpty(self, x, y):
        for solidObject in self.solidObjects:
            collider = solidObject.collider
                       
            if x >= collider.x - collider.w1 and \
            x <= collider.x + collider.w2 and \
            y >= collider.y - collider.h1 and \
            y <= collider.y + collider.h2:
                return False
        return True

    def createGameObject(self, x, y, drawParams, canCollide=False, solid=False, color=[1, 1, 1]):
        gameObject = GameObject(x, y, drawParams, canCollide, solid, color)
        self.gameObjects.append(gameObject)
        if solid:
            self.solidObjects.append(gameObject)
        return gameObject
    
    def createEnemy(self, x, y, drawParams, speed, direction):
        enemy = Enemy(x, y, drawParams, speed, direction)
        self.gameObjects.append(enemy)        
        self.enemies.append(enemy)
        return enemy
        
    
    def createPlayer(self, x, y, drawParams, speedTuning, canCollide=False):
        self.player = Player(x, y, drawParams, speedTuning, canCollide)        
        self.gameObjects += [self.player]
        return self.player

    def draw(self):
        for gameObject in self.gameObjects:
            glColor3f(20, 20, 20)
            gameObject.draw() 
            glColor3f(1, 1, 1)   

    def update(self):
        self.deltaTime()

        self.player.update()

        self.checkAllCollisions()        
        for gameObject in self.gameObjects:
            gameObject.collider.updatePosition()

        for enemy in self.enemies:
            enemy.move()

    def deltaTime(self):
        current_time = datetime.now()
        delta_time = current_time - self.previous_time
        self.delta_time_seconds = delta_time.total_seconds()
        self.previous_time = current_time
        return self.delta_time_seconds
    
    def addCollisionPair(self, gameObject1, gameObject2, onCollide=None):
        self.collisionPairs += [CollisionPair(gameObject1, gameObject2, onCollide)]
    
    def checkAllCollisions(self):        
        
        for collisionPair in self.collisionPairs:            
            collided = self.checkCollision(collisionPair)            
            if collided:
                if collisionPair.onCollide:
                    collisionPair.onCollide()

    def checkCollision(self, collisionPair, returnDirection=False):
        collider1 = collisionPair.collider1
        collider2 = collisionPair.collider2
        collided = (collider1.x - collider1.w1) < (collider2.x + collider2.w2) and \
        (collider1.x + collider1.w2) > (collider2.x - collider2.w1) and \
        (collider1.y - collider1.h1) < (collider2.y + collider2.h2) and \
        (collider1.y + collider1.h2) > (collider2.y - collider2.h1)
        left = collider1.x < collider2.x
        right = collider1.x > collider2.x
        up = collider1.y > collider2.y
        down = collider1.y < collider2.y
        return collided
    
class CollisionPair:
    def __init__(self, gameObject1, gameObject2, onCollide=None):
        self.collider1 = gameObject1.collider
        self.collider2 = gameObject2.collider        
        self.onCollide = onCollide


class GameObject:
    def __init__(self, x, y, drawParams, canCollide, solid, color=[1, 1, 1]):
        
        self.solid = solid
        self.x = x
        self.y = y
        self.color = color
        self.collider = None
        self.canCollide = canCollide
        self.drawPoints = []
        self.colliderSet = False  
        self.drawParams = drawParams
        xmin, xmax, ymin, ymax = find_bounds([self.x, self.y], *self.drawParams)
        
        if self.canCollide:
            self.createCollider(xmin, xmax, ymin, ymax)

    def createCollider(self, xmin, xmax, ymin, ymax):
        
        w1 = self.x - xmin  
        w2 = xmax - self.x  
        h1 = self.y - ymin  
        h2 = ymax - self.y  
        self.collider = Collider(self, w1, w2, h1, h2)

    def draw(self):
        draw_shape([self.x, self.y], *self.drawParams)  

class Enemy(GameObject):
    def __init__(self, x, y, drawParams, speed, direction, color=[1,1,1]):
        
        self.solid = False
        self.speed = speed
        self.color = color
        self.x = x
        self.y = y
        self.collider = None
        self.drawPoints = []
        self.colliderSet = False  
        self.drawParams = drawParams
        xmin, xmax, ymin, ymax = find_bounds([self.x, self.y], *self.drawParams)
        
        self.createCollider(xmin, xmax, ymin, ymax)
        self.direction = direction
    def move(self):
        if self.direction == "up-down":
            if self.speed > 0:
                y_check = self.y + self.collider.h2
            else:
                y_check = self.y - self.collider.h1
            if \
            Engine().checkEmpty(self.x, y_check + self.speed * Engine().delta_time_seconds) and \
            Engine().checkEmpty(self.x + self.collider.w2, y_check + self.speed * Engine().delta_time_seconds) and \
            Engine().checkEmpty(self.x - self.collider.w1, y_check + self.speed * Engine().delta_time_seconds):
                self.y += self.speed * Engine().delta_time_seconds
            else:
                self.speed *= -1
        elif self.direction == "left-right":
            if self.speed > 0:
                x_check = self.x + self.collider.w2
            else:
                x_check = self.x - self.collider.w1
            if \
            Engine().checkEmpty(x_check + self.speed * Engine().delta_time_seconds, self.y) and \
            Engine().checkEmpty(x_check + self.speed * Engine().delta_time_seconds, self.y + self.collider.h2) and \
            Engine().checkEmpty(x_check + self.speed * Engine().delta_time_seconds, self.y - self.collider.h1):
                self.x += self.speed * Engine().delta_time_seconds
            else:
                self.speed *= -1




class Player(GameObject):
    def __init__(self, x, y, drawParams, speedTuning, canCollide=False, color=[1,1,1]):
        
        self.x = x
        self.y = y
        self.color = color
        self.horVelocity = 0
        self.jumpVelocity = speedTuning[1]        
        self.walkSpeed = speedTuning[0]
        self.gravity = speedTuning[2]
        self.verVelocity = 0
        self.collider = None
        self.canCollide = canCollide
        self.drawPoints = []
        self.colliderSet = False  
        self.drawParams = drawParams
        xmin, xmax, ymin, ymax = find_bounds([self.x, self.y], *self.drawParams)
        self.grounded = False
        
        if self.canCollide:
            self.createCollider(xmin, xmax, ymin, ymax)

    def update(self):    
        left = Engine().keyboardInput[0]
        right = Engine().keyboardInput[1]
        up = Engine().keyboardInput[2]    

        

        self.move(left, right, up)

    def move(self, left, right, up):     

        x_check = self.x   
        if right:
            x_check = self.x + self.collider.w2
        elif left:
            x_check = self.x - self.collider.w1        
        self.horVelocity = (right - left) * self.walkSpeed

        if \
        Engine().checkEmpty(x_check + self.horVelocity * Engine().delta_time_seconds, self.y) and \
        Engine().checkEmpty(x_check + self.horVelocity * Engine().delta_time_seconds, self.y + self.collider.h2) and \
        Engine().checkEmpty(x_check + self.horVelocity * Engine().delta_time_seconds, self.y - self.collider.h1):
            self.x += self.horVelocity * Engine().delta_time_seconds
        
        

        if not self.grounded:
            self.verVelocity -= self.gravity * Engine().delta_time_seconds

            if self.verVelocity < 0:
                y_check = self.y - self.collider.h1
            else:
                y_check = self.y + self.collider.h2

            if \
            Engine().checkEmpty(self.x, y_check + self.verVelocity * Engine().delta_time_seconds) and \
            Engine().checkEmpty(self.x - self.collider.w1, y_check + self.verVelocity * Engine().delta_time_seconds) and \
            Engine().checkEmpty(self.x + self.collider.w2, y_check + self.verVelocity * Engine().delta_time_seconds):
                self.y += self.verVelocity * Engine().delta_time_seconds
            else:
                
                
                
                if self.verVelocity < 0:
                    self.grounded = True
                self.verVelocity = 0    
        else:
            if \
            Engine().checkEmpty(self.x, self.y - self.collider.h1 - 1) and \
            Engine().checkEmpty(self.x - self.collider.w1, self.y - self.collider.h1 - 1) and \
            Engine().checkEmpty(self.x + self.collider.w2, self.y - self.collider.h1 - 1):
                self.grounded = False
            if up:
                self.verVelocity = self.jumpVelocity
                self.grounded = False
                
        
        

class Collider:
    def __init__(self, owner, w1, w2, h1, h2):
        self.owner = owner
        
        self.x = owner.x
        self.y = owner.y
        self.w1 = w1  
        self.w2 = w2  
        self.h1 = h1  
        self.h2 = h2  

    def updatePosition(self):
        
        
        self.x = self.owner.x
        self.y = self.owner.y

def find_bounds(offset, *params):
    xmin = float('inf')  
    xmax = float('-inf')  
    ymin = float('inf')
    ymax = float('-inf')

    i = 0
    while i < len(params):
        if params[i] == "co":
            i += 2
            continue
        if params[i] == "l":  
            i += 1  
            while i < len(params) and not isinstance(params[i], str):
                x, y = params[i]  
                xmin = min(xmin, x)
                xmax = max(xmax, x)
                ymin = min(ymin, y)
                ymax = max(ymax, y)
                i += 1

        elif params[i] == "c":  
            i += 1  
            if i < len(params) and len(params[i]) == 3:
                x, y, r = params[i]  
                xmin = min(xmin, x - r)
                xmax = max(xmax, x + r)
                ymin = min(ymin, y - r)
                ymax = max(ymax, y + r)
                i += 1
            else:
                print("Error: Invalid circle parameters")
                break
    offx = offset[0]
    offy = offset[1]
    return xmin + offx, xmax + offx, ymin + offy, ymax + offy


def keyboardListener(key, x, y):
    if key==b'a':
        Engine().keyboardInput[0] = 1
    elif key==b'd':
        Engine().keyboardInput[1] = 1
    elif key==b'w':
        Engine().keyboardInput[2] = 1
    elif key==b's':
        Engine().keyboardInput[3] = 1        
    glutPostRedisplay()

def keyboardReleaseListener(key, x, y):
    if key==b'a':
        Engine().keyboardInput[0] = 0
    elif key==b'd':
        Engine().keyboardInput[1] = 0
    elif key==b'w':
        Engine().keyboardInput[2] = 0
    elif key==b's':
        Engine().keyboardInput[3] = 0   

def specialKeyListener(key, x, y):
    
    glutPostRedisplay()

def mouseListener(button, state, x, y):
    if state == GLUT_DOWN:
        pass
    glutPostRedisplay()


def draw_circle_points(cx, cy, x, y):
    glVertex2f(cx + x, cy + y)  
    glVertex2f(cx - x, cy + y)  
    glVertex2f(cx + x, cy - y)  
    glVertex2f(cx - x, cy - y)  
    glVertex2f(cx + y, cy + x)  
    glVertex2f(cx - y, cy + x)  
    glVertex2f(cx + y, cy - x)  
    glVertex2f(cx - y, cy - x)  

def mpc(cx, cy, r):
    x = 0
    y = r
    d = 1 - r     
    glBegin(GL_POINTS)

    draw_circle_points(cx, cy, x, y)  

    while x < y:
        x += 1
        if d < 0:
            d += 2 * x + 1 
        else:
            y -= 1
            d += 2 * (x - y) + 1  

        draw_circle_points(cx, cy, x, y)
    glEnd()  

def getZone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1

    if dx == 0:
        if dy > 0:
            return 2
        else:
            return 6
    elif dy == 0:
        if dx > 0:
            return 0
        else:
            return 4

    if abs(dx) > abs(dy):
        if dx > 0 and dy > 0:
            return 0
        elif dx < 0 and dy > 0:
            return 3
        elif dx < 0 and dy < 0:
            return 4
        elif dx > 0 and dy < 0:
            return 7
    elif abs(dy) > abs(dx):
        if dx > 0 and dy > 0:
            return 1
        elif dx < 0 and dy > 0:
            return 2
        elif dx < 0 and dy < 0:
            return 5
        elif dx > 0 and dy < 0:
            return 6
    else:
        if dx > 0 and dy > 0:
            return 1
        elif dx < 0 and dy > 0:
            return 3
        elif dx < 0 and dy < 0:
            return 5
        elif dx > 0 and dy < 0:
            return 7

def convertToZone0(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return y, -x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return -y, x
    elif zone == 7:
        return x, -y

def convertZone0toZone(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return -y, x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return y, -x
    elif zone == 7:
        return x, -y

def mpl(x1, y1, x2, y2):
    zone = getZone(x1, y1, x2, y2)
    if zone != 0:
        x1, y1 = convertToZone0(x1, y1, zone)
        x2, y2 = convertToZone0(x2, y2, zone)

    dy = y2 - y1
    dx = x2 - x1
    d = 2 * dy - dx
    dE = 2 * dy
    dNE = 2 * (dy - dx)
    x, y = x1, y1
    glBegin(GL_POINTS)
    draw_x, draw_y = convertZone0toZone(x, y, zone)
    glVertex2d(draw_x, draw_y)
    while x < x2:
        if (d <= 0):
            x += 1
            d += dE
        else:
            x += 1
            y += 1
            d += dNE
        draw_x, draw_y = convertZone0toZone(x, y, zone)
        glVertex2d(draw_x, draw_y)
    glEnd()

def draw_shape(offset, *params):
    offx = offset[0]
    offy = offset[1]     
    i = 0  
    
    while i < len(params):
        if params[i] == "l":  
            mode = "l"
            i += 1  
            continue
        elif params[i] == "co":
            mode = "co"
            i += 1
            continue
        elif params[i] == "c":  
            mode = "c"
            i += 1  
            continue

        if mode == "l":  
            while i < len(params) - 1 and not isinstance(params[i + 1], str):  
                x1, y1 = params[i]
                x2, y2 = params[i + 1]                
                mpl(x1 + offx, y1 + offy, x2 + offx, y2 + offy)  
                i += 1  
            i += 1  

        elif mode == "c":  
            if i < len(params) and len(params[i]) == 3:  
                x, y, r = [params[i][0] + offx, params[i][1] + offy, params[i][2]]                
                mpc(x, y, r)
                i += 1  
            else:
                print("Error: Invalid or incomplete circle parameters")
                break
        elif mode == "co":
            glColor3f(*params[i])
            i += 1
    glColor3f(1, 1, 1)

def draw():
    if not Engine().ended:
        Engine().draw()    
  

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    draw()
    glutSwapBuffers()

def animate():
    if not Engine().ended:
        Engine().update()
        glutPostRedisplay()

def init():
    glClearColor(0, 0, 0, 0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, maxX, 0, maxY)

defineGameObjects()
glutInit()
glutInitWindowSize(windowWidth, windowHeight)
glutInitWindowPosition(0, 0)
glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)

window = glutCreateWindow(b"CSE423 Project")
init()

glutDisplayFunc(display)
glutIdleFunc(animate)

glutKeyboardFunc(keyboardListener)
glutSpecialFunc(specialKeyListener)
glutMouseFunc(mouseListener)
glutKeyboardUpFunc(keyboardReleaseListener)

glutMainLoop()
