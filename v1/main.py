import pygame
import sys
import math
import random

def load_image(filename, size = None, flip = None):
    try:
        image = pygame.image.load(filename).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        if flip:
            image = pygame.transform.flip(image, True, False)
        return image
    except (pygame.error, FileNotFoundError):
        print(f"Could not load image: {filename}")
        # Create a placeholder colored rectangle if image fails to load
        placeholder = pygame.Surface((64, 64))
        placeholder.fill(RED if "face1" in filename else GREEN)
        return placeholder
    
def preload_heart_images():
    """Pre-load and cache heart images at different sizes for performance"""
    global HEART_CACHE
    
    # Load base heart image once
    try:
        heart = pygame.image.load('first_pygame/heart.png').convert_alpha()
        
        # Pre-scale to common sizes used by particles
        sizes = [20, 25, 30, 35, 40, 45]
        for size in sizes:
            HEART_CACHE[size] = pygame.transform.scale(heart, (size, size))
            
    except (pygame.error, FileNotFoundError):
        print("Could not load heart image, using rectangles instead")
        # Fallback to colored rectangles
        for size in [20, 25, 30, 35, 40, 45]:
            heart_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            heart_surface.fill((255, 182, 203, 255))  # Pink rectangle
            HEART_CACHE[size] = heart_surface

def get_cached_heart(size):
    """Get a cached heart image of the specified size"""
    # Find the closest cached size
    available_sizes = list(HEART_CACHE.keys())
    if not available_sizes:
        return None
        
    closest_size = min(available_sizes, key=lambda x: abs(x - size))
    
    # If exact match, return it
    if closest_size == size:
        return HEART_CACHE[closest_size]
    
    # If no exact match and difference is small, return closest
    if abs(closest_size - size) <= 5:
        return HEART_CACHE[closest_size]
    
    # For larger differences, scale the closest one (but cache it for future use)
    if size not in HEART_CACHE:
        HEART_CACHE[size] = pygame.transform.scale(HEART_CACHE[closest_size], (size, size))
    
    return HEART_CACHE[size]
    
def start_flip_animation(face_anim, current_time, text = None):
    """Start a bounce animation for flipping"""
    if not face_anim['is_animating']:
        face_anim['is_animating'] = True
        face_anim['start_time'] = current_time
        face_anim['start_scale'] = 1.0
        face_anim['target_scale'] = 1.2  # Slightly larger during bounce
        face_anim['bounce_height'] = 0
        face_anim['bounce_amp'] = 50  # px
        face_anim['flipped'] = not face_anim['flipped']
        face_anim['text'] = text

def update_animation(face_anim, current_time):
    """Update animation state and return scale factor and vertical offset"""
    if not face_anim['is_animating']:
        return 1.0, 0
    
    elapsed = current_time - face_anim['start_time']
    progress = min(elapsed / face_anim['duration'], 1.0)
    
    if progress >= 1.0:
        face_anim['is_animating'] = False
        return 1.0, 0
    
    # Use bounce easing for scale
    bounce_progress = easeOutBounce(progress)
    scale = 1.0 + (face_anim['target_scale'] - 1.0) * (1.0 - bounce_progress)
    
    # Add vertical bounce using sine wave for more natural movement
    bounce_height = math.sin(progress * math.pi) * face_anim['bounce_amp']  # Max x pixels up
    
    return scale, -bounce_height

def apply_animation_transform(original_img, scale, vertical_offset, is_flipped):
    """Apply scale and position transformations to image"""
    # Apply flip if needed
    img = original_img
    if is_flipped:
        img = pygame.transform.flip(img, True, False)
    
    # Apply scale
    if scale != 1.0:
        new_width = int(img.get_width() * scale)
        new_height = int(img.get_height() * scale)
        img = pygame.transform.scale(img, (new_width, new_height))
    
    return img, vertical_offset

def easeOutBounce(t):
    """Bounce easing function for smooth bounce animation"""
    if t < 1/2.75:
        return 7.5625 * t * t
    elif t < 2/2.75:
        t -= 1.5/2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5/2.75:
        t -= 2.25/2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625/2.75
        return 7.5625 * t * t + 0.984375

