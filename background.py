import pygame
import random
import math
from typing import List, Tuple
from constants import COLORS

class Background:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # Berechne die gewünschte Anzahl von Punkten (wie vorher)
        desired_cols = self.width // 100  # Ungefähr ein Punkt alle 100 Pixel
        desired_rows = self.height // 100
        
        # Berechne die tatsächliche Gittergröße, um den gesamten Bildschirm zu füllen
        self.grid_size_x = self.width / desired_cols
        self.grid_size_y = self.height / desired_rows
        self.line_thickness = 1
        
        # Liste für Farbwechsel-Effekte
        self.color_change_effects = []
        
        # Erstelle ein Raster von Punkten
        self.points = []
        for y in range(desired_rows + 1):
            row = []
            for x in range(desired_cols + 1):
                # Berechne die exakte Position für jeden Punkt
                pos_x = x * self.grid_size_x
                pos_y = y * self.grid_size_y
                row.append({
                    'x': pos_x,
                    'y': pos_y,
                    'base_x': pos_x,
                    'base_y': pos_y,
                    'radius': random.randint(4, 10),
                    'offset': random.uniform(0, 2 * math.pi),
                    'color': (128, 128, 128),
                    'inner_color': random.choice(COLORS)
                })
            self.points.append(row)
    
    def update(self):
        # Aktualisiere die Position der Punkte für eine subtile Bewegung
        time = pygame.time.get_ticks() / 1000  # Zeit in Sekunden
        for row in self.points:
            for point in row:
                # Kreisförmige Bewegung mit bis zu 4 Pixeln
                point['x'] = point['base_x'] + math.cos(time + point['offset']) * 4
                point['y'] = point['base_y'] + math.sin(time + point['offset']) * 4
        
        # Aktualisiere Farbwechsel-Effekte
        for effect in self.color_change_effects[:]:
            effect['radius'] += effect['speed']
            effect['angle'] += effect['rotation_speed']
            effect['lifetime'] -= 1
            
            if effect['lifetime'] <= 0 or effect['radius'] >= effect['max_radius']:
                self.color_change_effects.remove(effect)
    
    def update_colors(self, active_balls, destroyed_ball_color=None):
        # Wenn keine Ballfarbe angegeben wurde, nichts tun
        if destroyed_ball_color is None:
            return
            
        # Hole die Farben der noch aktiven Bälle
        available_colors = [ball.color for ball in active_balls if not ball.is_exploding]
        if not available_colors:  # Wenn keine Farben verfügbar sind
            return
            
        # Aktualisiere nur die Punkte, die die gleiche Farbe wie der zerstörte Ball hatten
        for row in self.points:
            for point in row:
                if point['inner_color'] == destroyed_ball_color:
                    new_color = random.choice(available_colors)
                    old_color = point['inner_color']
                    point['inner_color'] = new_color
                    
                    # Erstelle Spiral-Effekt für diesen Punkt
                    num_particles = 24  # Anzahl der Partikel bleibt gleich
                    for i in range(num_particles):
                        angle = (i / num_particles) * 2 * math.pi
                        self.color_change_effects.append({
                            'x': point['x'],
                            'y': point['y'],
                            'angle': angle,
                            'radius': 0,
                            'speed': 1.5,  # Reduziert von 3 auf 1.5 für langsamere Bewegung
                            'rotation_speed': 0.15,  # Reduziert von 0.3 auf 0.15 für langsamere Rotation
                            'lifetime': 90,  # Verdoppelt von 45 auf 90 für längere Dauer
                            'max_radius': point['radius'] * 4,  # Erhöht von 3 auf 4 für größere Reichweite
                            'old_color': old_color,
                            'new_color': new_color
                        })
    
    def draw(self, screen):
        # Zeichne die Verbindungslinien
        for i, row in enumerate(self.points):
            for j, point in enumerate(row):
                # Zeichne horizontale Linien
                if j < len(row) - 1:
                    start_pos = (int(point['x']), int(point['y']))
                    end_pos = (int(row[j + 1]['x']), int(row[j + 1]['y']))
                    color = (30, 30, 30)  # Dunkelgrau
                    pygame.draw.line(screen, color, start_pos, end_pos, self.line_thickness)
                
                # Zeichne vertikale Linien
                if i < len(self.points) - 1:
                    start_pos = (int(point['x']), int(point['y']))
                    end_pos = (int(self.points[i + 1][j]['x']), int(self.points[i + 1][j]['y']))
                    pygame.draw.line(screen, color, start_pos, end_pos, self.line_thickness)
        
        # Zeichne die Punkte
        for row in self.points:
            for point in row:
                # Zeichne den äußeren grauen Punkt
                pygame.draw.circle(screen, point['color'], 
                                 (int(point['x']), int(point['y'])), 
                                 point['radius'])
                
                # Zeichne den inneren farbigen Punkt (2/3 so groß)
                inner_radius = int(point['radius'] * 2/3)  # Zwei Drittel der Größe
                pygame.draw.circle(screen, point['inner_color'],
                                 (int(point['x']), int(point['y'])),
                                 inner_radius)
        
        # Zeichne Farbwechsel-Effekte
        for effect in self.color_change_effects:
            # Berechne Farbübergang
            progress = effect['radius'] / effect['max_radius']
            color = tuple(
                int(effect['old_color'][i] * (1 - progress) + effect['new_color'][i] * progress)
                for i in range(3)
            )
            
            # Berechne Position der Spiralpartikel
            x = effect['x'] + math.cos(effect['angle']) * effect['radius']
            y = effect['y'] + math.sin(effect['angle']) * effect['radius']
            
            # Zeichne Spiralpartikel mit Verblassen
            alpha = int(255 * (effect['lifetime'] / 90))  # Angepasst an neue Lebensdauer
            particle_surface = pygame.Surface((5, 5), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*color, alpha), (2, 2), 2)
            screen.blit(particle_surface, (int(x) - 2, int(y) - 2))