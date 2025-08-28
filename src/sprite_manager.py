#sprite_manager.py
import pygame
import random
import math

class Fish:
    def __init__(self, sprite_path, x, y, screen_width, screen_height):
        # Load and prepare sprite
        try:
            self.original_image = pygame.image.load(sprite_path).convert_alpha()
        except Exception as e:
            print(f"Failed to load sprite: {e}")
            # Create a default placeholder sprite
            self.original_image = pygame.Surface((50, 30), pygame.SRCALPHA)
            self.original_image.fill((255, 100, 100, 200))  # Semi-transparent red fish
        
        original_size = self.original_image.get_size()
        scale_factor = min(80 / max(original_size), 1.0)
        new_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
        self.original_image = pygame.transform.scale(self.original_image, new_size)
        
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Initialize ALL attributes BEFORE calling _setup_swim_style()
        self.base_speed = random.uniform(0.8, 2.5)
        self.speed = self.base_speed
        self.direction = random.uniform(0, 360)
        self.target_direction = self.direction
        
        # Initialize attributes that _setup_swim_style() will modify
        self.tail_beat_frequency = random.uniform(0.15, 0.35)
        self.following_tendency = random.uniform(0.1, 0.8)
        self.personal_space = random.uniform(25, 60)
        self.energy = random.uniform(0.7, 1.0)
        
        # Now it's safe to call _setup_swim_style()
        self.swim_style = random.choice(['cruiser', 'darting', 'lazy', 'active'])
        self._setup_swim_style()
        
        # Continue with other initializations
        self.time = 0
        self.swim_phase = random.uniform(0, 2 * math.pi)
        self.body_undulation = random.uniform(0.5, 1.5)
        
        self.depth_layer = random.uniform(0.3, 1.0)
        self.speed *= self.depth_layer
        
        self.comfort_distance = random.uniform(60, 120)
        
        self.boundary_comfort = random.uniform(40, 80)
        self.panic_distance = 20
        
        self.flip_horizontal = False
        self.current_scale = 1.0
        self.target_scale = 1.0
        
        self.state = 'exploring'
        self.state_timer = random.randint(180, 600)
        
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.03
        self.drag = 0.95
        
    def _setup_swim_style(self):
        if self.swim_style == 'cruiser':
            self.base_speed *= 0.8
            self.tail_beat_frequency *= 0.7
            self.following_tendency *= 1.2
        elif self.swim_style == 'darting':
            self.base_speed *= 1.4
            self.tail_beat_frequency *= 1.5
            self.personal_space *= 0.7
        elif self.swim_style == 'lazy':
            self.base_speed *= 0.6
            self.tail_beat_frequency *= 0.5
            self.energy *= 0.8
        elif self.swim_style == 'active':
            self.base_speed *= 1.1
            self.tail_beat_frequency *= 1.2
            
    def update(self, other_fish=None, food_sources=None):
        self.time += 1
        self.state_timer -= 1
        self._update_behavior_state(other_fish)
        self._handle_boundaries()
        if other_fish:
            self._advanced_schooling_behavior(other_fish)
        
        if self.state == 'exploring':
            self._explore_behavior()
        elif self.state == 'schooling':
            self._schooling_behavior_enhanced(other_fish)
        elif self.state == 'feeding':
            self._feeding_behavior(food_sources)
        elif self.state == 'resting':
            self._resting_behavior()
            
        self._apply_physics()
        self._add_natural_swimming_motion()
        
        self.rect.centerx += self.velocity_x
        self.rect.centery += self.velocity_y
        self._enforce_boundaries()
        self._update_visual_state()
        
    def _update_behavior_state(self, other_fish):
        if self.state_timer <= 0:
            nearby_fish_count = 0
            if other_fish:
                center_x, center_y = self.rect.center
                for fish in other_fish:
                    if fish != self:
                        other_x, other_y = fish.rect.center
                        distance = math.sqrt((center_x - other_x)**2 + (center_y - other_y)**2)
                        if distance < 100:
                            nearby_fish_count += 1
            
            if nearby_fish_count >= 3:
                self.state = 'schooling'
                self.state_timer = random.randint(300, 900)
            elif self.energy < 0.3:
                self.state = 'resting'
                self.state_timer = random.randint(120, 300)
            elif random.random() < 0.3:
                self.state = 'feeding'
                self.state_timer = random.randint(180, 400)
            else:
                self.state = 'exploring'
                self.state_timer = random.randint(200, 600)
                
    def _explore_behavior(self):
        if random.random() < 0.008:
            self.target_direction += random.uniform(-60, 60)
        if random.random() < 0.005:
            if self.rect.centery < self.screen_height * 0.3:
                self.target_direction = random.uniform(45, 135)
            elif self.rect.centery > self.screen_height * 0.7:
                self.target_direction = random.uniform(225, 315)
                
    def _schooling_behavior_enhanced(self, other_fish):
        if not other_fish:
            return
        center_x, center_y = self.rect.center
        nearby_fish = []
        for fish in other_fish:
            if fish == self:
                continue
            other_x, other_y = fish.rect.center
            distance = math.sqrt((center_x - other_x)**2 + (center_y - other_y)**2)
            if distance < self.comfort_distance:
                nearby_fish.append((fish, distance))
        
        if not nearby_fish:
            return
        leader = max(nearby_fish, key=lambda x: x[0].energy * x[0].speed)[0]
        leader_influence = 0.3 * self.following_tendency
        self.target_direction = (self.target_direction * (1 - leader_influence) + 
                               leader.direction * leader_influence)
        
    def _feeding_behavior(self, food_sources):
        target_y = self.screen_height * random.uniform(0.4, 0.6)
        current_y = self.rect.centery
        if abs(current_y - target_y) > 20:
            if current_y < target_y:
                self.target_direction = random.uniform(45, 135)
            else:
                self.target_direction = random.uniform(225, 315)
        self.speed = self.base_speed * 0.6
        
    def _resting_behavior(self):
        if self.rect.centery < self.screen_height * 0.7:
            self.target_direction = random.uniform(45, 135)
        self.speed = self.base_speed * 0.3
        self.energy = min(1.0, self.energy + 0.002)
        
    def _handle_boundaries(self):
        center_x, center_y = self.rect.center
        distances = {
            'left': center_x,
            'right': self.screen_width - center_x,
            'top': center_y,
            'bottom': self.screen_height - center_y
        }
        for boundary, distance in distances.items():
            if distance < self.panic_distance:
                if boundary == 'left':
                    self.target_direction = random.uniform(-30, 30)
                elif boundary == 'right':
                    self.target_direction = random.uniform(150, 210)
                elif boundary == 'top':
                    self.target_direction = random.uniform(45, 135)
                elif boundary == 'bottom':
                    self.target_direction = random.uniform(225, 315)
                self.speed = self.base_speed * 1.5
                return
        steering_force = 0
        for boundary, distance in distances.items():
            if distance < self.boundary_comfort:
                force_strength = (self.boundary_comfort - distance) / self.boundary_comfort
                if boundary == 'left':
                    steering_force += force_strength * 45
                elif boundary == 'right':
                    steering_force -= force_strength * 45
                elif boundary == 'top':
                    self.target_direction += force_strength * 20
                elif boundary == 'bottom':
                    self.target_direction -= force_strength * 20
        if steering_force != 0:
            self.target_direction += steering_force * 0.1
            
    def _advanced_schooling_behavior(self, other_fish):
        if not other_fish:
            return
        center_x, center_y = self.rect.center
        separation_x = separation_y = 0
        alignment_x = alignment_y = 0
        cohesion_x = cohesion_y = 0
        neighbors = 0
        for fish in other_fish:
            if fish == self:
                continue
            other_x, other_y = fish.rect.center
            distance = math.sqrt((center_x - other_x)**2 + (center_y - other_y)**2)
            if distance < self.comfort_distance and distance > 0:
                neighbors += 1
                if distance < self.personal_space:
                    separation_x += (center_x - other_x) / distance
                    separation_y += (center_y - other_y) / distance
                alignment_x += math.cos(math.radians(fish.direction))
                alignment_y += math.sin(math.radians(fish.direction))
                cohesion_x += other_x
                cohesion_y += other_y
        if neighbors > 0:
            if separation_x != 0 or separation_y != 0:
                sep_direction = math.degrees(math.atan2(separation_y, separation_x))
                self.target_direction = sep_direction
            else:
                avg_alignment_x = alignment_x / neighbors
                avg_alignment_y = alignment_y / neighbors
                avg_cohesion_x = cohesion_x / neighbors
                avg_cohesion_y = cohesion_y / neighbors
                desired_x = avg_alignment_x * 0.3 + (avg_cohesion_x - center_x) * 0.1
                desired_y = avg_alignment_y * 0.3 + (avg_cohesion_y - center_y) * 0.1
                if desired_x != 0 or desired_y != 0:
                    desired_direction = math.degrees(math.atan2(desired_y, desired_x))
                    influence = 0.15 * self.following_tendency
                    direction_diff = desired_direction - self.target_direction
                    if direction_diff > 180:
                        direction_diff -= 360
                    elif direction_diff < -180:
                        direction_diff += 360
                    self.target_direction += direction_diff * influence
    
    def _apply_physics(self):
        direction_diff = self.target_direction - self.direction
        if direction_diff > 180:
            direction_diff -= 360
        elif direction_diff < -180:
            direction_diff += 360
        max_turn_rate = 4.0 * (self.energy * 0.5 + 0.5)
        direction_diff = max(-max_turn_rate, min(max_turn_rate, direction_diff))
        self.direction += direction_diff
        if self.direction < 0:
            self.direction += 360
        elif self.direction >= 360:
            self.direction -= 360
        target_vel_x = math.cos(math.radians(self.direction)) * self.speed
        target_vel_y = math.sin(math.radians(self.direction)) * self.speed
        self.velocity_x += (target_vel_x - self.velocity_x) * self.acceleration
        self.velocity_y += (target_vel_y - self.velocity_y) * self.acceleration
        self.velocity_x *= self.drag
        self.velocity_y *= self.drag
        energy_cost = (abs(self.velocity_x) + abs(self.velocity_y)) * 0.0001
        self.energy = max(0.1, self.energy - energy_cost)
        
    def _add_natural_swimming_motion(self):
        tail_beat = math.sin(self.time * self.tail_beat_frequency + self.swim_phase)
        body_wave = math.sin(self.time * self.tail_beat_frequency * 2 + self.swim_phase) * 0.3
        perpendicular_angle = self.direction + 90
        undulation_x = math.cos(math.radians(perpendicular_angle)) * tail_beat * self.body_undulation
        undulation_y = math.sin(math.radians(perpendicular_angle)) * tail_beat * self.body_undulation
        self.velocity_x += undulation_x * 0.1
        self.velocity_y += undulation_y * 0.1
        buoyancy = math.sin(self.time * 0.01 + self.swim_phase) * 0.2
        self.velocity_y += buoyancy
        speed_variation = 1 + tail_beat * 0.1
        self.speed = self.base_speed * speed_variation * (self.energy * 0.3 + 0.7)
        
    def _enforce_boundaries(self):
        margin = 10
        self.rect.centerx = max(margin, min(self.screen_width - margin, self.rect.centerx))
        self.rect.centery = max(margin, min(self.screen_height - margin, self.rect.centery))
        
    def _update_visual_state(self):
        should_flip = 90 < self.direction < 270
        if should_flip != self.flip_horizontal:
            self.flip_horizontal = should_flip
            base_image = pygame.transform.flip(self.original_image, True, False)
        else:
            base_image = self.original_image.copy()
        rotation_angle = 0
        if abs(self.velocity_y) > 0.5:
            max_rotation = 15
            rotation_angle = (self.velocity_y / 3.0) * max_rotation
            rotation_angle = max(-max_rotation, min(max_rotation, rotation_angle))
        if abs(rotation_angle) > 1:
            base_image = pygame.transform.rotate(base_image, -rotation_angle)
        depth_scale = 0.7 + (self.depth_layer * 0.3)
        if abs(depth_scale - self.current_scale) > 0.01:
            self.current_scale += (depth_scale - self.current_scale) * 0.05
            new_size = (int(base_image.get_width() * self.current_scale),
                       int(base_image.get_height() * self.current_scale))
            base_image = pygame.transform.scale(base_image, new_size)
        alpha = int(255 * (0.4 + self.depth_layer * 0.6))
        base_image.set_alpha(alpha)
        old_center = self.rect.center
        self.image = base_image
        self.rect = self.image.get_rect()
        self.rect.center = old_center

