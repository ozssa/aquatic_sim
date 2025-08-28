#animation.py
import asyncio
import platform
import pygame
from src.sprite_manager import SpriteManager

async def run_animation(background_path, sprite_path, fish_count=5):
    """Main animation function with realistic fish behavior"""
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Realistic Fish Aquarium - Ultra Natural Swimming")
    
    # Load and scale background
    try:
        if platform.system() != "Emscripten" and background_path:
            background = pygame.image.load(background_path).convert()
            background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        else:
            # Create default blue water background
            background = pygame.Surface((WIDTH, HEIGHT))
            background.fill((20, 60, 120))
    except Exception as e:
        print(f"Failed to load background: {e}")
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill((20, 60, 120))
    
    # Create sprite manager
    sprite_manager = SpriteManager(WIDTH, HEIGHT)
    
    # Create mixed schools for more natural behavior
    sprite_manager.create_mixed_school(sprite_path, fish_count)
    
    # Game clock
    clock = pygame.time.Clock()
    
    # UI elements
    font = pygame.font.Font(None, 24)
    show_info = False
    
    print("Aquarium Controls:")
    print("SPACE - Add random fish")
    print("Click - Add fish at mouse position")
    print("R - Reset aquarium")
    print("I - Toggle info display")
    print("ESC - Exit")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    sprite_manager.add_fish(sprite_path)
                elif event.key == pygame.K_r:
                    sprite_manager.clear_all_fish()
                    sprite_manager.create_mixed_school(sprite_path, fish_count)
                elif event.key == pygame.K_i:
                    show_info = not show_info
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                sprite_manager.add_fish(sprite_path, mouse_x, mouse_y)
        
        # Update all sprites
        sprite_manager.update_sprites()
        
        # Draw everything
        screen.blit(background, (0, 0))
        sprite_manager.draw_sprites(screen)
        
        # Display information if enabled
        if show_info:
            fps = clock.get_fps()
            fish_count_current = sprite_manager.get_fish_count()
            
            info_texts = [
                f"FPS: {fps:.1f}",
                f"Fish Count: {fish_count_current}",
                f"Controls: SPACE=Add Fish, R=Reset, I=Info"
            ]
            
            for i, text in enumerate(info_texts):
                text_surface = font.render(text, True, (255, 255, 255))
                text_rect = text_surface.get_rect()
                text_rect.topleft = (10, 10 + i * 25)
                
                bg_rect = text_rect.copy()
                bg_rect.inflate(10, 5)
                pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
                
                screen.blit(text_surface, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(1.0 / 60)
    
    pygame.quit()

async def create_demo_aquarium(sprite_path, background_path=None):
    """Create advanced demo with multiple fish behaviors"""
    pygame.init()
    WIDTH, HEIGHT = 1200, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Advanced Fish Behavior Demo")
    
    # Create enhanced background
    if platform.system() != "Emscripten" and background_path:
        try:
            background = pygame.image.load(background_path).convert()
            background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        except Exception as e:
            print(f"Failed to load background: {e}")
            background = None
    else:
        background = None
    
    if not background:
        background = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            blue = int(20 + ratio * 40)
            green = int(40 + ratio * 20)
            color = (10, green, blue)
            pygame.draw.line(background, color, (0, y), (WIDTH, y))
    
    # Create sprite manager
    sprite_manager = SpriteManager(WIDTH, HEIGHT)
    
    # Create multiple diverse schools
    sprite_manager.create_school(sprite_path, count=6, center_x=200, center_y=200)
    sprite_manager.create_school(sprite_path, count=4, center_x=800, center_y=300)
    sprite_manager.create_school(sprite_path, count=5, center_x=600, center_y=600)
    sprite_manager.create_mixed_school(sprite_path, total_count=10)
    
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    sprite_manager.add_fish(sprite_path)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    sprite_manager.add_fish(sprite_path, mouse_x, mouse_y)
        
        sprite_manager.update_sprites()
        
        screen.blit(background, (0, 0))
        sprite_manager.draw_sprites(screen)
        
        fps = clock.get_fps()
        info_text = font.render(f"Advanced Fish Demo - FPS: {fps:.1f} - Fish: {sprite_manager.get_fish_count()}", True, (255, 255, 255))
        screen.blit(info_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(1.0 / 60)
    
    pygame.quit()