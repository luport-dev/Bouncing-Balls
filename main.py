import pygame
import random
import math
from typing import List, Tuple
from ball import Ball
from hexagon import Hexagon
from background import Background
from rankings import Rankings
from constants import WIDTH, HEIGHT, FPS, BALL_SPEED, WHITE, BLACK, COLORS

# Initialize Pygame
pygame.init()


# Get screen info
screen_info = pygame.display.Info()
HEIGHT = int(screen_info.current_h * 0.6)  # 60% der Bildschirmhöhe
WIDTH = int(HEIGHT * 4/3)  # 4:3 Verhältnis basierend auf der Höhe

# Constants
FPS = 60
BALL_SPEED = 7 

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255)   # Cyan
]


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bouncing Balls")
    clock = pygame.time.Clock()
    
    # Create Rankings instance
    rankings = Rankings(WIDTH, HEIGHT, WHITE)
    
    # Cache für häufig verwendete Surfaces
    particle_surfaces = {}
    
    # Erstelle den animierten Hintergrund
    background = Background(WIDTH, HEIGHT)

    # Globale Liste für fallende Quadrate
    falling_squares = []

    # Hexagongröße (etwas größer als die ursprüngliche Quadratgröße)
    hexagon_size = 40  # Radius des Hexagons
    # Abstand vom Rand (20% der Fensterbreite/höhe)
    margin_x = int(WIDTH * 0.20)
    margin_y = int(HEIGHT * 0.20)

    # Erstelle fünf Hexagone symmetrisch angeordnet
    hexagons = [
        Hexagon(margin_x, margin_y, hexagon_size),  # Links oben
        Hexagon(WIDTH - margin_x - hexagon_size*2, margin_y, hexagon_size),  # Rechts oben
        Hexagon(WIDTH//2 - hexagon_size, HEIGHT//2 - hexagon_size, hexagon_size),  # Mitte
        Hexagon(margin_x, HEIGHT - margin_y - hexagon_size*2, hexagon_size),  # Links unten
        Hexagon(WIDTH - margin_x - hexagon_size*2, HEIGHT - margin_y - hexagon_size*2, hexagon_size)  # Rechts unten
    ]

    # Create three balls with different colors
    balls = []
    for color in COLORS:
        # Versuche maximal 100 Mal, eine gültige Position zu finden
        valid_position = False
        for _ in range(100):
            # Generiere eine zufällige Position
            x = random.randint(50, WIDTH-50)
            y = random.randint(50, HEIGHT-50)
            
            # Prüfe, ob diese Position mit einem Hexagon kollidiert
            collision = False
            temp_ball = Ball(x, y, color)
            for hexagon in hexagons:
                if hexagon.check_collision(temp_ball):
                    collision = True
                    break
            
            # Wenn keine Kollision gefunden wurde, behalte diese Position
            if not collision:
                balls.append(temp_ball)
                valid_position = True
                break
        
        # Wenn keine gültige Position gefunden wurde, platziere den Ball in der Mitte
        if not valid_position:
            balls.append(Ball(WIDTH//2, HEIGHT//2, color))

    # Liste für eliminierte Bälle
    eliminated_balls = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update background
        background.update()

        # Update hexagons rotation
        for hexagon in hexagons:
            hexagon.update()

        # Update ball positions
        for ball in balls[:]:  # Kopie der Liste für sichere Iteration
            ball.move()
            # Verschiebe fallende Quadrate in die globale Liste
            for particle in ball.particles[:]:
                if particle.get('type') == 'falling_square':
                    falling_squares.append(particle)
                    ball.particles.remove(particle)
            ball.update_particles()
            if ball.update():  # Wenn True, ist die Explosion fertig
                # Verschiebe alle verbleibenden fallenden Quadrate in die globale Liste
                for particle in ball.particles[:]:
                    if particle.get('type') == 'falling_square':
                        falling_squares.append(particle)
                        ball.particles.remove(particle)
                eliminated_balls.append(ball)  # Füge eliminierten Ball zur Liste hinzu
                balls.remove(ball)
                background.update_colors(balls, ball.color)  # Aktualisiere Hintergrundfarben
                continue

        # Update falling squares
        for square in falling_squares:
            if not square['is_resting']:
                # Füge Gravitation hinzu
                square['dy'] += square['gravity']
                
                # Bewege das Quadrat
                square['x'] += square['dx']
                square['y'] += square['dy']
                
                # Rotiere das Quadrat
                square['rotation'] += square['rotation_speed']
                
                # Prüfe Kollision mit dem Boden
                if square['y'] + square['size']/2 >= HEIGHT:
                    square['y'] = HEIGHT - square['size']/2
                    
                    # Wenn die Geschwindigkeit sehr klein ist, lasse das Quadrat liegen
                    if abs(square['dy']) < 2:
                        square['is_resting'] = True
                        square['dx'] = 0
                        square['dy'] = 0
                        square['rotation_speed'] = 0  # Stoppe die Rotation
                    else:
                        # Bounce mit Energieverlust
                        square['dy'] = -square['dy'] * square['bounce_factor']
                        square['dx'] *= 0.8  # Reibung
                
                # Prüfe Kollision mit den Wänden
                if square['x'] - square['size']/2 <= 0:
                    square['x'] = square['size']/2
                    square['dx'] = abs(square['dx']) * square['bounce_factor']
                elif square['x'] + square['size']/2 >= WIDTH:
                    square['x'] = WIDTH - square['size']/2
                    square['dx'] = -abs(square['dx']) * square['bounce_factor']

        # Check collisions between balls
        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                balls[i].check_collision(balls[j], balls)

        # Überprüfe Kollisionen mit Hexagonen
        for ball in balls:
            for hexagon in hexagons:
                if hexagon.check_collision(ball):
                    # Entferne take_damage() - Bälle sollen nur abprallen, nicht beschädigt werden
                    pass

        # Draw everything
        screen.fill(BLACK)
        
        # Zeichne den animierten Hintergrund
        background.draw(screen)
        
        # Zeichne Hexagone
        for hexagon in hexagons:
            hexagon.draw(screen)

        # Draw trails
        for ball in balls:
            if not ball.is_exploding:
                for i, pos in enumerate(ball.trail):
                    alpha = int(255 * (i / ball.trail_length))
                    color = (*ball.color[:3], alpha)
                    
                    rect_width = ball.radius * 0.5
                    rect_height = ball.radius * 0.3 * (i / ball.trail_length)
                    
                    trail_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
                    pygame.draw.rect(trail_surface, color, (0, 0, rect_width, rect_height))
                    
                    screen.blit(trail_surface, (
                        pos[0] - rect_width/2,
                        pos[1] - rect_height/2
                    ))

        # Draw particles and falling squares
        for ball in balls:
            for particle in ball.particles:
                if particle.get('type') == 'shard':
                    # Zeichne Splitter mit Verblassen
                    alpha = int(255 * (particle['lifetime'] / 120))
                    color = (*particle['color'][:3], alpha)
                    
                    # Erstelle Surface für den Splitter
                    points = [(int(x), int(y)) for x, y in particle['points']]
                    
                    # Berechne Bounding Box für Surface
                    min_x = min(x for x, _ in points)
                    max_x = max(x for x, _ in points)
                    min_y = min(y for _, y in points)
                    max_y = max(y for _, y in points)
                    width = max_x - min_x + 2
                    height = max_y - min_y + 2
                    
                    if width > 0 and height > 0:
                        shard_surface = pygame.Surface((width, height), pygame.SRCALPHA)
                        # Verschiebe Punkte relativ zur Surface
                        adjusted_points = [(x - min_x, y - min_y) for x, y in points]
                        pygame.draw.polygon(shard_surface, color, adjusted_points)
                        screen.blit(shard_surface, (min_x, min_y))
                else:
                    # Normaler Partikel-Code für andere Partikeltypen
                    if particle.get('type') == 'falling_square':
                        # Fallende Quadrate haben keine Transparenz
                        color = particle['color']
                    else:
                        # Normale Partikel mit Verblassen
                        if particle['lifetime'] == float('inf'):
                            alpha = 255  # Volle Sichtbarkeit für unendliche Lebensdauer
                        else:
                            alpha = int(255 * (particle['lifetime'] / 20) * 1.5)
                        alpha = min(255, alpha)  # Nicht über 255 gehen
                        color = (*particle['color'][:3], alpha)
                    size = particle.get('size', 8)
                    particle_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                    # Zeichne ein Quadrat statt eines Kreises
                    pygame.draw.rect(particle_surface, color, (0, 0, size, size))
                    screen.blit(particle_surface, (particle['x'] - size//2, particle['y'] - size//2))
        
        # Zeichne fallende Quadrate
        for square in falling_squares:
            size = square['size']
            # Erstelle eine Surface für das rotierte Quadrat
            square_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            
            # Zeichne das Quadrat in der Mitte der Surface
            pygame.draw.rect(square_surface, square['color'], 
                           (size/2, size/2, size, size))
            
            # Rotiere die Surface
            rotated_surface = pygame.transform.rotate(square_surface, 
                                                   math.degrees(square['rotation']))
            
            # Berechne die Position für das rotierte Quadrat
            pos_x = square['x'] - rotated_surface.get_width()/2
            pos_y = square['y'] - rotated_surface.get_height()/2
            
            # Zeichne das rotierte Quadrat
            screen.blit(rotated_surface, (pos_x, pos_y))

        # Draw balls with damage visualization
        for ball in balls[:]:
            if not ball.is_exploding:
                damage_percentage = ball.damage / ball.health
                
                # Zeichne die äußere Hülle (Shell)
                shell_color = tuple(
                    min(255, int(c * 0.75))  # 75% der Originalfarbe (vorher 50%)
                    for c in ball.color
                )
                shell_radius = ball.radius + 6  # 6 Pixel größer als der Ball (vorher 4)
                shell_surface = pygame.Surface((shell_radius * 2, shell_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(shell_surface, (*shell_color, 150),  # Alpha auf 150 erhöht (vorher 100)
                                 (shell_radius, shell_radius), shell_radius)
                screen.blit(shell_surface, 
                          (int(ball.x - shell_radius), int(ball.y - shell_radius)))
                
                # Basis-Ball mit dunklerer Farbe bei mehr Schaden
                darkened_color = tuple(
                    max(0, int(c * (1 - damage_percentage * 0.5)))
                    for c in ball.color
                )
                pygame.draw.circle(screen, darkened_color, (int(ball.x), int(ball.y)), ball.radius)
                
                # Zeichne die fixierten Risse
                length = ball.radius * (0.5 + damage_percentage)
                for angle in ball.crack_angles:
                    end_x = ball.x + math.cos(angle) * length
                    end_y = ball.y + math.sin(angle) * length
                    
                    # Dickere Risse mit weißem Highlight
                    pygame.draw.line(screen, WHITE, 
                                   (int(ball.x), int(ball.y)),
                                   (int(end_x), int(end_y)), 1)
                    pygame.draw.line(screen, BLACK, 
                                   (int(ball.x), int(ball.y)),
                                   (int(end_x), int(end_y)), 3)

        # Zeige das Gewinner-Banner und Rangliste an
        if len(balls) == 1 and not balls[0].is_exploding:
            rankings.draw_winner_banner_and_rankings(screen, balls[0], eliminated_balls)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
