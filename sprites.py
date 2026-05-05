"""
Misty Moon Treasure Hunt - Sprite & Graphics Engine
Generates all pixel art sprites programmatically with animations and effects.
"""

import pygame
import math
import random


def create_wall_sprite(size):
    """Create a textured stone wall tile with depth and cracks."""
    surf = pygame.Surface((size, size))
    
    # base stone color with variation
    base_colors = [(75, 75, 95), (65, 68, 88), (80, 78, 100), (70, 72, 90)]
    
    # draw stone blocks pattern
    block_h = size // 3
    for row in range(3):
        offset = (size // 4) if row % 2 == 1 else 0
        block_w = size // 2
        for col in range(-1, 3):
            bx = col * block_w + offset
            by = row * block_h
            color = random.choice(base_colors)
            rect = pygame.Rect(bx + 1, by + 1, block_w - 2, block_h - 2)
            pygame.draw.rect(surf, color, rect)
            
            # highlight (top-left edge)
            highlight = tuple(min(c + 20, 255) for c in color)
            pygame.draw.line(surf, highlight, (bx + 1, by + 1), (bx + block_w - 2, by + 1))
            pygame.draw.line(surf, highlight, (bx + 1, by + 1), (bx + 1, by + block_h - 2))
            
            # shadow (bottom-right edge)
            shadow = tuple(max(c - 25, 0) for c in color)
            pygame.draw.line(surf, shadow, (bx + 1, by + block_h - 2), (bx + block_w - 2, by + block_h - 2))
            pygame.draw.line(surf, shadow, (bx + block_w - 2, by + 1), (bx + block_w - 2, by + block_h - 2))
    
    # mortar lines
    mortar = (40, 40, 55)
    for row in range(1, 3):
        pygame.draw.line(surf, mortar, (0, row * block_h), (size, row * block_h))
    
    # random cracks/noise
    for _ in range(8):
        cx = random.randint(2, size - 3)
        cy = random.randint(2, size - 3)
        crack_color = (50, 50, 65)
        surf.set_at((cx, cy), crack_color)
        if random.random() > 0.5:
            surf.set_at((cx + 1, cy), crack_color)
    
    return surf


def create_floor_sprite(size, variant=0):
    """Create a stone floor tile with subtle texture."""
    surf = pygame.Surface((size, size))
    
    # base floor
    base = (35 + variant * 3, 35 + variant * 2, 55 + variant * 3)
    surf.fill(base)
    
    # subtle tile pattern
    mid = size // 2
    line_color = (base[0] - 5, base[1] - 5, base[2] - 5)
    pygame.draw.line(surf, line_color, (0, 0), (size, 0))
    pygame.draw.line(surf, line_color, (0, 0), (0, size))
    
    # tiny noise dots
    for _ in range(6):
        nx = random.randint(2, size - 3)
        ny = random.randint(2, size - 3)
        noise_c = (base[0] + random.randint(-8, 8),
                   base[1] + random.randint(-8, 8),
                   base[2] + random.randint(-8, 8))
        noise_c = tuple(max(0, min(255, c)) for c in noise_c)
        surf.set_at((nx, ny), noise_c)
    
    return surf


def create_explored_floor_sprite(size, variant=0):
    """Floor tile that has been explored (slightly lighter)."""
    surf = create_floor_sprite(size, variant)
    # apply slight blue tint overlay
    overlay = pygame.Surface((size, size), pygame.SRCALPHA)
    overlay.fill((60, 80, 120, 25))
    surf.blit(overlay, (0, 0))
    return surf


def create_treasure_sprite(size, frame=0):
    """Create an animated treasure chest sprite."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    cx, cy = size // 2, size // 2 + 2
    w, h = size - 12, size - 16
    
    # glow effect (pulsating)
    glow_r = int(size * 0.6 + math.sin(frame * 0.15) * 4)
    glow_alpha = int(40 + math.sin(frame * 0.15) * 20)
    glow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (255, 200, 50, glow_alpha), (cx, cy), glow_r)
    surf.blit(glow_surf, (0, 0))
    
    # chest body
    body_rect = pygame.Rect(cx - w // 2, cy - h // 4, w, h // 2 + 2)
    pygame.draw.rect(surf, (139, 90, 43), body_rect, border_radius=2)
    pygame.draw.rect(surf, (120, 75, 35), body_rect, 2, border_radius=2)
    
    # chest lid
    lid_rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h // 4 + 2)
    pygame.draw.rect(surf, (160, 110, 55), lid_rect, border_radius=2)
    pygame.draw.rect(surf, (130, 85, 40), lid_rect, 2, border_radius=2)
    
    # metal bands
    band_color = (200, 180, 80)
    pygame.draw.rect(surf, band_color, (cx - 3, cy - h // 2, 6, h // 2 + h // 4 + 2), border_radius=1)
    
    # lock / keyhole
    pygame.draw.circle(surf, (220, 200, 100), (cx, cy - 1), 3)
    pygame.draw.circle(surf, (180, 160, 60), (cx, cy - 1), 3, 1)
    
    # sparkles
    sparkle_offsets = [(w // 3, -h // 3), (-w // 4, -h // 4), (w // 4, -h // 2.5)]
    for i, (sx, sy) in enumerate(sparkle_offsets):
        sparkle_phase = frame * 0.2 + i * 2.0
        sparkle_alpha = int(abs(math.sin(sparkle_phase)) * 200)
        sparkle_size = int(1 + abs(math.sin(sparkle_phase)) * 2)
        if sparkle_alpha > 50:
            sc = (255, 255, 200, sparkle_alpha)
            sparkle_surf = pygame.Surface((sparkle_size * 2 + 1, sparkle_size * 2 + 1), pygame.SRCALPHA)
            pygame.draw.circle(sparkle_surf, sc, (sparkle_size, sparkle_size), sparkle_size)
            surf.blit(sparkle_surf, (int(cx + sx - sparkle_size), int(cy + sy - sparkle_size)))
    
    return surf


def create_agent_sprite(size, frame=0, direction=(1, 0)):
    """Create an animated agent (explorer) sprite."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    
    # body bob animation
    bob = int(math.sin(frame * 0.4) * 1.5)
    
    # body (cloak)
    body_color = (30, 140, 220)
    body_dark = (20, 100, 170)
    body_points = [
        (cx - 8, cy + 10 + bob),
        (cx - 10, cy + 2 + bob),
        (cx - 6, cy - 6 + bob),
        (cx + 6, cy - 6 + bob),
        (cx + 10, cy + 2 + bob),
        (cx + 8, cy + 10 + bob),
    ]
    pygame.draw.polygon(surf, body_color, body_points)
    pygame.draw.polygon(surf, body_dark, body_points, 2)
    
    # head
    head_color = (240, 210, 170)
    pygame.draw.circle(surf, head_color, (cx, cy - 8 + bob), 6)
    pygame.draw.circle(surf, (200, 170, 130), (cx, cy - 8 + bob), 6, 1)
    
    # eyes (direction-aware)
    eye_offset = 0
    if direction[0] > 0:
        eye_offset = 1
    elif direction[0] < 0:
        eye_offset = -1
    pygame.draw.circle(surf, (30, 30, 50), (cx - 2 + eye_offset, cy - 9 + bob), 1)
    pygame.draw.circle(surf, (30, 30, 50), (cx + 2 + eye_offset, cy - 9 + bob), 1)
    
    # hat / hood
    hat_color = (25, 110, 190)
    hat_points = [
        (cx - 7, cy - 11 + bob),
        (cx, cy - 18 + bob),
        (cx + 7, cy - 11 + bob),
    ]
    pygame.draw.polygon(surf, hat_color, hat_points)
    pygame.draw.polygon(surf, (20, 90, 160), hat_points, 1)
    
    # lantern glow
    lantern_x = cx + 9
    lantern_y = cy - 2 + bob
    glow_r = int(5 + math.sin(frame * 0.3) * 2)
    glow_surf = pygame.Surface((glow_r * 4, glow_r * 4), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (255, 220, 100, 60), (glow_r * 2, glow_r * 2), glow_r * 2)
    pygame.draw.circle(glow_surf, (255, 240, 150, 100), (glow_r * 2, glow_r * 2), glow_r)
    surf.blit(glow_surf, (lantern_x - glow_r * 2, lantern_y - glow_r * 2))
    # lantern body
    pygame.draw.rect(surf, (200, 180, 60), (lantern_x - 2, lantern_y - 3, 4, 5))
    pygame.draw.circle(surf, (255, 230, 120), (lantern_x, lantern_y - 1), 2)
    
    return surf


def create_guard_sprite(size, frame=0):
    """Create an animated guard sprite (ghostly sentinel)."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    
    # ghost bob
    bob = int(math.sin(frame * 0.3 + 1.0) * 2)
    
    # danger glow
    glow_r = int(size * 0.45 + math.sin(frame * 0.2) * 3)
    glow_alpha = int(30 + math.sin(frame * 0.2) * 15)
    glow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (255, 50, 50, glow_alpha), (cx, cy + bob), glow_r)
    surf.blit(glow_surf, (0, 0))
    
    # body (ghostly shape)
    body_color = (200, 50, 60)
    body_dark = (160, 30, 40)
    
    # wavy bottom
    points = [(cx - 9, cy - 4 + bob)]
    points.append((cx - 10, cy + 8 + bob))
    for i in range(5):
        wave_x = cx - 10 + i * 5
        wave_y = cy + 10 + bob + (3 if i % 2 == 0 else 0)
        points.append((wave_x, wave_y))
    points.append((cx + 10, cy + 8 + bob))
    points.append((cx + 9, cy - 4 + bob))
    
    # top dome
    top_points = []
    for angle in range(180, 361, 15):
        rad = math.radians(angle)
        px = cx + int(10 * math.cos(rad))
        py = cy - 4 + bob + int(10 * math.sin(rad))
        top_points.append((px, py))
    
    all_points = top_points + points[1:-1]
    pygame.draw.polygon(surf, body_color, all_points)
    pygame.draw.polygon(surf, body_dark, all_points, 2)
    
    # eyes (menacing)
    eye_white = (255, 255, 200)
    pygame.draw.ellipse(surf, eye_white, (cx - 6, cy - 7 + bob, 5, 4))
    pygame.draw.ellipse(surf, eye_white, (cx + 1, cy - 7 + bob, 5, 4))
    # pupils
    pygame.draw.circle(surf, (80, 0, 0), (cx - 4, cy - 5 + bob), 1)
    pygame.draw.circle(surf, (80, 0, 0), (cx + 3, cy - 5 + bob), 1)
    
    return surf


def create_start_sprite(size):
    """Create the start position marker."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # green portal-like circle
    cx, cy = size // 2, size // 2
    
    # floor base
    floor = create_floor_sprite(size)
    surf.blit(floor, (0, 0))
    
    # glowing circle
    for r in range(12, 3, -1):
        alpha = int(60 - r * 4)
        color = (80, 255, 160, max(alpha, 10))
        glow = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(glow, color, (cx, cy), r)
        surf.blit(glow, (0, 0))
    
    # arrow pointing down-right
    pygame.draw.polygon(surf, (200, 255, 220), [
        (cx - 4, cy - 4), (cx + 4, cy), (cx - 4, cy + 4)
    ])
    
    return surf


def create_fog_sprite(size):
    """Create a fog tile with subtle swirl texture."""
    surf = pygame.Surface((size, size))
    surf.fill((8, 8, 18))
    
    # subtle swirl noise
    for _ in range(15):
        nx = random.randint(0, size - 1)
        ny = random.randint(0, size - 1)
        c = random.randint(5, 20)
        surf.set_at((nx, ny), (c, c, c + 5))
    
    # tiny star dots
    if random.random() > 0.6:
        sx = random.randint(3, size - 4)
        sy = random.randint(3, size - 4)
        star_c = random.randint(40, 80)
        surf.set_at((sx, sy), (star_c, star_c, star_c + 20))
    
    return surf


def create_path_marker(size, frame=0):
    """Create a glowing path indicator."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    
    alpha = int(60 + math.sin(frame * 0.2) * 30)
    r = 4 + int(math.sin(frame * 0.15) * 1)
    
    pygame.draw.circle(surf, (80, 220, 140, alpha), (cx, cy), r)
    pygame.draw.circle(surf, (120, 255, 180, alpha + 30), (cx, cy), r - 2)
    
    return surf


# ============================================================
# Particle System
# ============================================================

class Particle:
    """A single particle for visual effects."""
    
    def __init__(self, x, y, color, life=30, vx=0, vy=0, size=2, fade=True):
        self.x = x
        self.y = y
        self.color = color
        self.life = life
        self.max_life = life
        self.vx = vx
        self.vy = vy
        self.size = size
        self.fade = fade
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.02  # slight gravity
        self.life -= 1
    
    def draw(self, screen):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.max_life)) if self.fade else 200
        r = max(1, int(self.size * (self.life / self.max_life)))
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        c = (*self.color[:3], min(alpha, 255))
        pygame.draw.circle(s, c, (r, r), r)
        screen.blit(s, (int(self.x - r), int(self.y - r)))
    
    def alive(self):
        return self.life > 0


class ParticleSystem:
    """Manages collections of particles."""
    
    def __init__(self):
        self.particles = []
    
    def emit_sparkle(self, x, y, count=5):
        """Emit sparkle particles (for treasure)."""
        for _ in range(count):
            vx = random.uniform(-1.5, 1.5)
            vy = random.uniform(-2.5, -0.5)
            color = random.choice([
                (255, 215, 50), (255, 240, 100), (255, 200, 80), (255, 255, 180)
            ])
            life = random.randint(15, 35)
            size = random.uniform(1.5, 3)
            self.particles.append(Particle(x, y, color, life, vx, vy, size))
    
    def emit_footstep(self, x, y):
        """Emit dust particles when agent moves."""
        for _ in range(3):
            vx = random.uniform(-0.5, 0.5)
            vy = random.uniform(-0.3, 0.3)
            color = (80, 80, 100)
            life = random.randint(8, 15)
            self.particles.append(Particle(x, y + 5, color, life, vx, vy, 1.5))
    
    def emit_danger(self, x, y):
        """Emit red particles for guard warning."""
        for _ in range(4):
            vx = random.uniform(-1, 1)
            vy = random.uniform(-1, 1)
            color = (255, 60, 60)
            life = random.randint(10, 20)
            self.particles.append(Particle(x, y, color, life, vx, vy, 2))
    
    def emit_victory(self, x, y, count=30):
        """Big sparkle burst for victory."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = random.choice([
                (255, 215, 50), (255, 100, 100), (100, 255, 100),
                (100, 200, 255), (255, 255, 255), (255, 180, 50)
            ])
            life = random.randint(20, 50)
            size = random.uniform(2, 4)
            self.particles.append(Particle(x, y, color, life, vx, vy, size))
    
    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive()]
    
    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)


