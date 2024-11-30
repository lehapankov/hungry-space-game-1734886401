import pygame
import sys
import random
import math
from game.spaceship import Spaceship
from game.collectible import Collectible
from game.particle import ParticleSystem
from game.constants import *

class Game:
    def __init__(self):
        print("Initializing game...")
        try:
            pygame.init()
            print("Pygame initialized successfully")
            
            pygame.mixer.init()
            print("Pygame mixer initialized successfully")
            
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Hungry Space")
            print("Display window created successfully")
            
            # Game state initialization
            
            # Load sounds with error handling
            try:
                self.collect_sound = pygame.mixer.Sound('assets/sounds/collect.wav')
                self.gameover_sound = pygame.mixer.Sound('assets/sounds/gameover.wav')
                print("Sound files loaded successfully")
            except Exception as e:
                print(f"Warning: Could not load sound files: {e}")
                # Create dummy sound object that does nothing when played
                class DummySound:
                    def play(self): pass
                self.collect_sound = self.gameover_sound = DummySound()
            
            self.reset_game()
            print("Initial setup complete")
            
        except Exception as e:
            print(f"Fatal error during game initialization: {e}")
            pygame.quit()
            sys.exit(1)
    
    def reset_game(self):
        # Create game objects with random size variation
        initial_size = 40
        self.spaceship = Spaceship()
        self.collectibles = pygame.sprite.Group()
        self.particle_system = ParticleSystem()
        print("Game objects created successfully")
        
        # Game state
        self.score = 0
        self.game_over = False
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        
        # Spawn initial collectibles
        self.spawn_collectibles(5)
    
    def spawn_collectible_at_edge(self):
        # Choose a random edge (0: top, 1: right, 2: bottom, 3: left)
        edge = random.randint(0, 3)
        
        if edge == 0:  # Top
            x = random.randint(0, SCREEN_WIDTH)
            y = -COLLECTIBLE_SIZE_LARGE
            direction = random.uniform(math.pi / 4, 3 * math.pi / 4)  # Downward
        elif edge == 1:  # Right
            x = SCREEN_WIDTH + COLLECTIBLE_SIZE_LARGE
            y = random.randint(0, SCREEN_HEIGHT)
            direction = random.uniform(3 * math.pi / 4, 5 * math.pi / 4)  # Leftward
        elif edge == 2:  # Bottom
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + COLLECTIBLE_SIZE_LARGE
            direction = random.uniform(5 * math.pi / 4, 7 * math.pi / 4)  # Upward
        else:  # Left
            x = -COLLECTIBLE_SIZE_LARGE
            y = random.randint(0, SCREEN_HEIGHT)
            direction = random.uniform(-math.pi / 4, math.pi / 4)  # Rightward
        
        speed = random.uniform(COLLECTIBLE_SPEED_MIN, COLLECTIBLE_SPEED_MAX)
        velocity = (math.cos(direction) * speed, math.sin(direction) * speed)
        
        return Collectible(game=self, position=(x, y), velocity=velocity)
    
    def spawn_collectibles(self, count):
        for _ in range(count):
            self.collectibles.add(self.spawn_collectible_at_edge())
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and self.game_over:
                if event.key == pygame.K_SPACE:
                    self.reset_game()
            elif not self.game_over:
                self.spaceship.handle_event(event)
        return True
    
    def update(self):
        if not self.game_over:
            self.spaceship.update()
            self.collectibles.update()
            self.particle_system.update()
            
            # Maintain constant number of collectibles
            while len(self.collectibles) < 5:
                self.spawn_collectibles(1)
            
            # Check collisions
            collisions = pygame.sprite.spritecollide(self.spaceship, self.collectibles, True, 
                                          pygame.sprite.collide_mask)
            for collision in collisions:
                if collision.size > self.spaceship.size:
                    self.game_over = True
                    self.gameover_sound.play()
                    self.particle_system.create_particles(collision.rect.center)
                else:
                    self.score += collision.points
                    self.collect_sound.play()
                    self.particle_system.create_particles(collision.rect.center)
                    # Update spaceship size based on collected item
                    self.spaceship.adjust_size(collision.size)
    
    def draw(self):
        try:
            self.screen.fill(BACKGROUND_COLOR)
            
            # Draw game objects
            for collectible in self.collectibles:
                collectible.draw(self.screen)
            self.spaceship.draw(self.screen)
            self.particle_system.draw(self.screen)
            
            # Draw score
            score_text = self.font.render(f'Score: {self.score}', True, WHITE)
            self.screen.blit(score_text, (10, 10))
            
            # Draw game over message
            if self.game_over:
                # Game over message
                game_over_text = self.font.render('Game Over! Press SPACE to restart', True, WHITE)
                text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
                self.screen.blit(game_over_text, text_rect)
                
                # Game over screen
            
            pygame.display.flip()
        except Exception as e:
            print(f"Error during drawing: {e}")
    
    def run(self):
        print("Starting game loop...")
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()