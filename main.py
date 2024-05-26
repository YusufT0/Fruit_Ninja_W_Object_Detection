import pygame
import sys
import random
import cv2
import mediapipe as mp

from pygame.sprite import *

draw = mp.solutions.drawing_utils
hands = mp.solutions.hands
hand = hands.Hands()
pygame.init()
ekran = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
kamera = cv2.VideoCapture(0)
pygame.display.set_caption("Game")
pillows = ["openai", "nvidia"]
game_paused = True
gravity = 1
velocity = 35
FPS = 30
left_x = 0
upper_y = 0
score = last_score = 0
sayac = 0
counter = 0
x_mouse_pos, y_mouse_pos = 0, 0
spawn_counter = 0
spawn_frequency = 60
toplar = []
left_pieces = []
right_pieces = []
TEXT_COL = (255,255,255)
font = pygame.font.SysFont("arialblack", 40)



class ParticlePrinciple(pygame.sprite.Sprite):
    def __init__(self):      
        self.particles = []
    def emit(self):
        if self.particles:
            self.delete_particles()
            for particle in self.particles:
                particle[0][1] += particle[2][0]
                particle[0][0] += particle[2][1]
                particle[1] -= 0.2
                pygame.draw.circle(ekran,pygame.Color('Orange'),particle[0], int(particle[1]))
    def add_particles(self, pos_x, pos_y):
        radius = 10
        direction_x = random.randint(-3,3)
        direction_y = random.randint(-3,3)
        particle_circle = [[pos_x,pos_y],radius,[direction_x,direction_y]]
        self.particles.append(particle_circle)
    def delete_particles(self):
        particle_copy = [particle for particle in self.particles if particle[1] > 0]
        self.particles = particle_copy



class Top(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(f"assets/{color}.png"), (128, 128))
        self.starting_left_x = 0
        self.starting_right_x = 0
        self.rotation_angle = 2
        self.color = color
        self.upper = 0
        self.starting_y = 0
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = velocity
        self.split = False
        self.split_frames = 20

    def update(self):
        if not self.split:
            self.rect.y -= self.velocity
            self.velocity -= gravity                
            if (self.rect.x < 400):
                self.rect.x-=1
            if (self.rect.x > 400):
                self.rect.x +=1
            if self.rect.y > 800:
                delete_ball(self)
        else:
            x, y = self.rect.center            
            left = Splitted_Left(x-20,y+10, self.velocity, self.color)
            right = Splitted_Right(x+20,y+10, self.velocity, self.color)
            left_pieces.append(left)
            right_pieces.append(right)
            delete_ball(top)
def spawn_top():
    for _ in range(random.randint(1, 4)):
        x_position = random.randint(100, 700)
        y_position = 800
        color = random.choice(pillows)
        toplar.append(Top(x_position, y_position, color))
def splitted(top):
    top.split = True

def delete_ball(top):
    toplar.remove(top)    

def draw_text(text,font, text_col, x, y):
    text_surface = font.render(text, True, text_col)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    ekran.blit(text_surface, text_rect)

class Splitted_Left(pygame.sprite.Sprite):
    def __init__(self, x,y,velocity, color):
        self.x =x
        self.y =y
        self.rotation_angle = 2
        self.velocity = velocity
        self.image = pygame.transform.scale(pygame.image.load(f"assets/{color}_left.png"),(64,128))
    def update(self):
        self.y -= self.velocity
        self.velocity -= gravity
        self.x-=2
        if self.y>800:
            left_pieces.remove(self)

class Splitted_Right():
    def __init__(self, x,y,velocity, color):
        self.x =x
        self.y =y
        self.image = pygame.transform.scale(pygame.image.load(f"assets/{color}_right.png"),(64,128))
        self.velocity = velocity
        self.rotation_angle = 2
    def update(self):
        self.y -= self.velocity
        self.velocity -= gravity
        self.x+=2
        if self.y>800:
            right_pieces.remove(self)

particle = ParticlePrinciple()
PARTICLE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(PARTICLE_EVENT, 40)

while True:
    ekran.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Boşluğa basıldığında oyunu başlat/durdur
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                last_score = score
                game_paused = not game_paused
        if event.type == PARTICLE_EVENT:
            if left_x != 0:
                particle.add_particles(left_x, upper_y)
    if game_paused:
        ekran.fill("#607274")
        draw_text("PRESS SPACE TO START",font, TEXT_COL, 400, 300)
        pygame.display.flip()
        
    if not game_paused:
        ret, frame = kamera.read()
        if not ret:
            continue
        frame = cv2.resize(frame, (800, 800))
        image_height, image_width, _ = frame.shape
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame2 = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame2 = cv2.flip(frame2, 0)
        UI = pygame.surfarray.make_surface(frame2)
        ekran.blit(UI, (0, 0))
        result = hand.process(frame)
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                right_x = int(hand_landmarks.landmark[hands.HandLandmark.INDEX_FINGER_MCP].x * image_width)
                left_x = int(hand_landmarks.landmark[hands.HandLandmark.INDEX_FINGER_TIP].x * image_width)
                upper_y = int(hand_landmarks.landmark[hands.HandLandmark.INDEX_FINGER_TIP].y * image_height)
                bottom_y = int(hand_landmarks.landmark[hands.HandLandmark.INDEX_FINGER_MCP].y * image_height)
                box_coordinate = (left_x, upper_y, right_x - left_x, bottom_y - upper_y)
                for top in toplar:
                    if top.rect.colliderect(pygame.Rect(box_coordinate)):
                        splitted(top)
                        score += 1
        if spawn_counter >= spawn_frequency:
            spawn_top()
            spawn_counter = 0
        
        for top in toplar[:]:
            top.update()
            top.rotation_angle += 2
            rotated = pygame.transform.rotate(top.image, top.rotation_angle)
            ekran.blit(rotated, top.rect)

        for left in left_pieces[:]:
            left.update()
            left.rotation_angle += 2
            rotated = pygame.transform.rotate(left.image, left.rotation_angle)
            ekran.blit(rotated, (left.x, left.y))

        for right in right_pieces[:]:
            right.update()
            right.rotation_angle -= 2
            rotated = pygame.transform.rotate(right.image, right.rotation_angle)
            ekran.blit(rotated, (right.x, right.y))    
        particle.emit()
        pygame.display.flip()
        clock.tick(FPS)
        spawn_counter += 1
