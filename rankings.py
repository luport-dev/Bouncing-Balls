import pygame

class Rankings:
    def __init__(self, width, height, white):
        self.WIDTH = width
        self.HEIGHT = height
        self.WHITE = white
        self.color_names = {
            (255, 0, 0): "Red",      # Rot
            (0, 255, 0): "Green",    # Grün
            (0, 0, 255): "Blue",     # Blau
            (255, 255, 0): "Yellow", # Gelb
            (255, 0, 255): "Pink",   # Magenta
            (0, 255, 255): "Cyan"    # Cyan
        }

    def draw_winner_banner_and_rankings(self, screen, winner, eliminated_balls):
        # Erstelle Fonts
        title_font = pygame.font.Font(None, 74)  # Größerer Font für den Titel
        ranking_font = pygame.font.Font(None, 36)  # Kleinerer Font für die Rangliste
        
        # Banner-Titel
        title_text = "Ranking"
        title_surface = title_font.render(title_text, True, self.WHITE)
        
        # Erstelle die Kopfzeile für die Tabelle
        header_rank = ranking_font.render("Rank", True, self.WHITE)
        header_ball = ranking_font.render("Ball", True, self.WHITE)
        header_time = ranking_font.render("Time", True, self.WHITE)
        
        # Erstelle die Rangliste
        ranking_lines = []
        
        # Füge den Gewinner als ersten Eintrag hinzu
        winner_name = self.color_names.get(winner.color, "Unknown")
        rank_text = "1.".ljust(8)
        name_text = f"{winner_name}".ljust(8)
        
        # Erstelle drei separate Surfaces für den Gewinner
        rank_surface = ranking_font.render(rank_text, True, winner.color)
        name_surface = ranking_font.render(name_text, True, winner.color)
        winner_crown = ranking_font.render("Survivor", True, winner.color)  # Füge "Survivor" statt Zeit hinzu
        
        ranking_lines.append((rank_surface, name_surface, winner_crown))
        
        # Sortiere eliminierte Bälle nach Überlebenszeit
        sorted_eliminated = sorted(eliminated_balls, key=lambda b: b.survival_time, reverse=True)
        
        # Füge die restlichen Bälle hinzu
        for i, ball in enumerate(sorted_eliminated, 2):
            color_name = self.color_names.get(ball.color, "Unknown")
            seconds = ball.survival_time / 60
            
            # Formatiere den Text in Spalten
            rank_text = f"{i}.".ljust(8)
            name_text = f"{color_name}".ljust(8)
            time_text = f"{seconds:.1f}s"
            
            # Erstelle drei separate Surfaces
            rank_surface = ranking_font.render(rank_text, True, ball.color)
            name_surface = ranking_font.render(name_text, True, ball.color)
            time_surface = ranking_font.render(time_text, True, ball.color)
            
            ranking_lines.append((rank_surface, name_surface, time_surface))
        
        # Berechne Gesamthöhe des Banners
        padding = 20
        line_spacing = 15
        header_spacing = 25
        
        total_height = (padding * 2 + 
                       title_surface.get_height() + 
                       line_spacing * 2 +
                       header_spacing +
                       len(ranking_lines) * (ranking_font.get_height() + line_spacing))
        
        # Finde maximale Breite
        max_width = max(
            title_surface.get_width(),
            header_spacing + padding * 2,
            400  # Minimale Breite für die Tabelle
        ) + padding * 2
        
        # Erstelle Banner-Surface
        banner = pygame.Surface((max_width, total_height))
        banner.fill((40, 40, 40))  # Dunkelgrauer Hintergrund
        
        # Zeichne weißen Rahmen
        pygame.draw.rect(banner, self.WHITE, (0, 0, max_width, total_height), 2)
        
        # Platziere Titel
        y_pos = padding
        x_pos = (max_width - title_surface.get_width()) // 2
        banner.blit(title_surface, (x_pos, y_pos))
        
        # Platziere Header
        y_pos += title_surface.get_height() + line_spacing * 2
        x_pos_rank = padding * 2
        x_pos_ball = x_pos_rank + max_width * 0.3  # 30% für Rang
        x_pos_time = x_pos_ball + max_width * 0.3  # 30% für Ball, Rest für Zeit
        
        banner.blit(header_rank, (x_pos_rank, y_pos))
        banner.blit(header_ball, (x_pos_ball, y_pos))
        banner.blit(header_time, (x_pos_time, y_pos))
        
        # Zeichne Trennlinie unter der Kopfzeile
        y_pos += header_spacing
        pygame.draw.line(banner, self.WHITE, 
                        (padding, y_pos), 
                        (max_width - padding, y_pos), 1)
        
        # Platziere Rangliste
        y_pos += header_spacing
        
        # Berechne die Spaltenbreiten
        rank_width = max_width * 0.3  # 30% der Gesamtbreite für Rang
        ball_width = max_width * 0.3  # 30% der Gesamtbreite für Ballname
        time_width = max_width * 0.4  # 40% der Gesamtbreite für Zeit
        
        for rank_surface, name_surface, time_surface in ranking_lines:
            # Spaltenposition für jedes Element
            x_pos_rank = padding * 2
            x_pos_name = x_pos_rank + rank_width
            x_pos_time = x_pos_name + ball_width
            
            banner.blit(rank_surface, (x_pos_rank, y_pos))
            banner.blit(name_surface, (x_pos_name, y_pos))
            banner.blit(time_surface, (x_pos_time, y_pos))
            
            y_pos += ranking_font.get_height() + line_spacing
        
        # Platziere Banner in der Mitte des Bildschirms
        screen.blit(banner,
                   ((self.WIDTH - max_width) // 2,
                    (self.HEIGHT - total_height) // 2))
