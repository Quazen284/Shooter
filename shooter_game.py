from pygame import *
from random import randint
from time import time as timer

font.init()
font1 = font.Font(None, 80)
win = font1.render("YOU WIN!", True, (255, 255, 255))
lose = font1.render("YOU LOSE!", True, (180, 0, 0))
font2 = font.Font(None, 36)

#фоновая музыка
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')

#нам нужны такие картинки:
img_back = "galaxy.jpg" #фон игры
img_hero = "rocket.png" #герой
img_enemy = "ufo.png"
img_bullet = "bullet.png"
img_asteroid = "asteroid.png"
lost = 0
max_lost = 10
score = 0
goal = 100 
font.init()
font1 = font.Font(None, 36)
life = 3

#класс-родитель для других спрайтов
class GameSprite(sprite.Sprite):
 #конструктор класса
   def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
       #Вызываем конструктор класса (Sprite):
       sprite.Sprite.__init__(self)

       #каждый спрайт должен хранить свойство image - изображение
       self.image = transform.scale(image.load(player_image), (size_x, size_y))
       self.speed = player_speed

       #каждый спрайт должен хранить свойство rect - прямоугольник, в который он вписан
       self.rect = self.image.get_rect()
       self.rect.x = player_x
       self.rect.y = player_y
 #метод, отрисовывающий героя на окне
   def reset(self):
       window.blit(self.image, (self.rect.x, self.rect.y))

#класс главного игрока
class Player(GameSprite):
   #метод для управления спрайтом стрелками клавиатуры
    def update(self):
       keys = key.get_pressed()
       if keys[K_LEFT] and self.rect.x > 5:
           self.rect.x -= self.speed
       if keys[K_RIGHT] and self.rect.x < win_width - 80:
           self.rect.x += self.speed
 #метод "выстрел" (используем место игрока, чтобы создать там пулю)
    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)
    
class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost = lost + 1

class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:
            self.kill()
        
#Создаем окошко
win_width = 700
win_height = 500
display.set_caption("Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))

#создаем спрайты
ship = Player(img_hero, 5, win_height - 100, 80, 100, 20)
ufos = sprite.Group()
for i in range(1,6):
    ufo = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(2,5))
    ufos.add(ufo)
bullets = sprite.Group()
asteroids = sprite.Group()
for i in range(1,5):
    asteroid = Enemy(img_asteroid, randint(80, win_width - 80), -40, 80, 50, randint(2,5))
    asteroids.add(asteroid)

#переменная "игра закончилась": как только там True, в основном цикле перестают работать спрайты
finish = False
#Основной цикл игры:
run = True #флаг сбрасывается кнопкой закрытия окна

num_fire = 0

rel_time = False
while run:
   #событие нажатия на кнопку Закрыть
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                if num_fire < 5 and rel_time == False:
                    num_fire += 1
                    fire_sound.play()
                    ship.fire()
                if num_fire >= 5 and rel_time == False:
                    last_time = timer()
                    rel_time = True

    if not finish:
       #обновляем фон
        window.blit(background,(0,0))

       #производим движения спрайтов
        ship.update()
        ufos.update()
        bullets.update()
        asteroids.update()

       #обновляем их в новом местоположении при каждой итерации цикла
        ship.reset()
        ufos.draw(window)
        bullets.draw(window)
        asteroids.draw(window)

        if rel_time == True:
            now_time = timer()
            if now_time - last_time < 3:
                reload = font2.render("Wait, reload...", 1, (150, 0, 0))
                window.blit(reload, (260, 460))
            else: 
                num_fire = 0
                rel_time = False

        collides = sprite.groupcollide(ufos, bullets, True, True)
        for c in collides:
            score = score + 1
            ufo = Enemy(img_enemy, randint(80, win_width - 80), - 40, 80, 50, randint(2, 10))
            ufos.add(ufo)
        
        if sprite.spritecollide(ship, ufos, False) or sprite.spritecollide(ship, asteroids, False):
            sprite.spritecollide(ship, ufos, True)
            sprite.spritecollide(ship, asteroids, True)
            life -= 1
            if life == 0 or lost >= max_lost:
                finish = True
                window.blit(lose, (200, 200))
            
            if score >= goal:
                finish = True
                window.blit(win, (200, 200))


        text = font2.render("Счётчик: " + str(score), 1, (255, 255, 255))
        window.blit(text, (1, 15))
        text_lose = font2.render("Пропущенно: " + str(lost), 1, (255, 255, 255))
        window.blit(text_lose, (1,50))

        if life == 3:
            life_color = (0, 150, 0)
        if life == 2:
            life_color = (150, 150, 0)
        if life == 1:
            life_color = (150, 0, 0)
        text_life = font1.render(str(life), 1, life_color)
        window.blit(text_life, (650, 10))

        display.update()

    else:
        finish = False
        score = 0
        lost = 0
        num_fire = 0
        life = 3
        for b in bullets:
            b.kill()
        for u in ufos:
            u.kill()
        for a in asteroids:
            a.kill()
        
        time.delay(3000)

        for i in range(1,6):
            ufo = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(2,5))
            ufos.add(ufo)
        for i in range(1,5):
            asteroid = Enemy(img_asteroid, randint(80, win_width - 80), -40, 80, 50, randint(2,5))
            asteroids.add(asteroid)

   #цикл срабатывает каждые 0.05 секунд
    time.delay(50)