def easeOutElastic(t):
    """Elastic easing function for a more playful bounce"""
    if t == 0:
        return 0
    if t == 1:
        return 1
    p = 0.3
    s = p / 4
    return (2 ** (-10 * t)) * math.sin((t - s) * (2 * math.pi) / p) + 1

class BaseParticle:
    """Base class for all particles with common physics"""
    def __init__(self, x, y, v_x, v_y, color, size, life_time):
        self.x = x
        self.y = y
        self.v_x = v_x
        self.v_y = v_y
        self.color = color
        self.current_color = color
        self.size = size
        self.life_time = life_time
        self.max_life = life_time
        self.gravity = 0.1

    def update(self):
        """Update particle physics and lifetime"""
        self.x += self.v_x
        self.y += self.v_y
        self.v_y += self.gravity  # Apply gravity
        self.v_x *= 0.99  # Air resistance

        # Decrease life time
        self.life_time -= 1

        # Fade color based on remaining life
        alpha = self.life_time / self.max_life
        self.current_color = (
            int(self.color[0] * alpha),
            int(self.color[1] * alpha),
            int(self.color[2] * alpha)
        )

        return self.life_time > 0
    
    def draw(self, screen):
        """Override in subclasses"""
        pass

class PixelParticle(BaseParticle):
    """Simple pixel-art style rectangular particles"""
    def __init__(self, x, y, v_x, v_y, color, size, life_time):
        super().__init__(x, y, v_x, v_y, color, size, life_time)
    
    def draw(self, screen):
        if self.life_time > 0:
            # Draw particle as a small square for pixel art style
            particle_rect = pygame.Rect(int(self.x), int(self.y), self.size, self.size)
            pygame.draw.rect(screen, self.current_color, particle_rect)

class HeartParticle(BaseParticle):
    """Heart-shaped particles using cached heart images"""
    def __init__(self, x, y, v_x, v_y, color, size, life_time):
        super().__init__(x, y, v_x, v_y, color, size, life_time)
        self.heart_image = get_cached_heart(size)
        self.alpha_step = 255.0 / life_time
    
    def draw(self, screen):
        if self.life_time > 0 and self.heart_image:
            # Calculate alpha for fading effect
            alpha = int(255 * (self.life_time / self.max_life))
            
            # Only set alpha if it changed significantly (avoid unnecessary operations)
            if alpha < 255:
                # Create a copy with alpha for this frame
                faded_heart = self.heart_image.copy()
                faded_heart.set_alpha(alpha)
                screen.blit(faded_heart, (int(self.x), int(self.y)))
            else:
                # No fading needed, blit directly
                screen.blit(self.heart_image, (int(self.x), int(self.y)))

