import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 493
screen_height = 737

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# Define font
font = pygame.font.SysFont('Arial', 60)

# Define colours
white = (255, 255, 255)  

# Define game variables
ground_scroll = 0
scroll_speed =15 # This is the speed at which the ground moves
flying = False
game_over = False
pipe_gap = 250
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

# Load images
bg = pygame.image.load('bg.png')
ground_img = pygame.image.load('ground.png')
button_img = pygame.image.load('restart.png')
message_img = pygame.image.load('message1.png')


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col) # This is the text that will be displayed
    screen.blit(img, (x, y))

def draw_message():
    # Scale the message image to fit the screen dimensions
    scaled_message = pygame.transform.scale(message_img, (screen_width, screen_height))
    screen.blit(scaled_message, (0, 0))


def reset_game():
    pipe_group.empty()  #this is for the pipes
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0                         #for animation 

        for num in range(1, 4):
            img = pygame.image.load(f'bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]     #this is for the bird's position
        self.vel = 0
        self.clicked = False

    def update(self):
        if flying:
            # Gravity
            self.vel += 0.5
            if self.vel > 8:         #for the bird to not go too fast
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if not game_over:
            # Jump
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:         #for the bird to not jump while already jumping
                self.clicked = False

            # Handle the animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0                    #For wing animation
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # Rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)              #for the pipe 
        self.image = pygame.image.load('pipe.png')
        self.rect = self.image.get_rect()
        # Position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:      #for the pipe to disappear when it goes off the screen
            self.kill()


class Button():
    def __init__(self, x, y, image):
        self.image = image         # for the button
        self.rect = self.image.get_rect() 
        self.rect.topleft = (x, y)

    def draw(self):
        action = False

        # Get mouse position
        pos = pygame.mouse.get_pos() 

        # Check if mouse is over the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        # Draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))   # Draw the button on the screen

        return action


bird_group = pygame.sprite.Group() 
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))    # create a bird object
bird_group.add(flappy)

# Create get ready button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 50, button_img)

run = True
while run:

    clock.tick(fps)

    # Draw background
    screen.blit(bg, (0, 0))  # Draw the background on the screen

    # Draw bird and pipes
    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)

    # Draw the ground
    screen.blit(ground_img, (ground_scroll, 768)) 

    # Check the score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                and not pass_pipe: # Check if the bird is inside the pipe
            pass_pipe = True
        if pass_pipe:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    draw_text(str(score), font, white, int(screen_width / 2), 20) # for score display

    # Look for collision
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:  # for collision detection
        game_over = True

    # Check if bird has hit the ground
    if flappy.rect.bottom >= 768:
        game_over = True
        flying = False

    if not game_over and flying:
        # Generate new pipes
        time_now = pygame.time.get_ticks()                  
        if time_now - last_pipe > pipe_frequency:          # for pipe generation
            pipe_height = random.randint(-100, 100)     # random height for the pipe
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)  # create a bottom pipe
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1) # for top pipe
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        # Draw and scroll the ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        pipe_group.update()

    # Check for game over and reset
    if game_over:
        if button.draw():
            game_over = False
            score = reset_game()

    # Display the message when the game is over or before flying
    if game_over or not flying:
        draw_message()

    for event in pygame.event.get():    # for closing the window
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over: # for starting the game
            flying = True

    pygame.display.update()

pygame.quit()
 