import pygame
import random
import math
from ball import Ball
from typing import List, Tuple
from constants import WHITE, BALL_SPEED

class Hexagon:
    def __init__(self, x: int, y: int, size: int):
        self.x = x
        self.y = y
        self.size = size
        self.base_color = (128, 128, 128)  # Basis-Grau
        self.glow_color = (180, 180, 180)  # Helleres Grau für den Leuchteffekt
        self.inner_color = (100, 100, 100)  # Dunkleres Grau für den inneren Ring
        self.particles: List[dict] = []
        self.rotation = 0  # Aktuelle Rotation in Grad
        self.rotation_speed = random.uniform(0.25, 0.75)  # Rotationsgeschwindigkeit
        self.pulse_offset = random.uniform(0, 2 * math.pi)  # Zufälliger Start für die Pulsierung
        self.pulse = 1.0  # Initialize pulse with default value
        
    def update(self):
        # Aktualisiere Rotation
        self.rotation += self.rotation_speed
        if self.rotation >= 360:
            self.rotation -= 360
            
        # Berechne Pulsierung (0.9 bis 1.1)
        time = pygame.time.get_ticks() / 1000  # Zeit in Sekunden
        self.pulse = 1 + 0.1 * math.sin(time * 2 + self.pulse_offset)

    def get_corners(self, size_factor=1.0) -> List[Tuple[float, float]]:
        # Berechne die Eckpunkte des rotierten Hexagons
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        corners = []
        
        for i in range(6):  # 6 Ecken für ein Hexagon
            angle = math.radians(60 * i + self.rotation)  # 60 Grad zwischen den Ecken
            # Verwende size direkt als Radius, mit Pulsierung
            x = center_x + self.size * size_factor * math.cos(angle) * self.pulse
            y = center_y + self.size * size_factor * math.sin(angle) * self.pulse
            corners.append((x, y))
        
        return corners

    def get_inner_corners(self) -> List[Tuple[float, float]]:
        # Berechne die Eckpunkte des inneren Hexagons (50% der Größe des äußeren)
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        corners = []
        
        for i in range(6):  # 6 Ecken für ein Hexagon
            angle = math.radians(60 * i + self.rotation)  # 60 Grad zwischen den Ecken
            # Innerer Ring ist 50% der Größe des äußeren
            x = center_x + self.size * 0.5 * math.cos(angle) * self.pulse
            y = center_y + self.size * 0.5 * math.sin(angle) * self.pulse
            corners.append((x, y))
        
        return corners

    def draw(self, screen):
        # Zeichne den äußeren Leuchteffekt
        glow_corners = self.get_corners(1.1)  # 10% größer
        glow_surface = pygame.Surface((self.size * 2.2, self.size * 2.2), pygame.SRCALPHA)
        pygame.draw.polygon(glow_surface, (*self.glow_color, 30), 
                          [(x - self.x + self.size * 0.1, y - self.y + self.size * 0.1) 
                           for x, y in glow_corners])
        screen.blit(glow_surface, (self.x - self.size * 0.1, self.y - self.size * 0.1))

        # Zeichne das Haupthexagon
        outer_corners = self.get_corners()
        pygame.draw.polygon(screen, self.base_color, outer_corners)
        
        # Zeichne den inneren Ring
        inner_corners = self.get_inner_corners()
        pygame.draw.polygon(screen, self.inner_color, inner_corners, 2)  # Nur Umriss
        
        # Verbinde die Ecken des inneren und äußeren Rings
        for outer, inner in zip(outer_corners, inner_corners):
            pygame.draw.line(screen, self.inner_color, outer, inner, 2)
        
        # Zeichne die äußere Umrandung
        pygame.draw.polygon(screen, WHITE, outer_corners, 2)

    def check_collision(self, ball: 'Ball') -> bool:
        # Berechne den Mittelpunkt des Hexagons
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        
        # Berechne die Distanz zwischen Ball und Hexagon-Zentrum
        dx = ball.x - center_x
        dy = ball.y - center_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Grobe Kollisionsprüfung mit umgebendem Kreis
        if distance > self.size + ball.radius:
            return False
            
        # Genaue Kollisionsprüfung mit den Kanten
        corners = self.get_corners()
        for i in range(6):
            p1 = corners[i]
            p2 = corners[(i + 1) % 6]
            
            # Berechne den nächsten Punkt auf der Linie zum Ball
            line_vec_x = p2[0] - p1[0]
            line_vec_y = p2[1] - p1[1]
            line_len = math.sqrt(line_vec_x*line_vec_x + line_vec_y*line_vec_y)
            
            if line_len == 0:
                continue
                
            # Normalisiere den Vektor
            line_vec_x /= line_len
            line_vec_y /= line_len
            
            # Relative Position des Balls zur Linie
            rel_x = ball.x - p1[0]
            rel_y = ball.y - p1[1]
            
            # Projiziere auf die Linie
            proj = rel_x*line_vec_x + rel_y*line_vec_y
            proj = max(0, min(line_len, proj))
            
            # Nächster Punkt auf der Linie
            closest_x = p1[0] + proj * line_vec_x
            closest_y = p1[1] + proj * line_vec_y
            
            # Distanz zum nächsten Punkt
            dx = ball.x - closest_x
            dy = ball.y - closest_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance <= ball.radius:
                # Kollision gefunden - berechne Normalenvektor
                if distance == 0:
                    nx = -line_vec_y
                    ny = line_vec_x
                else:
                    nx = dx / distance
                    ny = dy / distance
                
                # Verschiebe Ball aus dem Hexagon
                overlap = ball.radius - distance
                ball.x += overlap * nx
                ball.y += overlap * ny
                
                # Reflektiere Geschwindigkeit
                dot_product = (ball.dx * nx + ball.dy * ny) * 2
                ball.dx -= dot_product * nx
                ball.dy -= dot_product * ny
                
                # Normalisiere Geschwindigkeit
                speed = math.sqrt(ball.dx**2 + ball.dy**2)
                if speed != 0:
                    factor = BALL_SPEED / speed
                    ball.dx *= factor
                    ball.dy *= factor
                
                # Erzeuge Partikel
                ball.create_particles()
                return True
        
        return False