class Firework:
    def __init__(self, x, y, target_x, target_y, color, particle_type="heart"):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.color = color
        self.particle_type = particle_type  # "heart" or "pixel"
        self.v_x = (target_x - x) * 0.02
        self.v_y = (target_y - y) * 0.02
        self.exploded = False
        self.particles = []

    def update(self):
        if not self.exploded:
            # Move towards target
            self.x += self.v_x
            self.y += self.v_y

            # Check if reached target (with some tolerance)
            if abs(self.x - self.target_x) < 10 and abs(self.y - self.target_y) < 10:
                self.explode()
        else:
            # Update explosion particles
            self.particles = [p for p in self.particles if p.update()]

        return len(self.particles) > 0 or not self.exploded
    
    def explode(self):
        self.exploded = True
        # Create explosion particles in all directions
        particle_count = random.randint(5, 15)  # 15, 25

        for _ in range(particle_count):
            # Random direction and speed
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            v_x = math.cos(angle) * speed
            v_y = math.sin(angle) * speed

            # Vary particle properties based on type
            if self.particle_type == "heart":
                size = random.randint(25, 40)
                life_time = random.randint(30, 60)
            else:  # pixel particles
                size = random.randint(2, 6)
                life_time = random.randint(20, 40)
            
            # Color variations
            color_variant = (
                min(255, max(0, self.color[0] + random.randint(-30, 30))),
                min(255, max(0, self.color[1] + random.randint(-30, 30))),
                min(255, max(0, self.color[2] + random.randint(-30, 30)))
            )

            # Create the appropriate particle type
            if self.particle_type == "heart":
                particle = HeartParticle(self.x, self.y, v_x, v_y, color_variant, size, life_time)
            else:
                particle = PixelParticle(self.x, self.y, v_x, v_y, color_variant, size, life_time)
            
            self.particles.append(particle)

    def draw(self, screen):
        if not self.exploded:
            # Draw the ascending firework
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)
            # Draw trail
            for i in range(5):
                trail_x = int(self.x - self.v_x * i * 2)
                trail_y = int(self.y - self.v_y * i * 2)
                alpha = 1 - (i * 0.2)
                trail_color = (
                    int(self.color[0] * alpha),
                    int(self.color[1] * alpha),
                    int(self.color[2] * alpha)
                )
                pygame.draw.circle(screen, trail_color, (int(trail_x), int(trail_y)), max(1, 3 - i))
        else:
            # Draw explosion particles
            for particle in self.particles:
                particle.draw(screen)

