# SUPER SNAKE 1.2 - By Daniel Ruiz Poli aka NoahKnox


# Importaciones librerías
import pygame
import random
import sys
import os
from pygame import mixer
import json

# Inicialización
pygame.init()
mixer.init()

# Constantes
WIDTH = 800
HEIGHT = 600
FPS = 15  
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Colores
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (255, 89, 94)
GREEN = (76, 209, 55)
BLUE = (72, 149, 239)
GRAY = (128, 128, 128)
BACKGROUND = (15, 15, 15)

# Configuración de la ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SUPER SNAKE - By Daniel Ruiz Poli aka NoahKnox")
clock = pygame.time.Clock()

# Funciones
def draw_text(surface, text, size, x, y, color):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

# Clases
class ParticleEffect:
    def __init__(self, x, y, color):
        self.particles = []
        for _ in range(10):
            particle = {
                'x': x,
                'y': y,
                'dx': random.uniform(-2, 2),
                'dy': random.uniform(-2, 2),
                'lifetime': 30,
                'color': color
            }
            self.particles.append(particle)
    # Actualizar partículas
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['lifetime'] -= 1
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    # Dibujar partículas
    def draw(self, surface):
        for particle in self.particles:
            alpha = int((particle['lifetime'] / 30) * 255)
            color = (*particle['color'][:3], alpha)
            pygame.draw.circle(surface, color, 
                             (int(particle['x']), int(particle['y'])), 2)

# Clase para la serpiente
class Snake(pygame.sprite.Sprite):
    def __init__(self, sprite_sheet=None):
        super().__init__()
        self.load_sprites(sprite_sheet)
        self.direction = "right"
        self.speed = GRID_SIZE
        self.body = []
        self.positions = []
        self.reset()
    
    # Crear sprites por defecto
    def create_default_sprites(self):
        self.head_images = {}
        head_surf = pygame.Surface((GRID_SIZE, GRID_SIZE))
        head_surf.fill(GREEN)
        for direction in ["right", "left", "up", "down"]:
            self.head_images[direction] = head_surf.copy()
        body_surf = pygame.Surface((GRID_SIZE, GRID_SIZE))
        body_surf.fill(GREEN)
        self.body_image = body_surf
    
    # Cargar sprites desde una hoja de sprites
    def load_sprites(self, sprite_sheet):
        try:
            if sprite_sheet:
                self.head_images = {
                    "right": pygame.transform.scale(sprite_sheet.subsurface((0, 0, 64, 64)), (GRID_SIZE, GRID_SIZE)),
                    "left": pygame.transform.scale(pygame.transform.flip(sprite_sheet.subsurface((0, 0, 64, 64)), True, False), (GRID_SIZE, GRID_SIZE)),
                    "up": pygame.transform.scale(pygame.transform.rotate(sprite_sheet.subsurface((0, 0, 64, 64)), 90), (GRID_SIZE, GRID_SIZE)),
                    "down": pygame.transform.scale(pygame.transform.rotate(sprite_sheet.subsurface((0, 0, 64, 64)), -90), (GRID_SIZE, GRID_SIZE))
                }
                self.body_image = pygame.transform.scale(sprite_sheet.subsurface((64, 0, 64, 64)), (GRID_SIZE, GRID_SIZE))
            else:
                raise Exception("No sprite sheet provided")
        except:
            self.create_default_sprites()
    
    # Resetear la serpiente
    def reset(self):
        self.rect = self.head_images["right"].get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.direction = "right"
        self.body = []
        self.positions = [(self.rect.x, self.rect.y)]
    
    # Hacer que la serpiente crezca
    def grow(self):
        body_part = pygame.sprite.Sprite()
        body_part.image = self.body_image
        body_part.rect = body_part.image.get_rect()
        if self.body:
            body_part.rect.center = self.positions[-1]
        else:
            body_part.rect.center = self.positions[0]
        self.body.append(body_part)
    
    # Actualizar la serpiente
    def update(self):
        # Guardar posición anterior
        self.positions.insert(0, (self.rect.x, self.rect.y))
        if len(self.positions) > len(self.body) + 1:
            self.positions.pop()
        
        # Movimiento
        keys = pygame.key.get_pressed()
        new_direction = self.direction
        if keys[pygame.K_LEFT] and self.direction != "right":
            new_direction = "left"
        if keys[pygame.K_RIGHT] and self.direction != "left":
            new_direction = "right"
        if keys[pygame.K_UP] and self.direction != "down":
            new_direction = "up"
        if keys[pygame.K_DOWN] and self.direction != "up":
            new_direction = "down"

        self.direction = new_direction
        self.image = self.head_images[self.direction]

        # Mover según dirección
        if self.direction == "right":
            self.rect.x += self.speed
        elif self.direction == "left":
            self.rect.x -= self.speed
        elif self.direction == "up":
            self.rect.y -= self.speed
        elif self.direction == "down":
            self.rect.y += self.speed

        # Actualizar cuerpo
        for i, body_part in enumerate(self.body):
            body_part.rect.x = self.positions[i + 1][0]
            body_part.rect.y = self.positions[i + 1][1]
    
    # Dibujar la serpiente
    def draw(self, surface):
        # Dibujar cuerpo
        for body_part in self.body:
            surface.blit(body_part.image, body_part.rect)
        # Dibujar cabeza
        surface.blit(self.image, self.rect)

