import pygame
import cv2
import numpy as np
import sys
import time
import os
import random

# Initialize Pygame and OpenCV
pygame.init()
pygame.display.set_caption("Snake Game with Camera Background and Icons")

# Original game dimensions (aspect ratio)
GAME_WIDTH, GAME_HEIGHT = 1200, 900  # You can change these values

# Initialize camera
cap = cv2.VideoCapture(0)  # Use 0 for the default camera

# Variables to manage screen modes
is_fullscreen = False

# Create the window in windowed mode initially
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))

# Game settings
clock = pygame.time.Clock()
speed = 5

# Colors
WHITE = (255, 255, 255)  # Default body color
RED = (255, 0, 0)        # For drawing food when no icons are available
YELLOW = (255, 255, 0)   # Snake 2 default body color
BLACK = (0, 0, 0)        # For background padding

# Adjustable block size for snake and food
BLOCK_SIZE = 60  # Adjust this value to change the size

# Load icon images from 'icons' sub-folder
def load_icons():
    icons_folder = 'icons'
    default_body_icon = None
    food_icons = []
    if not os.path.exists(icons_folder):
        os.makedirs(icons_folder)
        print(f"Created '{icons_folder}' folder. Please add icon images to this folder.")
    else:
        for filename in os.listdir(icons_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image_path = os.path.join(icons_folder, filename)
                try:
                    icon_image = pygame.image.load(image_path).convert_alpha()
                    icon_image = pygame.transform.scale(icon_image, (BLOCK_SIZE, BLOCK_SIZE))
                    if filename == 'default-body.png':
                        default_body_icon = icon_image
                    else:
                        food_icons.append(icon_image)
                except Exception as e:
                    print(f"Failed to load image '{filename}': {e}")
    if not default_body_icon:
        print(f"No 'default-body.png' found in '{icons_folder}' folder. Using default color for snake body.")
    if not food_icons:
        print(f"No food icons found in '{icons_folder}' folder. Using default red square for food.")
    return default_body_icon, food_icons

# Load icons at the start
DEFAULT_BODY_ICON, FOOD_ICONS = load_icons()

def toggle_fullscreen():
    global is_fullscreen, window
    is_fullscreen = not is_fullscreen
    if is_fullscreen:
        pygame.display.quit()
        pygame.display.init()
        infoObject = pygame.display.Info()
        SCREEN_WIDTH, SCREEN_HEIGHT = infoObject.current_w, infoObject.current_h
        window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    else:
        pygame.display.quit()
        pygame.display.init()
        window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    pygame.display.set_caption("Snake Game with Camera Background and Icons")

def main_menu():
    menu_font = pygame.font.SysFont('Arial', 50)
    info_font = pygame.font.SysFont('Arial', 30)
    run = True
    while run:
        # Create a game surface with the original game dimensions
        game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

        # Capture camera frame
        ret, frame = cap.read()
        if not ret:
            continue

        # Process camera frame
        frame_surface, _, _, _, _ = process_camera_frame(frame)

        # Display frame on the game surface
        game_surface.blit(frame_surface, (0, 0))

        # Render menu text
        title_text = menu_font.render("Snake Game", True, WHITE)
        single_text = menu_font.render("1. Single Player", True, WHITE)
        double_text = menu_font.render("2. Double Player", True, WHITE)
        instructions1 = info_font.render("Player 1: Arrow keys", True, WHITE)
        instructions2 = info_font.render("Player 2: W/A/S/D keys", True, WHITE)
        pause_text = info_font.render("Press SPACE to pause during game", True, WHITE)
        size_text = info_font.render(f"Current Block Size: {BLOCK_SIZE}", True, WHITE)
        fullscreen_text = info_font.render("Press 'f' to toggle Full Screen", True, WHITE)
        quit_text = info_font.render("Press 'q' to Quit", True, WHITE)

        # Blit text onto the game surface
        game_surface.blit(title_text, (GAME_WIDTH//2 - title_text.get_width()//2, GAME_HEIGHT//6))
        game_surface.blit(single_text, (GAME_WIDTH//2 - single_text.get_width()//2, GAME_HEIGHT//3))
        game_surface.blit(double_text, (GAME_WIDTH//2 - double_text.get_width()//2, GAME_HEIGHT//3 + 60))
        game_surface.blit(instructions1, (GAME_WIDTH//2 - instructions1.get_width()//2, GAME_HEIGHT//2 + 60))
        game_surface.blit(instructions2, (GAME_WIDTH//2 - instructions2.get_width()//2, GAME_HEIGHT//2 + 100))
        game_surface.blit(pause_text, (GAME_WIDTH//2 - pause_text.get_width()//2, GAME_HEIGHT//2 + 140))
        game_surface.blit(size_text, (GAME_WIDTH//2 - size_text.get_width()//2, GAME_HEIGHT//2 + 180))
        game_surface.blit(fullscreen_text, (GAME_WIDTH//2 - fullscreen_text.get_width()//2, GAME_HEIGHT//2 + 220))
        game_surface.blit(quit_text, (GAME_WIDTH//2 - quit_text.get_width()//2, GAME_HEIGHT//2 + 260))

        # Scale and center the game surface onto the window
        scale_and_center(game_surface)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                cv2.destroyAllWindows()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player1_face_small, player1_face_large = capture_player_face(1)
                    game_loop(single_player=True, snake1_head_image=player1_face_small)
                elif event.key == pygame.K_2:
                    player1_face_small, player1_face_large = capture_player_face(1)
                    player2_face_small, player2_face_large = capture_player_face(2)
                    game_loop(single_player=False,
                              snake1_head_image=player1_face_small,
                              snake2_head_image=player2_face_small,
                              player1_face_large=player1_face_large,
                              player2_face_large=player2_face_large)
                elif event.key == pygame.K_f:
                    toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    if is_fullscreen:
                        toggle_fullscreen()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    cap.release()
                    cv2.destroyAllWindows()
                    sys.exit()

def capture_player_face(player_number):
    font = pygame.font.SysFont('Arial', 40)
    capturing = True
    while capturing:
        # Create a game surface with the original game dimensions
        game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

        # Capture camera frame
        ret, frame = cap.read()
        if not ret:
            continue

        # Process camera frame
        frame_surface, x_offset, y_offset, scale_factor, resized_frame = process_camera_frame(frame)

        # Display frame on the game surface
        game_surface.blit(frame_surface, (0, 0))

        # Draw the square block in the center
        square_size = min(GAME_WIDTH, GAME_HEIGHT) // 3
        square_rect = pygame.Rect(
            (GAME_WIDTH - square_size) // 2,
            (GAME_HEIGHT - square_size) // 2,
            square_size,
            square_size
        )
        pygame.draw.rect(game_surface, RED, square_rect, 2)  # Draw the square border

        # Display instructions
        instruction_text = font.render(f"Player {player_number}, align your face", True, WHITE)
        instruction_text2 = font.render("inside the square and press Enter", True, WHITE)
        game_surface.blit(instruction_text, (GAME_WIDTH//2 - instruction_text.get_width()//2, 50))
        game_surface.blit(instruction_text2, (GAME_WIDTH//2 - instruction_text2.get_width()//2, 100))

        # Scale and center the game surface onto the window
        scale_and_center(game_surface)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                cv2.destroyAllWindows()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Calculate the coordinates of the square in the resized frame
                    x1 = square_rect.left - x_offset
                    y1 = square_rect.top - y_offset
                    x2 = square_rect.right - x_offset
                    y2 = square_rect.bottom - y_offset

                    # Ensure coordinates are within frame bounds
                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(resized_frame.shape[1], x2)
                    y2 = min(resized_frame.shape[0], y2)
                    if x2 <= x1 or y2 <= y1:
                        print("Invalid face capture area.")
                        continue

                    # Crop the image
                    face_image = resized_frame[y1:y2, x1:x2]

                    # Convert to Pygame surface
                    face_surface_large = pygame.image.frombuffer(face_image.tobytes(), face_image.shape[1::-1], "RGB")

                    # Resize to fit the snake head
                    face_surface_small = pygame.transform.scale(face_surface_large, (BLOCK_SIZE, BLOCK_SIZE))

                    return face_surface_small, face_surface_large  # Return both small and large face images
                elif event.key == pygame.K_f:
                    toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    if is_fullscreen:
                        toggle_fullscreen()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    cap.release()
                    cv2.destroyAllWindows()
                    sys.exit()

def game_over_screen(final_game_surface, winner_face_image=None):
    game_over_font = pygame.font.SysFont('Arial', 50)
    info_font = pygame.font.SysFont('Arial', 30)
    run = True
    while run:
        # Use the final game surface
        game_surface = final_game_surface.copy()

        # Dim the background by overlaying a semi-transparent black surface
        dim_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        dim_surface.set_alpha(150)  # Adjust alpha value for the desired dim effect (0-255)
        dim_surface.fill(BLACK)
        game_surface.blit(dim_surface, (0, 0))

        # Calculate positions
        top_offset = 50  # Starting y-coordinate for the first text/image
        spacing = 20     # Space between elements

        elements = []

        if winner_face_image is not None:
            # Display winner's face and label
            winner_label = game_over_font.render("Winner!", True, RED)
            # Resize winner's face image to fit in the screen if necessary
            face_width = winner_face_image.get_width()
            face_height = winner_face_image.get_height()
            max_face_width = GAME_WIDTH // 2
            max_face_height = GAME_HEIGHT // 3

            scale_factor = min(max_face_width / face_width, max_face_height / face_height, 1)
            new_width = int(face_width * scale_factor)
            new_height = int(face_height * scale_factor)

            winner_face_resized = pygame.transform.scale(winner_face_image, (new_width, new_height))

            # Add elements to the list with their calculated positions
            elements.append((winner_face_resized, (GAME_WIDTH//2 - new_width//2, top_offset)))
            top_offset += new_height + spacing
            elements.append((winner_label, (GAME_WIDTH//2 - winner_label.get_width()//2, top_offset)))
            top_offset += winner_label.get_height() + spacing
        else:
            # It's a draw or single-player game over
            over_text = game_over_font.render("Game Over!", True, RED)
            elements.append((over_text, (GAME_WIDTH//2 - over_text.get_width()//2, top_offset)))
            top_offset += over_text.get_height() + spacing

        # Other texts
        continue_text = game_over_font.render("Press any key to continue", True, WHITE)
        elements.append((continue_text, (GAME_WIDTH//2 - continue_text.get_width()//2, top_offset)))
        top_offset += continue_text.get_height() + spacing

        fullscreen_text = info_font.render("Press 'f' to toggle Full Screen", True, WHITE)
        elements.append((fullscreen_text, (GAME_WIDTH//2 - fullscreen_text.get_width()//2, top_offset)))
        top_offset += fullscreen_text.get_height() + spacing

        quit_text = info_font.render("Press 'q' to Quit", True, WHITE)
        elements.append((quit_text, (GAME_WIDTH//2 - quit_text.get_width()//2, top_offset)))

        # Blit all elements onto the game surface
        for element, position in elements:
            game_surface.blit(element, position)

        # Scale and center the game surface onto the window
        scale_and_center(game_surface)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                cv2.destroyAllWindows()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    if is_fullscreen:
                        toggle_fullscreen()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    cap.release()
                    cv2.destroyAllWindows()
                    sys.exit()
                else:
                    run = False

def game_loop(single_player=True, snake1_head_image=None, snake2_head_image=None, player1_face_large=None, player2_face_large=None):
    # Initialize snake(s)
    snake1_pos = [BLOCK_SIZE * 5, BLOCK_SIZE * 5]  # Ensure starting position aligns with BLOCK_SIZE grid
    snake1_body = [list(snake1_pos),
                   [snake1_pos[0] - BLOCK_SIZE, snake1_pos[1]],
                   [snake1_pos[0] - (2 * BLOCK_SIZE), snake1_pos[1]]]
    snake1_direction = 'RIGHT'
    change_to1 = snake1_direction

    # Initialize icon lists for snake1
    snake1_icon_list = [snake1_head_image] + [DEFAULT_BODY_ICON] * (len(snake1_body) -1)

    # For double player mode
    if not single_player:
        snake2_pos = [BLOCK_SIZE * (GAME_WIDTH // BLOCK_SIZE - 5), BLOCK_SIZE * (GAME_HEIGHT // BLOCK_SIZE - 5)]
        snake2_body = [list(snake2_pos),
                       [snake2_pos[0] + BLOCK_SIZE, snake2_pos[1]],
                       [snake2_pos[0] + (2 * BLOCK_SIZE), snake2_pos[1]]]
        snake2_direction = 'LEFT'
        change_to2 = snake2_direction

        # Initialize icon lists for snake2
        snake2_icon_list = [snake2_head_image] + [DEFAULT_BODY_ICON] * (len(snake2_body) -1)
    else:
        snake2_pos = None  # Define snake2_pos as None for single-player mode
        snake2_body = []
        snake2_icon_list = []

    # Food settings
    food_pos = [np.random.randint(0, GAME_WIDTH // BLOCK_SIZE) * BLOCK_SIZE,
                np.random.randint(0, GAME_HEIGHT // BLOCK_SIZE) * BLOCK_SIZE]
    food_spawn = True
    food_icon = random.choice(FOOD_ICONS) if FOOD_ICONS else None

    # Game variables
    pause = False
    game_over_flag = False
    winner_face_image = None  # To store the winner's face image

    # Countdown before the game starts
    countdown(single_player, snake1_head_image, snake2_head_image, snake1_pos, snake2_pos)

    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                cv2.destroyAllWindows()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pause = not pause
                elif event.key == pygame.K_f:
                    toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    if is_fullscreen:
                        toggle_fullscreen()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    cap.release()
                    cv2.destroyAllWindows()
                    sys.exit()
                if not pause:
                    # Controls for snake 1
                    if single_player:
                        # In single-player mode, allow both arrow keys and W/A/S/D
                        if event.key == pygame.K_UP or event.key == ord('w'):
                            if snake1_direction != 'DOWN':
                                change_to1 = 'UP'
                        elif event.key == pygame.K_DOWN or event.key == ord('s'):
                            if snake1_direction != 'UP':
                                change_to1 = 'DOWN'
                        elif event.key == pygame.K_LEFT or event.key == ord('a'):
                            if snake1_direction != 'RIGHT':
                                change_to1 = 'LEFT'
                        elif event.key == pygame.K_RIGHT or event.key == ord('d'):
                            if snake1_direction != 'LEFT':
                                change_to1 = 'RIGHT'
                    else:
                        # In double-player mode, arrow keys control snake1
                        if event.key == pygame.K_UP:
                            if snake1_direction != 'DOWN':
                                change_to1 = 'UP'
                        elif event.key == pygame.K_DOWN:
                            if snake1_direction != 'UP':
                                change_to1 = 'DOWN'
                        elif event.key == pygame.K_LEFT:
                            if snake1_direction != 'RIGHT':
                                change_to1 = 'LEFT'
                        elif event.key == pygame.K_RIGHT:
                            if snake1_direction != 'LEFT':
                                change_to1 = 'RIGHT'

                        # Controls for snake 2
                        if event.key == ord('w'):
                            if snake2_direction != 'DOWN':
                                change_to2 = 'UP'
                        elif event.key == ord('s'):
                            if snake2_direction != 'UP':
                                change_to2 = 'DOWN'
                        elif event.key == ord('a'):
                            if snake2_direction != 'RIGHT':
                                change_to2 = 'LEFT'
                        elif event.key == ord('d'):
                            if snake2_direction != 'LEFT':
                                change_to2 = 'RIGHT'
        if pause:
            continue

        # Validate direction for snake1
        if change_to1 == 'UP' and snake1_direction != 'DOWN':
            snake1_direction = 'UP'
        if change_to1 == 'DOWN' and snake1_direction != 'UP':
            snake1_direction = 'DOWN'
        if change_to1 == 'LEFT' and snake1_direction != 'RIGHT':
            snake1_direction = 'LEFT'
        if change_to1 == 'RIGHT' and snake1_direction != 'LEFT':
            snake1_direction = 'RIGHT'

        # Update snake1 position
        if snake1_direction == 'UP':
            snake1_pos[1] -= BLOCK_SIZE
        if snake1_direction == 'DOWN':
            snake1_pos[1] += BLOCK_SIZE
        if snake1_direction == 'LEFT':
            snake1_pos[0] -= BLOCK_SIZE
        if snake1_direction == 'RIGHT':
            snake1_pos[0] += BLOCK_SIZE

        # Wrap snake1 position around the screen
        snake1_pos[0] %= GAME_WIDTH
        snake1_pos[1] %= GAME_HEIGHT

        # Insert new head position and image
        snake1_body.insert(0, list(snake1_pos))
        #snake1_icon_list.insert(0, snake1_head_image)  # Always insert head image at index 0

        if snake1_pos == food_pos:
            food_spawn = False
            # Append the food icon to the tail of the icon list
            snake1_icon_list.append(food_icon)
        else:
            # Remove the tail to keep the snake length constant
            snake1_body.pop()

        if not single_player:
            # Validate direction for snake2
            if change_to2 == 'UP' and snake2_direction != 'DOWN':
                snake2_direction = 'UP'
            if change_to2 == 'DOWN' and snake2_direction != 'UP':
                snake2_direction = 'DOWN'
            if change_to2 == 'LEFT' and snake2_direction != 'RIGHT':
                snake2_direction = 'LEFT'
            if change_to2 == 'RIGHT' and snake2_direction != 'LEFT':
                snake2_direction = 'RIGHT'

            # Update snake2 position
            if snake2_direction == 'UP':
                snake2_pos[1] -= BLOCK_SIZE
            if snake2_direction == 'DOWN':
                snake2_pos[1] += BLOCK_SIZE
            if snake2_direction == 'LEFT':
                snake2_pos[0] -= BLOCK_SIZE
            if snake2_direction == 'RIGHT':
                snake2_pos[0] += BLOCK_SIZE

            # Wrap snake2 position around the screen
            snake2_pos[0] %= GAME_WIDTH
            snake2_pos[1] %= GAME_HEIGHT

            # Insert new head position and image
            snake2_body.insert(0, list(snake2_pos))

            if snake2_pos == food_pos:
                food_spawn = False
                # Append the food icon to the tail of the icon list
                snake2_icon_list.append(food_icon)
            else:
                # Remove the tail to keep the snake length constant
                snake2_body.pop()

        # Spawn food
        if not food_spawn:
            while True:
                food_pos = [np.random.randint(0, GAME_WIDTH // BLOCK_SIZE) * BLOCK_SIZE,
                            np.random.randint(0, GAME_HEIGHT // BLOCK_SIZE) * BLOCK_SIZE]
                # Ensure food doesn't spawn on top of the snake
                if (food_pos not in snake1_body) and (single_player or food_pos not in snake2_body):
                    break
            food_spawn = True
            food_icon = random.choice(FOOD_ICONS) if FOOD_ICONS else None

        # Game Over conditions
        # For snake1
        for block in snake1_body[1:]:
            if snake1_pos == block:
                # Player 1 collided with itself; Player 2 wins
                winner_face_image = player2_face_large if not single_player else None
                game_over_flag = True
                break

        if game_over_flag:
            pass  # Already determined the winner
        else:
            # For snake2
            if not single_player:
                for block in snake2_body[1:]:
                    if snake2_pos == block:
                        # Player 2 collided with itself; Player 1 wins
                        winner_face_image = player1_face_large
                        game_over_flag = True
                        break

                if not game_over_flag:
                    # Check if snake1's head collides with snake2's body (excluding head)
                    for block in snake2_body[1:]:
                        if snake1_pos == block:
                            # Player 1 hit Player 2's body; Player 2 wins
                            winner_face_image = player2_face_large
                            game_over_flag = True
                            break

                if not game_over_flag:
                    # Check if snake2's head collides with snake1's body (excluding head)
                    for block in snake1_body[1:]:
                        if snake2_pos == block:
                            # Player 2 hit Player 1's body; Player 1 wins
                            winner_face_image = player1_face_large
                            game_over_flag = True
                            break

                if not game_over_flag:
                    # Check if both snakes' heads collide
                    if snake1_pos == snake2_pos:
                        # It's a draw
                        winner_face_image = None
                        game_over_flag = True

        # Create a game surface with the original game dimensions
        game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

        # Capture camera frame
        ret, frame = cap.read()
        if not ret:
            continue

        # Process camera frame
        frame_surface, _, _, _, _ = process_camera_frame(frame)

        # Display camera frame on the game surface
        game_surface.blit(frame_surface, (0, 0))

        # Draw snake1
        for idx, pos in enumerate(snake1_body):
            segment_image = snake1_icon_list[idx]
            if segment_image:
                game_surface.blit(segment_image, (pos[0], pos[1]))
            else:
                if DEFAULT_BODY_ICON:
                    game_surface.blit(DEFAULT_BODY_ICON, (pos[0], pos[1]))
                else:
                    # Draw default body segment
                    pygame.draw.rect(game_surface, WHITE, pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))

        # Draw snake2
        if not single_player:
            for idx, pos in enumerate(snake2_body):
                segment_image = snake2_icon_list[idx]
                if segment_image:
                    game_surface.blit(segment_image, (pos[0], pos[1]))
                else:
                    if DEFAULT_BODY_ICON:
                        game_surface.blit(DEFAULT_BODY_ICON, (pos[0], pos[1]))
                    else:
                        pygame.draw.rect(game_surface, YELLOW, pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))

        # Draw food
        if food_icon:
            game_surface.blit(food_icon, (food_pos[0], food_pos[1]))
        else:
            pygame.draw.rect(game_surface, RED, pygame.Rect(food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE))

        # Check for game over after drawing the final frame
        if game_over_flag:
            game_over_screen(game_surface, winner_face_image)
            return  # Return to main menu

        # Scale and center the game surface onto the window
        scale_and_center(game_surface)

        # Control game speed
        clock.tick(speed)

def countdown(single_player, snake1_head_image, snake2_head_image, snake1_pos, snake2_pos):
    countdown_font = pygame.font.SysFont('Arial', 100)
    info_font = pygame.font.SysFont('Arial', 30)
    for count in ["3", "2", "1", "Go!"]:
        # Create a game surface with the original game dimensions
        game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

        # Capture camera frame
        ret, frame = cap.read()
        if not ret:
            continue

        # Process camera frame
        frame_surface, _, _, _, _ = process_camera_frame(frame)

        # Display camera frame on the game surface
        game_surface.blit(frame_surface, (0, 0))

        # Optionally, you can draw the snakes in their starting positions
        # Draw snake1
        initial_snake1_body = [list(snake1_pos),
                               [snake1_pos[0] - BLOCK_SIZE, snake1_pos[1]],
                               [snake1_pos[0] - (2 * BLOCK_SIZE), snake1_pos[1]]]
        for idx, pos in enumerate(initial_snake1_body):
            if idx == 0 and snake1_head_image:
                # Draw the head image
                game_surface.blit(snake1_head_image, (pos[0], pos[1]))
            else:
                if DEFAULT_BODY_ICON:
                    game_surface.blit(DEFAULT_BODY_ICON, (pos[0], pos[1]))
                else:
                    pygame.draw.rect(game_surface, WHITE, pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))

        # Draw snake2 if double-player
        if not single_player and snake2_pos is not None:
            initial_snake2_body = [list(snake2_pos),
                                   [snake2_pos[0] + BLOCK_SIZE, snake2_pos[1]],
                                   [snake2_pos[0] + (2 * BLOCK_SIZE), snake2_pos[1]]]
            for idx, pos in enumerate(initial_snake2_body):
                if idx == 0 and snake2_head_image:
                    # Draw the head image
                    game_surface.blit(snake2_head_image, (pos[0], pos[1]))
                else:
                    if DEFAULT_BODY_ICON:
                        game_surface.blit(DEFAULT_BODY_ICON, (pos[0], pos[1]))
                    else:
                        pygame.draw.rect(game_surface, YELLOW, pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))

        # Render countdown text
        countdown_text = countdown_font.render(count, True, WHITE)
        game_surface.blit(countdown_text, (GAME_WIDTH//2 - countdown_text.get_width()//2, GAME_HEIGHT//2 - countdown_text.get_height()//2))

        # Optional: Display instructions or get ready text
        get_ready_text = info_font.render("Get Ready!", True, WHITE)
        game_surface.blit(get_ready_text, (GAME_WIDTH//2 - get_ready_text.get_width()//2, GAME_HEIGHT//2 - countdown_text.get_height()))

        # Scale and center the game surface onto the window
        scale_and_center(game_surface)

        # Wait for a second
        pygame.time.delay(1000)

        # Handle events during the countdown
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                cv2.destroyAllWindows()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    if is_fullscreen:
                        toggle_fullscreen()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    cap.release()
                    cv2.destroyAllWindows()
                    sys.exit()

def process_camera_frame(frame):
    # Flip and convert to RGB
    frame = cv2.flip(frame, 1)  # Flip horizontally to mirror the image
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Get the frame dimensions
    frame_height, frame_width = frame.shape[:2]

    # Calculate the aspect ratios
    frame_aspect = frame_width / frame_height
    game_aspect = GAME_WIDTH / GAME_HEIGHT

    # Determine scaling factors to preserve aspect ratio
    if frame_aspect > game_aspect:
        # Frame is wider than game surface
        scale_factor = GAME_HEIGHT / frame_height
    else:
        # Frame is taller than game surface
        scale_factor = GAME_WIDTH / frame_width

    # Calculate new dimensions
    new_width = int(frame_width * scale_factor)
    new_height = int(frame_height * scale_factor)

    # Resize frame
    resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

    # Convert frame to Pygame surface
    frame_surface = pygame.image.frombuffer(resized_frame.tobytes(), (new_width, new_height), "RGB")

    # Create a black background
    background = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    background.fill(BLACK)

    # Blit the resized frame onto the background to center it
    x_offset = (GAME_WIDTH - new_width) // 2
    y_offset = (GAME_HEIGHT - new_height) // 2
    background.blit(frame_surface, (x_offset, y_offset))

    return background, x_offset, y_offset, scale_factor, resized_frame

def scale_and_center(game_surface):
    if is_fullscreen:
        # Get full-screen dimensions
        infoObject = pygame.display.Info()
        SCREEN_WIDTH, SCREEN_HEIGHT = infoObject.current_w, infoObject.current_h

        # Calculate the scaling factor to fit the game surface into the screen
        scale_width = SCREEN_WIDTH / GAME_WIDTH
        scale_height = SCREEN_HEIGHT / GAME_HEIGHT
        scale = min(scale_width, scale_height)

        # Calculate new dimensions
        new_width = int(GAME_WIDTH * scale)
        new_height = int(GAME_HEIGHT * scale)

        # Scale the game surface
        scaled_surface = pygame.transform.smoothscale(game_surface, (new_width, new_height))

        # Calculate position to center the game surface
        pos_x = (SCREEN_WIDTH - new_width) // 2
        pos_y = (SCREEN_HEIGHT - new_height) // 2

        # Blit the scaled surface onto the window
        window.blit(scaled_surface, (pos_x, pos_y))
    else:
        # In windowed mode, simply blit the game surface onto the window
        window.blit(game_surface, (0, 0))

    # Update the display
    pygame.display.update()

if __name__ == '__main__':
    main_menu()