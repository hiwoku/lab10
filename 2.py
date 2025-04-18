import pygame
import psycopg2
import random
from config import params

def create_tables():
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_score (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    score INTEGER,
                    level INTEGER
                )
            """)
        conn.commit()

def get_or_create_user():
    username = input("Введите имя игрока: ")
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            row = cur.fetchone()
            if row:
                user_id = row[0]
                cur.execute("SELECT MAX(score), MAX(level) FROM user_score WHERE user_id = %s", (user_id,))
                result = cur.fetchone()
                max_score = result[0] or 0
                level = result[1] or 1
                print(f"Добро пожаловать, {username}. Уровень: {level}, лучший счёт: {max_score}")
                return user_id, level
            else:
                cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING id", (username,))
                user_id = cur.fetchone()[0]
                conn.commit()
                print(f"Создан новый пользователь: {username}")
                return user_id, 1

def save_score(user_id, score, level):
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO user_score (user_id, score, level) VALUES (%s, %s, %s)", (user_id, score, level))
        conn.commit()
    print(" Счёт сохранён!")


def snake_game(user_id, level):
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Змейка ")
    clock = pygame.time.Clock()

    snake = [[200, 200]]
    dx, dy = 20, 0
    food = [random.randrange(0, 400, 20), random.randrange(0, 400, 20)]
    score = 0
    speed = 10 + level * 2
    paused = False
    running = True

    font = pygame.font.SysFont("Arial", 24)

    while running:
        screen.fill((0, 0, 0))
        for s in snake:
            pygame.draw.rect(screen, (0, 255, 0), (*s, 20, 20))
        pygame.draw.rect(screen, (255, 0, 0), (*food, 20, 20))

        score_text = font.render(f"Счёт: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                save_score(user_id, score, level)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and dy == 0:
                    dx, dy = 0, -20
                elif event.key == pygame.K_DOWN and dy == 0:
                    dx, dy = 0, 20
                elif event.key == pygame.K_LEFT and dx == 0:
                    dx, dy = -20, 0
                elif event.key == pygame.K_RIGHT and dx == 0:
                    dx, dy = 20, 0
                elif event.key == pygame.K_p:
                    paused = not paused
                    if paused:
                        print("⏸ Игра приостановлена")
                        save_score(user_id, score, level)
                    else:
                        print("▶ Продолжение игры")

        if not paused:
            new_head = [snake[0][0] + dx, snake[0][1] + dy]

            
            if (
                new_head in snake or
                new_head[0] < 0 or new_head[0] >= 400 or
                new_head[1] < 0 or new_head[1] >= 400
            ):
                print("Игра окончена!")
                save_score(user_id, score, level)
                running = False
                continue

            snake.insert(0, new_head)
            if new_head == food:
                score += 10
                food = [random.randrange(0, 400, 20), random.randrange(0, 400, 20)]
            else:
                snake.pop()

        clock.tick(speed)

    pygame.quit()

if __name__ == "__main__":
    create_tables()
    user_id, level = get_or_create_user()
    snake_game(user_id, level)