# ============================================================
# Sprite Cache (pre-generate and cache sprites)
# ============================================================

class SpriteCache:
    """Pre-generates and caches all sprites for performance."""
    
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.wall_sprites = [create_wall_sprite(cell_size) for _ in range(6)]
        self.floor_sprites = [create_floor_sprite(cell_size, i % 4) for i in range(8)]
        self.explored_sprites = [create_explored_floor_sprite(cell_size, i % 4) for i in range(4)]
        self.fog_sprites = [create_fog_sprite(cell_size) for _ in range(10)]
        self.start_sprite = create_start_sprite(cell_size)
        
        # animated sprites are generated per-frame
        self._treasure_cache = {}
        self._agent_cache = {}
        self._guard_cache = {}
        self._path_cache = {}
    
    def get_wall(self, x, y):
        idx = (x * 7 + y * 13) % len(self.wall_sprites)
        return self.wall_sprites[idx]
    
    def get_floor(self, x, y):
        idx = (x * 3 + y * 7) % len(self.floor_sprites)
        return self.floor_sprites[idx]
    
    def get_explored_floor(self, x, y):
        idx = (x * 3 + y * 7) % len(self.explored_sprites)
        return self.explored_sprites[idx]
    
    def get_fog(self, x, y):
        idx = (x * 11 + y * 17) % len(self.fog_sprites)
        return self.fog_sprites[idx]
    
    def get_treasure(self, frame):
        key = frame % 60
        if key not in self._treasure_cache:
            self._treasure_cache[key] = create_treasure_sprite(self.cell_size, frame)
        return self._treasure_cache[key]
    
    def get_agent(self, frame, direction=(1, 0)):
        key = (frame % 30, direction)
        if key not in self._agent_cache:
            self._agent_cache[key] = create_agent_sprite(self.cell_size, frame, direction)
        return self._agent_cache[key]
    
    def get_guard(self, frame):
        key = frame % 40
        if key not in self._guard_cache:
            self._guard_cache[key] = create_guard_sprite(self.cell_size, frame)
        return self._guard_cache[key]
    
    def get_path_marker(self, frame):
        key = frame % 40
        if key not in self._path_cache:
            self._path_cache[key] = create_path_marker(self.cell_size, frame)
        return self._path_cache[key]
