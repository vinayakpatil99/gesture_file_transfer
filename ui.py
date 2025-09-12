# --- ui.py (fixed) ---
import pygame

class Animation:
    def __init__(self, file_path, win_size=(640,480), target_pos=(540,380)):
        pygame.init()
        self.win_w, self.win_h = win_size
        self.screen = pygame.display.set_mode(win_size)
        pygame.display.set_caption("Gesture File Transfer - Ultra Pro")
        self.clock = pygame.time.Clock()
        self.file_image_orig = pygame.image.load(file_path)
        self.file_image_orig = pygame.transform.scale(self.file_image_orig, (80,80))
        self.hand_pos = None
        self.flying = False
        self.fly_start = None
        self.fly_end = target_pos  # <-- fix: accept target_pos
        self.fly_progress = 0
        self.current_size = 80
        self.angle = 0
        self.trail_points = []

    def start_grab(self, x, y):
        self.hand_pos = (x, y)
        self.trail_points = []

    def drop(self):
        if self.hand_pos:
            self.fly_start = self.hand_pos
            self.flying = True
            self.fly_progress = 0
            self.current_size = 80
            self.angle = 0
            self.trail_points = []

    def update(self, x, y):
        self.screen.fill((30,30,30))
        if x is not None and y is not None:
            pygame.draw.circle(self.screen, (0,255,0), (int(x), int(y)), 15)
        if x is not None and y is not None:
            self.hand_pos = (x, y)
        if self.flying and self.fly_start and self.fly_end:
            self.fly_progress += 0.03
            if self.fly_progress >= 1:
                self.fly_progress = 1
                self.flying = False
            fx = self.fly_start[0] + (self.fly_end[0]-self.fly_start[0])*self.fly_progress
            fy = self.fly_start[1] + (self.fly_end[1]-self.fly_start[1])*self.fly_progress
            size = 80 - int(50*self.fly_progress)
            self.current_size = max(size,1)
            self.angle += 10
            img = pygame.transform.rotate(pygame.transform.scale(self.file_image_orig, (self.current_size,self.current_size)), self.angle)
            self.trail_points.append((fx, fy))
            for idx, point in enumerate(self.trail_points[-10:]):
                alpha = int(255 * (idx+1)/10)
                trail_surf = pygame.Surface((self.current_size,self.current_size), pygame.SRCALPHA)
                trail_surf.blit(img, (0,0))
                trail_surf.set_alpha(alpha//2)
                self.screen.blit(trail_surf, (point[0]-self.current_size//2, point[1]-self.current_size//2))
            rect = img.get_rect(center=(fx, fy))
            self.screen.blit(img, rect.topleft)
        elif self.hand_pos and not self.flying:
            self.screen.blit(self.file_image_orig, (self.hand_pos[0]-40, self.hand_pos[1]-40))
        pygame.display.flip()
        self.clock.tick(60)

    def close(self):
        pygame.quit()