class SpriteManager:
    def __init__(self, screen_width=800, screen_height=600):
        self.fish_list = []
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.water_current_x = 0
        self.water_current_y = 0
        self.current_change_timer = 0
        
    def create_sprite(self, sprite_path, count=1):
        for _ in range(count):
            x = random.randint(80, self.screen_width - 80)
            y = random.randint(80, self.screen_height - 80)
            fish = Fish(sprite_path, x, y, self.screen_width, self.screen_height)
            self.fish_list.append(fish)
    
    def create_school(self, sprite_path, count=5, center_x=None, center_y=None):
        if center_x is None:
            center_x = random.randint(150, self.screen_width - 150)
        if center_y is None:
            center_y = random.randint(150, self.screen_height - 150)
        school_radius = min(80, count * 15)
        for i in range(count):
            angle = i * 137.5
            radius = school_radius * math.sqrt(i / count)
            x = center_x + radius * math.cos(math.radians(angle))
            y = center_y + radius * math.sin(math.radians(angle))
            x = max(80, min(self.screen_width - 80, x))
            y = max(80, min(self.screen_height - 80, y))
            fish = Fish(sprite_path, x, y, self.screen_width, self.screen_height)
            base_direction = random.uniform(0, 360)
            fish.direction = base_direction + random.uniform(-30, 30)
            fish.target_direction = fish.direction
            fish.following_tendency = random.uniform(0.5, 0.9)
            self.fish_list.append(fish)
    
    def create_mixed_school(self, sprite_path, total_count=8):
        remaining = total_count
        school_count = random.randint(2, 4)
        for i in range(school_count):
            if remaining <= 0:
                break
            school_size = random.randint(1, min(remaining, 4))
            center_x = random.randint(150, self.screen_width - 150)
            center_y = random.randint(150, self.screen_height - 150)
            self.create_school(sprite_path, school_size, center_x, center_y)
            remaining -= school_size
    
    def update_sprites(self):
        self.current_change_timer += 1
        if self.current_change_timer > 1800:
            self.water_current_x = random.uniform(-0.2, 0.2)
            self.water_current_y = random.uniform(-0.1, 0.1)
            self.current_change_timer = 0
        for fish in self.fish_list:
            fish.update(self.fish_list)
            fish.velocity_x += self.water_current_x
            fish.velocity_y += self.water_current_y
    
    def draw_sprites(self, screen):
        sorted_fish = sorted(self.fish_list, key=lambda f: f.depth_layer)
        for fish in sorted_fish:
            screen.blit(fish.image, fish.rect)
    
    def add_fish(self, sprite_path, x=None, y=None):
        if x is None:
            x = random.randint(80, self.screen_width - 80)
        if y is None:
            y = random.randint(80, self.screen_height - 80)
        fish = Fish(sprite_path, x, y, self.screen_width, self.screen_height)
        self.fish_list.append(fish)
        return fish
    
    def get_fish_count(self):
        return len(self.fish_list)
    
    def clear_all_fish(self):
        self.fish_list.clear()