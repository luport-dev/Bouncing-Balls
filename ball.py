import pygame
import random
import math
from typing import List, Tuple

# Import constants that the Ball class depends on
from constants import WIDTH, HEIGHT, BALL_SPEED

class Ball:
    def __init__(self, x: int, y: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.radius = 20
        self.color = color
        
        # Random direction with constant speed
        angle = random.uniform(0, 2 * math.pi)
        self.dx = BALL_SPEED * math.cos(angle)
        self.dy = BALL_SPEED * math.sin(angle)
        
        self.particles: List[dict] = []
        self.trail: List[Tuple[float, float]] = []
        self.trail_length = 20
        self.trail_gap = 5
        self.health = 10
        self.damage = 0
        self.damage_per_hit = 1  # 1 damage = 10% (since health = 10)
        self.crack_angles = []  # New variable for fixed crack positions
        self.is_exploding = False
        self.explosion_timer = 0
        self.explosion_duration = 120  # 2 seconds at 60 FPS
        self.survival_time = 0  # Time in frames

    def move(self):
        # If the ball is exploding, no movement
        if self.is_exploding:
            return
            
        trail_x = self.x - self.dx * self.trail_gap
        trail_y = self.y - self.dy * self.trail_gap
        self.trail.append((trail_x, trail_y))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)

        self.x += self.dx
        self.y += self.dy

        # Bounce off walls
        if self.x - self.radius <= 0 or self.x + self.radius >= WIDTH:
            self.dx *= -1
            self.create_particles()
        if self.y - self.radius <= 0 or self.y + self.radius >= HEIGHT:
            self.dy *= -1
            self.create_particles()

    def create_particles(self):
        # Reduce number of particles from 5 to 3
        for _ in range(3):
            bright_color = tuple(
                min(255, int(c + (255 - c) * 0.7))
                for c in self.color
            )
            particle = {
                'x': self.x,
                'y': self.y,
                'dx': random.uniform(-6, 6),
                'dy': random.uniform(-6, 6),
                'lifetime': 15,  # Reduce lifetime from 20 to 15
                'color': bright_color
            }
            self.particles.append(particle)

    def update_particles(self):
        for particle in self.particles[:]:
            if 'speed_decay' in particle:
                particle['dx'] *= particle['speed_decay']
                particle['dy'] *= particle['speed_decay']
            
            # Special treatment for falling squares
            if particle.get('type') == 'falling_square':
                if not particle['is_resting']:
                    # Add gravity
                    particle['dy'] += particle['gravity']
                    
                    # Move the square
                    particle['x'] += particle['dx']
                    particle['y'] += particle['dy']
                    
                    # Rotate the square
                    particle['rotation'] += particle['rotation_speed']
                    
                    # Check collision with the ground
                    if particle['y'] + particle['size']/2 >= HEIGHT:
                        particle['y'] = HEIGHT - particle['size']/2
                        
                        # If the speed is very small, let the square rest
                        if abs(particle['dy']) < 2:
                            particle['is_resting'] = True
                            particle['dx'] = 0
                            particle['dy'] = 0
                            particle['rotation_speed'] = 0  # Stop the rotation
                        else:
                            # Bounce with energy loss
                            particle['dy'] = -particle['dy'] * particle['bounce_factor']
                            particle['dx'] *= 0.8  # Friction
                    
                    # Check collision with the walls
                    if particle['x'] - particle['size']/2 <= 0:
                        particle['x'] = particle['size']/2
                        particle['dx'] = abs(particle['dx']) * particle['bounce_factor']
                    elif particle['x'] + particle['size']/2 >= WIDTH:
                        particle['x'] = WIDTH - particle['size']/2
                        particle['dx'] = -abs(particle['dx']) * particle['bounce_factor']
                continue  # Important: Continue here so that the rest of the particle logic is skipped
            
            # Special treatment for ball splitters
            if particle.get('type') == 'shard':
                # Move the splitter
                particle['center_x'] += particle['dx']
                particle['center_y'] += particle['dy']
                
                # Rotate the splitter
                particle['rotation'] += particle['rotation_speed']
                
                # Update the point positions based on rotation and position
                center_x, center_y = particle['center_x'], particle['center_y']
                original_points = particle['points']
                
                # Calculate new point positions after rotation
                new_points = []
                for px, py in original_points:
                    # Move point relative to the original center
                    dx = px - self.x
                    dy = py - self.y
                    
                    # Rotate
                    rot = particle['rotation']
                    new_x = dx * math.cos(rot) - dy * math.sin(rot)
                    new_y = dx * math.sin(rot) + dy * math.cos(rot)
                    
                    # Move to the current center
                    new_points.append((
                        center_x + new_x,
                        center_y + new_y
                    ))
                
                particle['points'] = new_points
                
                # Fade out the splitter
                particle['lifetime'] -= 1
                if particle['lifetime'] <= 0:
                    self.particles.remove(particle)
                continue
            
            # Normal particles
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['lifetime'] -= 1

            # Special effects for different particle types
            if 'pulse' in particle:
                # Pulsating size
                particle['size'] = particle.get('size', 8) * (
                    0.8 + 0.4 * math.sin(particle['pulse'] + particle['lifetime'] * 0.1)
                )
            
            if 'spiral' in particle:
                # Spiral movement
                particle['angle'] += 0.1
                particle['dx'] += math.cos(particle['angle']) * 0.2
                particle['dy'] += math.sin(particle['angle']) * 0.2
            
            if 'shockwave' in particle:
                # Expanding shockwave
                progress = 1 - (particle['lifetime'] / 60)
                particle['size'] = particle['max_size'] * progress

            # Remove only normal particles when their lifetime has expired
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)

    def take_damage(self):
        self.damage += self.damage_per_hit
        if self.damage >= self.health and not self.is_exploding:
            self.start_explosion()
            return False  # Ball is not yet removed
        # Add new fixed cracks
        new_cracks = int(12 * (1/self.health))  # 12 cracks / 10 health = ~1 new crack per hit
        for _ in range(new_cracks):
            self.crack_angles.append(random.uniform(0, 2 * math.pi))
        return False

    def start_explosion(self):
        self.is_exploding = True
        self.explosion_timer = self.explosion_duration
        self.explode()  # Start the explosion

    def update(self):
        if not self.is_exploding:
            self.survival_time += 1  # Increase the survival time
        if self.is_exploding:
            self.explosion_timer -= 1
            # Add new particles periodically during the explosion
            if self.explosion_timer % 20 == 0:  # New particles every 20 frames
                self.add_explosion_particles()
            return self.explosion_timer <= 0  # True when the explosion is over
        return False

    def explode(self):
        rainbow_colors = [
            (255, 0, 0),    # Red
            (255, 127, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 0, 255),  # Pink
        ]
        
        # Add falling squares
        num_squares = 15  # Number of falling squares
        for _ in range(num_squares):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 10)
            size = random.randint(5, 9)  # Increased from 4-8 to 5-9
            color = random.choice(rainbow_colors)
            
            particle = {
                'x': self.x,
                'y': self.y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed - 5,  # Initial upwards for arc effect
                'size': size,
                'color': color,
                'type': 'falling_square',
                'rotation': random.uniform(0, 2 * math.pi),
                'rotation_speed': random.uniform(-0.2, 0.2),
                'gravity': 0.5,
                'bounce_factor': 0.5,
                'is_resting': False,
                'lifetime': float('inf')  # Infinite lifetime
            }
            self.particles.append(particle)
            
        # Reduce number of splitters to 3
        num_shards = 3
        
        # Create irregular splitters
        for i in range(num_shards):
            angle = (i / num_shards) * 2 * math.pi
            next_angle = ((i + 1) / num_shards) * 2 * math.pi
            
            # Random intermediate points for more irregular shape
            mid_angle = (angle + next_angle) / 2
            rand_radius = self.radius * random.uniform(0.8, 1.2)
            
            points = [
                (self.x, self.y),
                (self.x + math.cos(angle) * self.radius,
                 self.y + math.sin(angle) * self.radius),
                (self.x + math.cos(mid_angle) * rand_radius,
                 self.y + math.sin(mid_angle) * rand_radius),
                (self.x + math.cos(next_angle) * self.radius,
                 self.y + math.sin(next_angle) * self.radius)
            ]
            
            speed = random.uniform(8, 12)
            rotation_speed = random.uniform(-0.3, 0.3)
            
            bright_color = tuple(
                min(255, int(c + (255 - c) * 0.3))
                for c in self.color
            )
            
            shard = {
                'points': points,
                'center_x': self.x,
                'center_y': self.y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'rotation': 0,
                'rotation_speed': rotation_speed,
                'color': bright_color,
                'lifetime': 80,  # Reduce lifetime
                'type': 'shard',
                'speed_decay': 0.99
            }
            self.particles.append(shard)

        # Reduce number of explosion particles
        num_particles = 80  # Reduced from 150
        for i in range(num_particles):
            angle = (i / num_particles) * 2 * math.pi
            speed = random.uniform(8, 15)
            
            color = random.choice(rainbow_colors)
            
            particle = {
                'x': self.x,
                'y': self.y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'lifetime': random.randint(60, 80),  # Reduced lifetime
                'color': color,
                'size': random.randint(1, 2),  # Size changed to 1-2 pixels
                'speed_decay': 0.97,
                'pulse': random.random() * math.pi
            }
            self.particles.append(particle)

        # Reduce number of spiral particles
        for i in range(30):  # Reduced from 60
            spiral_angle = (i / 15) * 4 * math.pi
            radius = i * 0.25
            speed = random.uniform(4, 6)
            
            base_color = rainbow_colors[i % len(rainbow_colors)]
            bright_color = tuple(
                min(255, int(c + (255 - c) * 0.8))
                for c in base_color
            )
            
            particle = {
                'x': self.x + math.cos(spiral_angle) * radius,
                'y': self.y + math.sin(spiral_angle) * radius,
                'dx': math.cos(spiral_angle) * speed,
                'dy': math.sin(spiral_angle) * speed,
                'lifetime': random.randint(60, 80),
                'color': bright_color,
                'size': random.randint(2, 3),  # Size changed to 2-3 pixels
                'speed_decay': 0.98,
                'spiral': True,
                'angle': spiral_angle
            }
            self.particles.append(particle)

        # Reduce number of shockwaves
        num_shockwave = 20  # Reduced from 40
        for i in range(num_shockwave):
            angle = (i / num_shockwave) * 2 * math.pi
            base_color = random.choice(rainbow_colors)
            bright_color = tuple(
                min(255, int(c + (255 - c) * 0.95))
                for c in base_color
            )
            
            particle = {
                'x': self.x,
                'y': self.y,
                'dx': math.cos(angle) * 1.5,
                'dy': math.sin(angle) * 1.5,
                'lifetime': 40,  # Reduced lifetime
                'color': bright_color,
                'size': random.randint(1, 3),  # Size remains 1-3 pixels
                'speed_decay': 0.99,
                'shockwave': True,
                'max_size': random.randint(1, 3)  # Maximum size remains 1-3 pixels
            }
            self.particles.append(particle)

    def add_explosion_particles(self):
        rainbow_colors = [
            (255, 0, 0),    # Red
            (255, 127, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 0, 255),  # Pink
        ]
        
        # Reduce number of additional explosion particles
        for i in range(10):  # Reduced from 20
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(8, 15)
            
            color = random.choice(rainbow_colors)
            
            particle = {
                'x': self.x,
                'y': self.y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'lifetime': random.randint(30, 40),  # Reduced lifetime
                'color': color,
                'size': random.randint(2, 3),  # Size changed to 2-3 pixels
                'speed_decay': 0.98,
                'pulse': random.random() * math.pi
            }
            self.particles.append(particle)

    def check_collision(self, other: 'Ball', active_balls: List['Ball']) -> bool:
        # If one of the balls is exploding, no collision
        if self.is_exploding or other.is_exploding:
            return False
            
        distance = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        if distance <= self.radius + other.radius:
            # Calculate collision response
            nx = (other.x - self.x) / distance
            ny = (other.y - self.y) / distance
            
            # Separate balls to prevent sticking
            overlap = (self.radius + other.radius - distance) / 2
            self.x -= overlap * nx
            self.y -= overlap * ny
            other.x += overlap * nx
            other.y += overlap * ny
            
            # Exchange velocities along the collision normal
            tx = -ny
            ty = nx
            
            dpTan1 = self.dx * tx + self.dy * ty
            dpTan2 = other.dx * tx + other.dy * ty
            
            dpNorm1 = self.dx * nx + self.dy * ny
            dpNorm2 = other.dx * nx + other.dy * ny
            
            self.dx = tx * dpTan1 + nx * dpNorm2
            self.dy = ty * dpTan1 + ny * dpNorm2
            other.dx = tx * dpTan2 + nx * dpNorm1
            other.dy = ty * dpTan2 + ny * dpNorm1
            
            # Normalize the speed after the collision
            speed1 = math.sqrt(self.dx**2 + self.dy**2)
            speed2 = math.sqrt(other.dx**2 + self.dy**2)
            
            if speed1 != 0:
                factor1 = BALL_SPEED / speed1
                self.dx *= factor1
                self.dy *= factor1
                
            if speed2 != 0:
                factor2 = BALL_SPEED / speed2
                other.dx *= factor2
                other.dy *= factor2
            
            # Count active balls
            num_active_balls = sum(1 for ball in active_balls if not ball.is_exploding)
            
            # If more than 2 balls, normal damage
            if num_active_balls > 2:
                self.take_damage()
                other.take_damage()
            # If exactly 2 balls
            elif num_active_balls == 2:
                # Only if both are critically damaged (10% life = 1 health point)
                if self.health - self.damage <= 1 and other.health - other.damage <= 1:
                    # Randomly select a ball to die
                    if random.choice([True, False]):
                        self.take_damage()
                        self.take_damage()  # Extra damage to ensure the ball dies
                    else:
                        other.take_damage()
                        other.take_damage()  # Extra damage to ensure the ball dies
                else:
                    # Normal damage if not both critically damaged
                    self.take_damage()
                    other.take_damage()
            
            self.create_particles()
            other.create_particles()
            return True
        return False