# Clase para la comida
class Food(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.reposition()
    
    # Reposicionar la comida
    def reposition(self):
        self.rect.x = random.randrange(0, WIDTH - GRID_SIZE, GRID_SIZE)
        self.rect.y = random.randrange(0, HEIGHT - GRID_SIZE, GRID_SIZE)
    
    # Dibujar la comida
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 1)
        glow_rect = self.rect.copy()
        glow_rect.inflate_ip(4, 4)
        pygame.draw.rect(surface, (*RED, 128), glow_rect, 2)

# Clase para el juego
class Game:
    def __init__(self):
        self.load_assets()
        self.high_score = self.load_high_score()
        self.difficulty = "NORMAL"  # Dificultad por defecto
        self.reset_game()
        self.particles = []
    
    # Cargar los assets
    def load_assets(self):
        self.assets = {'sounds': {}, 'images': {}, 'fonts': {}}
        try:
            sprite_sheet = pygame.image.load("images/Snake sprite sheet.png").convert_alpha()
            self.assets['images']['sprite_sheet'] = sprite_sheet
        except:
            self.assets['images']['sprite_sheet'] = None
    
    # Cargar el high score
    def load_high_score(self):
        try:
            with open('high_score.json', 'r') as f:
                return json.load(f)['high_score']
        except:
            return 0
    
    # Guardar el high score
    def save_high_score(self):
        try:
            with open('high_score.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            print("Error guardando high score")
    
    # Resetear el juego
    def reset_game(self):
        self.snake = Snake(self.assets['images'].get('sprite_sheet'))
        self.food = Food()
        self.score = 0
        self.game_over = False
    
    # Comprobar colisiones
    def check_collisions(self):
        # Colisión con la comida
        if pygame.sprite.collide_rect(self.snake, self.food):
            self.food.reposition()
            self.score += 10
            self.snake.grow()
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            self.particles.append(ParticleEffect(
                self.food.rect.centerx, 
                self.food.rect.centery, 
                GREEN))
        
        # Colisión con los bordes
        if (self.snake.rect.right > WIDTH or self.snake.rect.left < 0 or 
            self.snake.rect.bottom > HEIGHT or self.snake.rect.top < 0):
            self.game_over = True
        
        # Colisión con el cuerpo
        for body_part in self.snake.body[1:]:
            if self.snake.rect.colliderect(body_part.rect):
                self.game_over = True
    
    # Actualizar el juego
    def update(self):
        if not self.game_over:
            self.snake.update()
            self.check_collisions()
            for particle in self.particles[:]:
                particle.update()
                if not particle.particles:
                    self.particles.remove(particle)
    
    # Dibujar el juego
    def draw(self):
        screen.fill(BACKGROUND)
        
        # Grid
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(screen, (30, 30, 30), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, (30, 30, 30), (0, y), (WIDTH, y))
        
        self.snake.draw(screen)
        self.food.draw(screen)
        
        for particle in self.particles:
            particle.draw(screen)
        
        # UI
        draw_text(screen, f"Score: {self.score}", 36, WIDTH//2, 10, WHITE)
        draw_text(screen, f"High Score: {self.high_score}", 24, WIDTH-100, 10, GRAY)
        
        pygame.display.flip()
    
    # Mostrar instrucciones
    def show_instructions(self):
        screen.fill(BLACK)
        
        # Título
        draw_text(screen, "INSTRUCCIONES", 64, WIDTH//2, 50, GREEN)
        
        # Instrucciones del juego
        instructions = [
            "CONTROLES:",
            "- Flechas del teclado para mover la serpiente",
            "- ESC para volver al menú",
            "",
            "OBJETIVO:",
            "- Come la comida roja para crecer",
            "- Cada comida vale 10 puntos",
            "- Evita chocar con los bordes",
            "- No choques con tu propio cuerpo",
            "",
            "CONSEJOS:",
            "- Planifica tu ruta con anticipación",
            "- Mantén espacio para maniobrar",
            "",
            "Presiona ESPACIO para volver al menú"
        ]
        
        y_pos = 150
        for i, line in enumerate(instructions):
            color = GREEN if line.endswith(":") else WHITE
            size = 36 if line.endswith(":") else 28
            draw_text(screen, line, size, WIDTH//2, y_pos, color)
            y_pos += 35
        
        pygame.display.flip()
        
        waiting = True
        while waiting:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                        waiting = False
    
    # Obtener la velocidad por dificultad
    def get_speed_by_difficulty(self):
        speeds = {
            "FÁCIL": 10,
            "NORMAL": 15,
            "DIFÍCIL": 20,
            "EXPERTO": 25
        }
        return speeds.get(self.difficulty, 15)
    
    # Mostrar el menú de dificultad
    def show_difficulty_menu(self):
        screen.fill(BLACK)
        
        # Título
        draw_text(screen, "SELECCIONA DIFICULTAD", 64, WIDTH//2, HEIGHT//4, GREEN)
        
        # Opciones de dificultad con descripción de velocidad
        difficulties = [
            ("FÁCIL - Velocidad Baja [1]", HEIGHT//2 - 90, "FÁCIL"),
            ("NORMAL - Velocidad Media [2]", HEIGHT//2 - 30, "NORMAL"),
            ("DIFÍCIL - Velocidad Alta [3]", HEIGHT//2 + 30, "DIFÍCIL"),
            ("EXPERTO - Velocidad Máxima [4]", HEIGHT//2 + 90, "EXPERTO")
        ]
        
        # Dibujar opciones con efecto hover y selección actual
        mouse_pos = pygame.mouse.get_pos()
        for text, y, diff_name in difficulties:
            button_rect = pygame.Rect(WIDTH//2 - 200, y - 15, 400, 40)
            
            # Resaltar la dificultad seleccionada y el hover
            if diff_name == self.difficulty:
                pygame.draw.rect(screen, GREEN, button_rect, 2)
                color = GREEN
            elif button_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, BLUE, button_rect, 2)
                color = BLUE
            else:
                color = WHITE
            
            draw_text(screen, text, 36, WIDTH//2, y, color)
        
        # Instrucciones
        draw_text(screen, "Presiona ESPACIO para volver al menú", 24, WIDTH//2, HEIGHT - 50, GRAY)
        
        pygame.display.flip()
        
        waiting = True
        while waiting:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Manejo de eventos del teclado
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                    elif event.key == pygame.K_1:
                        self.difficulty = "FÁCIL"
                        waiting = False
                    elif event.key == pygame.K_2:
                        self.difficulty = "NORMAL"
                        waiting = False
                    elif event.key == pygame.K_3:
                        self.difficulty = "DIFÍCIL"
                        waiting = False
                    elif event.key == pygame.K_4:
                        self.difficulty = "EXPERTO"
                        waiting = False
                
                # Manejo de clics del mouse
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic izquierdo
                        mouse_pos = pygame.mouse.get_pos()
                        for _, y, diff_name in difficulties:
                            button_rect = pygame.Rect(WIDTH//2 - 200, y - 15, 400, 40)
                            if button_rect.collidepoint(mouse_pos):
                                self.difficulty = diff_name
                                waiting = False
                                break
        
        # Actualizar la velocidad de la serpiente después de cambiar la dificultad
        if hasattr(self, 'snake'):
            self.snake.speed = self.get_speed_by_difficulty()
    
    def show_menu(self):
        screen.fill(BLACK)
        
        # Título con efecto de sombra
        draw_text(screen, "SUPER SNAKE", 64, WIDTH//2 + 2, HEIGHT//4 + 2, GRAY)
        draw_text(screen, "SUPER SNAKE", 64, WIDTH//2, HEIGHT//4, GREEN)
        draw_text(screen, "By PoliXDev", 32, WIDTH//2, HEIGHT//4 + 50, GRAY)
        
        # Botones del menú
        buttons = [
            ("JUGAR [ESPACIO]", HEIGHT//2),
            (f"DIFICULTAD: {self.difficulty} [D]", HEIGHT//2 + 60),
            ("INSTRUCCIONES [I]", HEIGHT//2 + 120),
            ("SALIR [ESC]", HEIGHT//2 + 180)
        ]
        
        # Dibujar botones con efecto hover
        mouse_pos = pygame.mouse.get_pos()
        for text, y in buttons:
            button_rect = pygame.Rect(WIDTH//2 - 150, y - 15, 300, 40)
            if button_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, GREEN, button_rect, 2)
                color = GREEN
            else:
                color = WHITE
            draw_text(screen, text, 36, WIDTH//2, y, color)
        
        # Créditos
        draw_text(screen, "Proyecto de Estudios - ConquerBlocks - Noviembre 2024", 20, WIDTH//2, HEIGHT - 30, GRAY)
        
        pygame.display.flip()
        #Esperar input del usuario
        waiting = True
        while waiting:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                    elif event.key == pygame.K_d:  
                        self.show_difficulty_menu()
                        return self.show_menu()
                    elif event.key == pygame.K_i:
                        self.show_instructions()
    
    # Bucle del juego
    def game_loop(self):
        while not self.game_over:
            clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                    return
            
            self.update()
            self.draw()
    
    # Mostrar el menú de Game Over
    def show_game_over(self):
        screen.fill(BLACK)
        draw_text(screen, "GAME OVER", 64, WIDTH//2, HEIGHT//4, RED)
        draw_text(screen, f"Score: {self.score}", 48, WIDTH//2, HEIGHT//2, WHITE)
        draw_text(screen, "Presiona ESPACIO para jugar de nuevo", 36, WIDTH//2, HEIGHT*3/4, WHITE)
        pygame.display.flip()
        
        waiting = True
        while waiting:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

# Mostrar la pantalla de intro
def show_intro():
    screen.fill(BLACK)
    
    # Logo o título de ConquerBlocks 
    draw_text(screen, "MASTER FULL STACK", 48, WIDTH//2, HEIGHT//4 - 70, BLUE)
    draw_text(screen, "ACADEMIA CONQUERBLOCKS", 64, WIDTH//2, HEIGHT//4, WHITE)
    
    # Información del proyecto 
    draw_text(screen, "Proyecto: SUPER SNAKE", 36, WIDTH//2, HEIGHT//2 - 50, GREEN)
    draw_text(screen, "Desarrollado en Python 3.12", 32, WIDTH//2, HEIGHT//2, GRAY)
    draw_text(screen, "Modulo Python Avanzado", 32, WIDTH//2, HEIGHT//2 + 40, GRAY)

    # Créditos del desarrollador 
    draw_text(screen, "Codigo escrito por:", 28, WIDTH//2, HEIGHT*3/4 - 60, WHITE)
    draw_text(screen, "Daniel Ruiz Poli", 42, WIDTH//2, HEIGHT*3/4 - 20, GREEN)
    draw_text(screen, "GitHub: PoliXDev", 36, WIDTH//2, HEIGHT*3/4 + 20, BLUE)
    draw_text(screen, "Estudiante de ConquerBlocks", 28, WIDTH//2, HEIGHT*3/4 + 50, GRAY)
    
    # Instrucción para continuar
    draw_text(screen, "Presiona ESPACIO para continuar", 24, WIDTH//2, HEIGHT - 30, WHITE)
    
    pygame.display.flip()
    
    # Esperar input del usuario
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

# Función principal
def main():
    show_intro()  #
    game = Game()
    while True:
        game.show_menu()
        game.game_loop()
        if game.game_over:
            game.show_game_over()
            game.reset_game()

if __name__ == "__main__":
    main()

    


