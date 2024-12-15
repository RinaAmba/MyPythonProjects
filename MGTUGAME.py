import pygame
import random
import sqlite3
import time

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Catch the Prizes!")
clock = pygame.time.Clock()

nickname = input("Введите свой никнейм: ")

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 255, 0))  
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        #Границы экрана
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

class Prize(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((0, 0, 255))  
        pygame.draw.polygon(self.image, (0,0,255), [(0,30), (15,0), (30,30)])
        self.rect = self.image.get_rect(center=(random.randint(50,SCREEN_WIDTH-50), random.randint(50,SCREEN_HEIGHT-50)))

class Bomb(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 0, 0)) 
        pygame.draw.circle(self.image, (255,0,0), (15,15), 15)
        self.rect = self.image.get_rect(center=(random.randint(50,SCREEN_WIDTH-50), random.randint(50,SCREEN_HEIGHT-50)))

class DatabaseHandler:
    def __init__(self, db_name="highscores.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS highscores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname TEXT,
                score INTEGER
            )
        ''')
        self.conn.commit()

    def insert_score(self, nickname, score):
        self.cursor.execute("INSERT INTO highscores (nickname, score) VALUES (?, ?)", (nickname, score))
        self.conn.commit()

    def get_highscores(self, limit=5):
        self.cursor.execute("SELECT nickname, score FROM highscores ORDER BY score DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

def show_intro_text():
    font = pygame.font.Font(None, 36)
    texts = [
        "Собирай синие призы, двигаясь стрелками,",
        "и продержись дольше остальных игроков.",
        "Остерегайся красных бомб, наткнувшись хоть на одну ты проиграешь.",
        "Нажми пробел для продолжения"
    ]
    y_offset = 100
    for text in texts:
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        screen.blit(text_surface, text_rect)
        y_offset += 50
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

show_intro_text()

player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
prizes = pygame.sprite.Group()
bombs = pygame.sprite.Group()
all_sprites = pygame.sprite.Group(player)

for _ in range(10): 
    prizes.add(Prize())
for _ in range(5): 
    bombs.add(Bomb())
all_sprites.add(prizes, bombs)

score = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.update(keys)

    #Проверка столкновений
    collided_prizes = pygame.sprite.spritecollide(player, prizes, True)
    collided_bombs = pygame.sprite.spritecollide(player, bombs, False)

    for prize in collided_prizes:
        score += 1

    if collided_prizes:  # Создаем новый приз только если были столкновения
        new_prize = Prize()
        prizes.add(new_prize)
        all_sprites.add(new_prize)

    if collided_bombs:
        running = False


    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Счет: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    pygame.display.flip()
    clock.tick(60)

# Запись результата в БД
db = DatabaseHandler()
db.insert_score(nickname, score)

# Вывод таблицы лидеров
highscores = db.get_highscores()

font = pygame.font.Font(None, 30) 

y_offset = 50 
text_color = (255, 255, 255) 


title_surface = font.render("ТОП-5 игроков:", True, text_color)
title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
screen.blit(title_surface, title_rect)
y_offset += 40 

# Отрисовка записей таблицы лидеров
for nickname, score in highscores:
    score_text = font.render(f"{nickname}: {score}", True, text_color)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
    screen.blit(score_text, score_rect)
    y_offset += 30 

pygame.display.flip() 

db.close()
pygame.time.delay(5000)
pygame.quit()