def create_firework(particle_type="heart"):
    """Create a new firework at random position with specified particle type"""
    start_x = random.randint(50, WIDTH - 50)
    start_y = HEIGHT
    target_x = random.randint(100, WIDTH - 100)
    target_y = random.randint(50, HEIGHT // 2)
    color = random.choice(firework_colors)

    return Firework(start_x, start_y, target_x, target_y, color, particle_type)


# Initilize fireworks system
fireworks = []
firework_colors = [
    (255, 100, 100),  # Red
    (100, 255, 100),  # Green
    (100, 100, 255),  # Blue
    (255, 255, 100),  # Yellow
    (255, 100, 255),  # Magenta
    (100, 255, 255),  # Cyan
    (255, 200, 100),  # Orange
    (200, 100, 255),  # Purple
]

# Initialize Pygame
pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Starter Setup")

# Set up clock
clock = pygame.time.Clock()
FPS = 60

src_face1_img = load_image('first_pygame/derp.png',(64,64), True)
src_face2_img = load_image('first_pygame/derp.png',(64,64))

face1_img = src_face1_img.copy()
face2_img = src_face2_img.copy()

face1_pos = [100, HEIGHT // 2 - 32]
face2_pos = [WIDTH - 164, HEIGHT // 2 - 32]

HEART_CACHE = {}
# Pre-load heart images for performance
preload_heart_images()

face1_anim = {
    'is_animating': False,
    'start_time': 0,
    'duration': 600,  # ms
    'start_scale': 1.0,
    'target_scale': 1.0,
    'bounce_height': 0,
    'flipped': False
}

face2_anim = {
    'is_animating': False,
    'start_time': 0,
    'duration': 600,  # ms
    'start_scale': 1.0,
    'target_scale': 1.0,
    'bounce_height': 0,
    'flipped': False
}

# Main loop
running = True
space_timer = 0
p_timer = 0
kg_timer = 0

while running:
    current_time = pygame.time.get_ticks()
    screen.fill((30, 30, 30))  # Fill the screen with a dark color

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Check for continuous key presses for animations
    keys = pygame.key.get_pressed()

    # Firework controls
    if keys[pygame.K_SPACE]:
        # Space = Heart fireworks
        space_timer += 1
        if space_timer % 8 == 0:  # Every 8 frames
            fireworks.append(create_firework("heart"))
    else:
        space_timer = 0

    if keys[pygame.K_p] and not keys[pygame.K_k]:
        # P = Pixel fireworks
        p_timer += 1
        if p_timer % 8 == 0:  # Every 8 frames
            fireworks.append(create_firework("pixel"))
    else:
        p_timer = 0

    # Handle LEFT key for face1 animation
    if keys[pygame.K_LEFT]:
        if not face1_anim['is_animating']:
            # Start new animation
            start_flip_animation(face1_anim, current_time)

    # Handle RIGHT key for face2 animation
    if keys[pygame.K_RIGHT]:
        if not face2_anim['is_animating']:
            # Start new animation
            start_flip_animation(face2_anim, current_time)

    # Handle K key for face1 animation with text
    if keys[pygame.K_k]:
        if not face1_anim['is_animating']:
            font = pygame.font.Font(None, 24)
            text = font.render("Grogu is so cutie", True, WHITE)
            start_flip_animation(face1_anim, current_time, text)
    # Handle G key for face2 with text
    if keys[pygame.K_g]:
        if not face2_anim['is_animating']:
            font = pygame.font.Font(None, 24)
            text = font.render("Kwomiiiii", True, WHITE)
            start_flip_animation(face2_anim, current_time, text)

    # Trigger multiple fireworks during the combo (heart fireworks for romance!)
    if keys[pygame.K_k] and keys[pygame.K_g]:
        kg_timer += 1
        if kg_timer % 4 == 0:  # Every 4 frames
            fireworks.append(create_firework("heart"))
    else:
        kg_timer = 0

    # Update fireworks
    fireworks = [fw for fw in fireworks if fw.update()]

    # Update animations
    face1_scale, face1_bounce = update_animation(face1_anim, current_time)
    face2_scale, face2_bounce = update_animation(face2_anim, current_time)

    # Apply transformations
    face1_img, face1_y_offset = apply_animation_transform(
        src_face1_img, face1_scale, face1_bounce, face1_anim['flipped']
    )
    face2_img, face2_y_offset = apply_animation_transform(
        src_face2_img, face2_scale, face2_bounce, face2_anim['flipped']
    )

    pygame.draw.line(screen, WHITE, [0, HEIGHT // 2 + 32], [WIDTH, HEIGHT // 2 + 32], 10)

    # Calculate positions with bounce offset and centering for scaled images
    face1_draw_pos = [
        face1_pos[0] - (face1_img.get_width() - 64) // 2,  # Center scaled image
        face1_pos[1] + face1_y_offset - (face1_img.get_height() - 64) // 2
    ]
    face2_draw_pos = [
        face2_pos[0] - (face2_img.get_width() - 64) // 2,  # Center scaled image  
        face2_pos[1] + face2_y_offset - (face2_img.get_height() - 64) // 2
    ]

    # Draw faces
    screen.blit(face1_img, face1_draw_pos)
    screen.blit(face2_img, face2_draw_pos)

    # Draw fireworks
    for firework in fireworks:
        firework.draw(screen)

    # Draw labels for the faces
    font = pygame.font.Font(None, 36)
    label1 = font.render("Kwimi", True, WHITE)
    label2 = font.render("Grogu", True, WHITE)

    screen.blit(label1, (face1_pos[0], face1_draw_pos[1] - 40))
    screen.blit(label2, (face2_pos[0], face2_draw_pos[1] - 40))

    # Draw animated text if available
    if face1_anim.get('text') and face1_anim['is_animating']:
        # Position text above the bouncing image
        text_pos = (face1_draw_pos[0] + 80, face1_draw_pos[1])
        screen.blit(face1_anim['text'], text_pos)
    
    if face2_anim.get('text') and face2_anim['is_animating']:
        # Position text above the bouncing image
        text_pos = (face2_draw_pos[0] - 80, face2_draw_pos[1])
        screen.blit(face2_anim['text'], text_pos)

    # Draw firework instructions
    instruction_font = pygame.font.Font(None, 24)
    instructions = [
        "SPACE: Heart fireworks",
        "P: Pixel fireworks", 
        "K+G: Romance combo (hearts!)"
    ]
    
    for i, instruction in enumerate(instructions):
        instruction_surface = instruction_font.render(instruction, True, WHITE)
        screen.blit(instruction_surface, (10, 10 + i * 25))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()