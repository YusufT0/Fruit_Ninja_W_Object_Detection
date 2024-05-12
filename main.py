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
game_paused = True
gravity = 1
velocity = 35
FPS = 30
score = last_score = 0
sayac = 0
counter = 0
x_mouse_pos, y_mouse_pos = 0, 0
spawn_counter = 0
spawn_frequency = 25
toplar = []
left_pieces = []
right_pieces = []
TEXT_COL = (255,255,255)
font = pygame.font.SysFont("arialblack", 40)
class Top(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("assets/ball.png"), (64, 64))
        self.starting_left_x = 0
        self.starting_right_x = 0
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
            left = Splitted_Left(x-20,y+10, self.velocity)
            right = Splitted_Right(x+20,y+10, self.velocity)
            left_pieces.append(left)
            right_pieces.append(right)
            delete_ball(top)
def spawn_top():
    for _ in range(random.randint(1, 4)):
        x_position = random.randint(100, 700)
        y_position = 800
        toplar.append(Top(x_position, y_position))
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
    def __init__(self, x,y,velocity):
        self.x =x
        self.y =y
        self.rotation_angle = 2
        self.velocity = velocity
        self.image = pygame.image.load("assets/left.png")
    def update(self):
        self.y -= self.velocity
        self.velocity -= gravity
        self.x-=2
        if self.y>800:
            left_pieces.remove(self)

class Splitted_Right():
    def __init__(self, x,y,velocity):
        self.x =x
        self.y =y
        self.image = pygame.image.load("assets/right.png")
        self.velocity = velocity
        self.rotation_angle = 2
    def update(self):
        self.y -= self.velocity
        self.velocity -= gravity
        self.x+=2
        if self.y>800:
            right_pieces.remove(self)


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

    if game_paused:
        ekran.fill("#607274")
        draw_text("PRESS SPACE TO START",font, TEXT_COL, 400, 300)
        draw_text(f"Score: {last_score}", font, TEXT_COL, 400, 400)
        pygame.display.flip()
        
    if not game_paused:
        sayac+=1
        if sayac == 30:
            counter+=1
            sayac = 0
            print(counter)

        if counter == 10:
            last_score = score
            game_paused = True
            score = 0
            counter = 0
        
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
                right_x = int(hand_landmarks.landmark[hands.HandLandmark.PINKY_TIP].x * image_width)
                left_x = int(hand_landmarks.landmark[hands.HandLandmark.THUMB_TIP].x * image_width)
                upper_y = int(hand_landmarks.landmark[hands.HandLandmark.MIDDLE_FINGER_TIP].y * image_height)
                bottom_y = int(hand_landmarks.landmark[hands.HandLandmark.WRIST].y * image_height)
                box_coordinate = (left_x, upper_y, right_x - left_x, bottom_y - upper_y)
                pygame.draw.rect(ekran, (0, 0, 255), box_coordinate, 2)
                for top in toplar:
                    if top.rect.colliderect(pygame.Rect(box_coordinate)):
                        splitted(top)
                        score += 1
                        print(f"Score: {score}")
        
        draw_text(f"Score: {score}", font, TEXT_COL, 100,20)
        if spawn_counter >= spawn_frequency:
            spawn_top()
            spawn_counter = 0
        
        for top in toplar[:]:
            top.update()
            ekran.blit(top.image, top.rect)

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

        draw_text(f"{counter}", font, TEXT_COL, 400,700)
        pygame.display.flip()
        clock.tick(FPS)
        spawn_counter += 1
