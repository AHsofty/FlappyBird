
x = 400
y = 140
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)


import pygame
import random
import math
import json

black    = (0,   0,   0)
white    = (255, 255, 255)
green    = (0, 255,   0)
red      = (255,   0,   0)
orange = (255,165,0)
blue = (0, 0, 128) 


pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 60)

points = 0
text = font.render(str(points), False, (0, 0, 0)) 

with open("settings.txt", "rb") as nea:
	dwight = json.load(nea)

WIDTH = dwight["screen"]["width"]
HEIGHT = dwight["screen"]["height"]
DELAY = dwight["screen"]["delay"]

difficulty = dwight["game"]["hard"]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bad bird")
bkg = pygame.image.load("background.png")
screen.fill(orange)
run = True
ongoing = True


# Pipe settings
try:
	pipe_speed = dwight["pipe"]["speed"]
except Exception:
	print("Looks like some things are missing in the settings file. Using in built settings")
	pipe_speed = 3.5

try:
	pipe_gap = dwight["pipe"]["gap"]
except Exception:
	print("Looks like some things are missing in the settings file. Using in built settings")
	pipe_gap = 150

try:
	pipe_width = dwight["pipe"]["width"]
except Exception:
	print("Looks like some things are missing in the settings file. Using in built settings")
	pipe_width = 50

try:
	pipe_start = dwight["pipe"]["start"]
except Exception:
	print("Looks like some things are missing in the settings file. Using in built settings")
	pipe_start = 610

pipe_yspeed = 1
pipe_end = -pipe_width - 10
fly = False

# bird settings
try:
	bird_height = dwight["bird"]["height"]
except Exception:
	print("Looks like some things are missing in the settings file. Using in built settings")
	bird_height = 40

try:
	bird_width = dwight["bird"]["height"]
except Exception:
	print("Looks like some things are missing in the settings file. Using in built settings")
	bird_width = 60

should_switch = True


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  
        self.image = pygame.image.load(image_file).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location
        self.rect.x = 0

BackGround = Background('background.png', [0,0])

sides = ["top", "bottom"]
class Pipe():
	def __init__(self, screen, side): 
		if side == "top":
			self.side = side			
			self.screen = screen
			self.image = pygame.image.load("down.png")
			self.top = self.image.get_rect()			

			self.top.x = pipe_start
			self.pos = random.randint(100, 700)
			self.top.y =  self.pos - 860
			self.top.width = pipe_width
			self.x = self.top.x
			self.y = self.top.y


		elif side == "bottom":
			self.side = "bottom"
			self.screen = screen
			self.image = pygame.image.load("up.png")
			self.bottom = self.image.get_rect()			
			self.bottom.width = pipe_width

			self.bottom.x = pipe_start
			self.bottom.y = pipe_top.pos + pipe_gap
			self.y = self.bottom.y
			self.x = self.bottom.x

	def reset_pipes(self):
		global points
		global textRect
		global difficulty
		global pipe_yspeed
		if self.x < pipe_end:
			if self.side == "top":
				self.top.x = pipe_start
				self.pos = random.randint(100, 700)
				self.top.y =  self.pos - 860
				self.x = self.top.x
				self.y = self.top.y
				points += 1
				text = font.render(str(points), False, (0, 0, 0)) 

				if difficulty:
					if pipe_yspeed < 0 and self.y > HEIGHT / 2:
						piee_yspeed *= -1
					elif pipe_yspeed > 0 and self.y < HEIGHT / 2:
						pipe_yspeed *= -1 
			else:
				self.bottom.x = pipe_start
				self.bottom.y = pipe_top.pos + pipe_gap
				self.y = self.bottom.y
				self.x = self.bottom.x
				points += 1
				text = font.render(str(points), False, (0, 0, 0)) 
			
			self.draw()					

	def move_pipes(self):
		global pipe_yspeed
		global should_switch
		if self.side == "top":
			self.top.x -= pipe_speed
			self.x = self.top.x

			if difficulty == True:
				self.top.y = self.top.y - pipe_yspeed
				self.y = self.top.y
	
				self.pos = self.top.y + 860
				if self.pos  < HEIGHT / 90:
					pipe_yspeed *= -1
					should_switch = False

		else:
			self.bottom.x -= pipe_speed
			self.x = self.bottom.x

			if difficulty == True:
				self.bottom.y -= pipe_yspeed
				self.y = self.bottom.y

				if self.y > 710 and should_switch == True:
					pipe_yspeed *= -1
				if self.y > 700:
					if pipe_yspeed < 0:
						pipe_yspeed *= -1
					should_switch = False
					
	
	def draw(self):
		if self.side == "top":
			screen.blit(self.image, self.top)
		if self.side == "bottom":
			screen.blit(self.image, self.bottom)



pipe_top = Pipe(screen, "top")
pipe_bottom = Pipe(screen, "bottom")
pipes = [pipe_top, pipe_bottom]



class Bird():
	def __init__(self, screen):
		self.image = pygame.image.load("bird.png")
		self.bird_fly = pygame.image.load("bird_fly.png")
		self.bird = self.image.get_rect()
		self.bird.x = 100
		self.bird.y = 300
		self.velocity = 0

	def draw_bird(self, screen):
		if fly == False:
			screen.blit(self.image, self.bird)
		else:
			screen.blit(self.bird_fly, self.bird)

	def move(self):
		global fly
		if self.velocity < 7:
			self.velocity += 1
		else:
			self.velocity += 0.1

		if self.velocity == 2:
			fly = False
		self.bird.y += self.velocity 


	def collision(self):
		"""
		We don't want the collision to be exact, otherwise it will look scuffed, That's why the -15 is there.
		Future note to myself: DONT BREAK IT YOU IDIOT

		The problem is that our bird is a "circle" and the image is a square. So the bird has a lot of white space around him, so it is possible for the pipes to collide with the white space, which looks stupid and is unfair.
		That's why we don't want the collision detection to be exact.
		"""
		if self.bird.x+bird_width-15 > pipe_top.x and self.bird.x+15 < pipe_top.x + pipe_width:
			if self.bird.y+15 < pipe_top.pos:
				game_over()

		if self.bird.x+bird_width-15 > pipe_bottom.x and self.bird.x+15 < pipe_bottom.x + pipe_width:
			if self.bird.y + bird_height > pipe_bottom.y+16:
				game_over()

	def reset_bird(self):
		self.bird.x = 100
		self.bird.y = 300
		self.velocity = 0


bird = Bird(screen)


def game_over():
	global ongoing
	ongoing = False

	global bird
	global pipe


def reset():
	global pipes

	for n in pipes:
		n.x = -100
		n.reset_pipes()


	bird.reset_bird()

	global ongoing
	ongoing = True



while run:
	pygame.time.delay(DELAY)
	if ongoing:
		screen.fill([255, 255, 255])
		if BackGround.rect.x - 600 <= -2560:
			BackGround.rect.x = 0
		else:
			BackGround.rect.x -= 1		
		screen.blit(BackGround.image, BackGround.rect)



		for n in pipes:
			n.move_pipes()
			n.reset_pipes()
			n.draw()

		bird.collision()
		bird.move()
		bird.draw_bird(screen)
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
			
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
				fly = True
				bird.velocity = -15

			if event.key == pygame.K_q:
				reset()

	pygame.display.update()

pygame.quit()
