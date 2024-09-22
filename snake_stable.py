import pygame
import random
import pymongo

# Initialize Pygame
pygame.init()

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["snake_game"]
scores_collection = db["scores"]

# Define colors
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)
purple = (128, 0, 128)

# Display settings
dis_width = 800
dis_height = 600
dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption('Snake Game')

clock = pygame.time.Clock()
snake_block = 10
snake_speed = 15

font_style = pygame.font.SysFont(None, 50)
score_font = pygame.font.SysFont(None, 35)

# Load background music
# pygame.mixer.music.load('background.mp3')
# pygame.mixer.music.play(-1)  # Play the music in a loop

# Initialize joystick
pygame.joystick.init()
joystick_count = pygame.joystick.get_count()
if joystick_count > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()


def our_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(dis, black, [x[0], x[1], snake_block, snake_block])


def message(msg, color, y_displace=0):
    msg = font_style.render(msg, True, color)
    dis.blit(msg, [dis_width / 6, dis_height / 3 + y_displace])


def save_score(username, score):
    scores_collection.insert_one({"username": username, "score": score})


def get_high_score():
    high_score = scores_collection.find_one(sort=[("score", pymongo.DESCENDING)])
    return high_score["score"] if high_score else 0


def show_score(score, high_score):
    value = score_font.render("Your Score: " + str(score), True, yellow)
    high_score_value = score_font.render("High Score: " + str(high_score), True, yellow)
    dis.blit(value, [0, 0])
    dis.blit(high_score_value, [dis_width - 200, 0])


def show_special_food_timer(timer):
    timer_value = score_font.render("Special Food Timer: " + str(timer), True, red)
    dis.blit(timer_value, [dis_width / 2 - 100, 0])


def landing_page():
    username = ""
    input_active = False
    landing = True
    while landing:
        dis.fill(blue)
        message("Enter Username: " + username, white, -50)
        message("Press Enter to Start or Q to Quit", white, 50)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                if event.key == pygame.K_RETURN:
                    if username:
                        landing = False
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode
    return username


def pause_game():
    paused = True
    while paused:
        message("Game Paused. Press P to Resume", white)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False


def gameloop(username):
    game_over = False
    game_close = False

    x1 = dis_width / 2
    y1 = dis_height / 2

    x1_change = 0
    y1_change = 0

    snake_list = []
    length_of_snake = 1

    foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0

    special_foodx = None
    special_foody = None
    special_food_timer = 0

    high_score = get_high_score()
    food_count = 0

    while not game_over:

        while game_close:
            dis.fill(blue)
            message("You lost! Press Q-Quit or C-Play Again", red)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameloop(username)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0
                elif event.key == pygame.K_p:
                    pause_game()

            if event.type == pygame.JOYAXISMOTION:
                if event.axis == 0:  # Left stick horizontal
                    if event.value < -0.5:
                        x1_change = -snake_block
                        y1_change = 0
                    elif event.value > 0.5:
                        x1_change = snake_block
                        y1_change = 0
                if event.axis == 1:  # Left stick vertical
                    if event.value < -0.5:
                        y1_change = -snake_block
                        x1_change = 0
                    elif event.value > 0.5:
                        y1_change = snake_block
                        x1_change = 0

        if x1 >= dis_width or x1 < 0 or y1 >= dis_height or y1 < 0:
            game_close = True
        x1 += x1_change
        y1 += y1_change
        dis.fill(blue)
        pygame.draw.rect(dis, green, [foodx, foody, snake_block, snake_block])

        if special_foodx is not None and special_foody is not None:
            pygame.draw.rect(dis, purple, [special_foodx, special_foody, snake_block, snake_block])
            show_special_food_timer(special_food_timer // snake_speed)
            special_food_timer -= 1
            if special_food_timer <= 0:
                special_foodx = None
                special_foody = None

        snake_head = [x1, y1]
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        for x in snake_list[:-1]:
            if x == snake_head:
                game_close = True

        our_snake(snake_block, snake_list)
        show_score(length_of_snake - 1, high_score)
        pygame.display.update()

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
            length_of_snake += 1
            food_count += 1

            if food_count % 10 == 0:
                special_foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
                special_foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
                special_food_timer = 6 * snake_speed  # 6 seconds

        if x1 == special_foodx and y1 == special_foody:
            special_foodx = None
            special_foody = None
            length_of_snake += 5

        clock.tick(snake_speed)

    save_score(username, length_of_snake - 1)
    pygame.quit()

username = landing_page()
gameloop(username)
