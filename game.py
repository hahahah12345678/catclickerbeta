import pygame
import math
import random
import time
import json
import os
from PIL import Image, ImageDraw

# Initialize Pygame
pygame.init()
try:
    pygame.mixer.init()
    sound_enabled = True
except pygame.error:
    sound_enabled = False
    print("Audio not available, continuing without sound")

# Set screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
cats = 0
# Set window title
pygame.display.set_caption("cat clicker")
#make a display that shows your amount of cats
font = pygame.font.SysFont(None, 55)
click_font = pygame.font.SysFont(None, 40)

# Click effect variables
click_effects = []
cat_scale = 1.0
cat_scale_target = 1.0
clock = pygame.time.Clock()

# Sound effects (load MP3 files)
def load_sound(filename):
    if not sound_enabled:
        return None
    try:
        if os.path.exists(filename):
            return pygame.mixer.Sound(filename)
        else:
            print(f"Sound file {filename} not found")
            return None
    except Exception as e:
        print(f"Error loading sound {filename}: {e}")
        return None

# Load sound effects
click_sound = load_sound("click_sound.mp3")
purchase_sound = load_sound("purchase_sound.mp3")
rainbow_click_sound = load_sound("rainbow_click_sound.mp3")

# Load and play background music
def load_background_music():
    if not sound_enabled:
        return
    try:
        if os.path.exists("background_music.mp3"):
            pygame.mixer.music.load("background_music.mp3")
            pygame.mixer.music.set_volume(0.3)  # Lower volume for background
            pygame.mixer.music.play(-1)  # Loop infinitely
        else:
            print("Background music file not found")
    except Exception as e:
        print(f"Error loading background music: {e}")

# Start background music
load_background_music()

# Scrolling variables
upgrade_scroll = 0
max_visible_upgrades = 4

# Upgrade system
upgrades = [
    {
        'name': 'Auto Clicker',
        'description': 'Automatically clicks 1 cat per second',
        'cost': 15,
        'owned': 0,
        'auto_rate': 1,
        'icon': 'cat_upgrade1.png'
    },
    {
        'name': 'Cat Multiplier',
        'description': 'Each click gives +1 extra cat',
        'cost': 100,
        'owned': 0,
        'click_bonus': 1,
        'icon': 'cat_upgrade2.png'
    },
    {
        'name': 'Super Clicker',
        'description': 'Automatically clicks 5 cats per second',
        'cost': 500,
        'owned': 0,
        'auto_rate': 5,
        'icon': 'cat_upgrade1.png'
    },
    {
        'name': 'Mega Multiplier',
        'description': 'Each click gives +5 extra cats',
        'cost': 2000,
        'owned': 0,
        'click_bonus': 5,
        'icon': 'cat_upgrade2.png'
    },
    {
        'name': 'Cat Factory',
        'description': 'Automatically produces 25 cats per second',
        'cost': 10000,
        'owned': 0,
        'auto_rate': 25,
        'icon': 'cat_upgrade1.png'
    }
]

# Upgrade tiers
upgrade_tiers = {
    'Auto Clicker': [
        {'name': 'Improved Motors', 'cost_multiplier': 1.2, 'auto_rate_bonus': 1},
        {'name': 'Steel Fingers', 'cost_multiplier': 1.3, 'auto_rate_bonus': 2}
    ],
    'Cat Multiplier': [
        {'name': 'Shiny Cats', 'cost_multiplier': 1.2, 'click_bonus_increase': 1},
        {'name': 'Golden Cats', 'cost_multiplier': 1.3, 'click_bonus_increase': 2}
    ]
}

# Unlocked upgrade tiers
unlocked_tiers = {upgrade['name']: 0 for upgrade in upgrades if upgrade['name'] in upgrade_tiers}

# Advanced upgrades (prestige shop)
advanced_upgrades = [
    {'name': 'Faster Rainbow Cats', 'description': 'Rainbow cats spawn twice as fast', 'cost': 10, 'owned': 0},
    {'name': 'Cheaper Upgrades', 'description': 'All upgrades are 10% cheaper', 'cost': 25, 'owned': 0}
]

# Auto clicker timer
auto_click_timer = 0
click_power = 1

# Prestige system variables
prestige_level = 0
prestige_points = 0
base_cats_for_prestige = 10000  # Starting amount of cats needed to prestige

# Function to calculate potential prestige points
def calculate_prestige_points():
    if cats >= base_cats_for_prestige:
        # Calculate prestige points (simplified formula)
        return int(math.log10(cats / base_cats_for_prestige) * 5)
    else:
        return 0

# Function to perform prestige
def perform_prestige():
    global cats, click_power, prestige_level, prestige_points, base_cats_for_prestige

    potential_points = calculate_prestige_points()
    if potential_points > 0:
        # Reset game state
        cats = 0
        click_power = 1

        # Increase prestige level and add prestige points
        prestige_level += 1
        prestige_points += potential_points

        # Update base cats required for prestige (increase exponentially)
        base_cats_for_prestige *= 10
        print("Prestige performed! New level:", prestige_level, "Prestige points:", prestige_points)
    else:
        print("Not enough cats to prestige.")

# Save/Load system
def save_game():
    data = {
        'cats': cats,
        'upgrades': upgrades,
        'click_power': click_power,
        'prestige_level': prestige_level,
        'prestige_points': prestige_points,
        'base_cats_for_prestige': base_cats_for_prestige,
        'unlocked_tiers': unlocked_tiers,
        'advanced_upgrades': advanced_upgrades
    }
    try:
        with open('save_game.json', 'w') as f:
            json.dump(data, f)
    except:
        pass

def load_game():
    global cats, upgrades, click_power, prestige_level, prestige_points, base_cats_for_prestige
    global unlocked_tiers, advanced_upgrades
    try:
        if os.path.exists('save_game.json'):
            with open('save_game.json', 'r') as f:
                data = json.load(f)
                cats = data.get('cats', 0)
                upgrades[:] = data.get('upgrades', upgrades)
                click_power = data.get('click_power', 1)
                prestige_level = data.get('prestige_level', 0)
                prestige_points = data.get('prestige_points', 0)
                base_cats_for_prestige = data.get('base_cats_for_prestige', 10000)
                unlocked_tiers.update(data.get('unlocked_tiers', unlocked_tiers))
                advanced_upgrades[:] = data.get('advanced_upgrades', advanced_upgrades)
    except:
        pass

# Load game at start
load_game()

# Auto-save timer
auto_save_timer = 0

# Rainbow cat system
rainbow_cats = []
rainbow_cat_timer = 0
rainbow_cat_spawn_time = random.randint(300, 900)  # 5-15 minutes at 60 FPS

# Create background image if it doesn't exist
def create_background():
    try:
        # Create a gradient background
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color='lightblue')
        draw = ImageDraw.Draw(image)

        # Create a simple sky gradient
        for y in range(height):
            # Gradient from light blue to white
            color_value = int(135 + (255 - 135) * (y / height))
            color = (color_value, color_value + 20, 255)
            draw.line([(0, y), (width, y)], fill=color)

        # Add some simple clouds
        for i in range(5):
            x = random.randint(0, width - 100)
            y = random.randint(0, height // 3)
            draw.ellipse([x, y, x + 80, y + 40], fill='white')
            draw.ellipse([x + 20, y - 10, x + 100, y + 30], fill='white')

        image.save('background.png')
        return True
    except:
        return False

# Create background if it doesn't exist
if not os.path.exists('background.png'):
    create_background()

# Restart functionality
def restart_game():
    global cats, upgrades, click_power, upgrade_scroll, auto_click_timer, auto_save_timer
    global click_effects, cat_scale, cat_scale_target, rainbow_cats, rainbow_cat_timer, rainbow_cat_spawn_time
    global prestige_level, prestige_points, base_cats_for_prestige, unlocked_tiers, advanced_upgrades

    # Reset all game variables
    cats = 0
    click_power = 1
    upgrade_scroll = 0
    auto_click_timer = 0
    auto_save_timer = 0
    click_effects = []
    cat_scale = 1.0
    cat_scale_target = 1.0
    rainbow_cats = []
    rainbow_cat_timer = 0
    rainbow_cat_spawn_time = random.randint(18000, 54000)

    # Reset prestige variables
    prestige_level = 0
    prestige_points = 0
    base_cats_for_prestige = 10000

    # Reset upgrades
    upgrades = [
        {
            'name': 'Auto Clicker',
            'description': 'Automatically clicks 1 cat per second',
            'cost': 15,
            'owned': 0,
            'auto_rate': 1,
            'icon': 'cat_upgrade1.png'
        },
        {
            'name': 'Cat Multiplier',
            'description': 'Each click gives +1 extra cat',
            'cost': 100,
            'owned': 0,
            'click_bonus': 1,
            'icon': 'cat_upgrade2.png'
        },
        {
            'name': 'Super Clicker',
            'description': 'Automatically clicks 5 cats per second',
            'cost': 500,
            'owned': 0,
            'auto_rate': 5,
            'icon': 'cat_upgrade3.png'
        },
        {
            'name': 'Mega Multiplier',
            'description': 'Each click gives +5 extra cats',
            'cost': 2000,
            'owned': 0,
            'click_bonus': 5,
            'icon': 'cat_upgrade4.png'
        },
        {
            'name': 'Cat Factory',
            'description': 'Automatically produces 25 cats per second',
            'cost': 10000,
            'owned': 0,
            'auto_rate': 25,
            'icon': 'cat_upgrade5.png'
        }
    ]

    # Reset unlocked tiers
    unlocked_tiers = {upgrade['name']: 0 for upgrade in upgrades if upgrade['name'] in upgrade_tiers}

    # Reset advanced upgrades
    advanced_upgrades = [
        {'name': 'Faster Rainbow Cats', 'description': 'Rainbow cats spawn twice as fast', 'cost': 10, 'owned': 0},
        {'name': 'Cheaper Upgrades', 'description': 'All upgrades are 10% cheaper', 'cost': 25, 'owned': 0}
    ]

    # Delete save file
    try:
        if os.path.exists('save_game.json'):
            os.remove('save_game.json')
    except:
        pass

# Image loading function
def load_image(filename, size=None, fallback_color=(100, 100, 100)):
    try:
        image = pygame.image.load(filename)
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except:
        # Create a fallback rectangle if image doesn't exist
        if size:
            surface = pygame.Surface(size)
            surface.fill(fallback_color)
            return surface
        else:
            surface = pygame.Surface((64, 64))
            surface.fill(fallback_color)
            return surface

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game()  # Save before quitting
            running = False

        if event.type == pygame.KEYDOWN:
            # Scroll upgrades with arrow keys
            if event.key == pygame.K_UP and upgrade_scroll > 0:
                upgrade_scroll -= 1
            elif event.key == pygame.K_DOWN and upgrade_scroll < len(upgrades) - max_visible_upgrades:
                upgrade_scroll += 1

        if event.type == pygame.MOUSEWHEEL:
            # Scroll upgrades with mouse wheel
            if event.y > 0 and upgrade_scroll > 0:
                upgrade_scroll -= 1
            elif event.y < 0 and upgrade_scroll < len(upgrades) - max_visible_upgrades:
                upgrade_scroll += 1

        #make it so when you click the cat it gives you 1 cat
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            cat_x = screen_width//4 - screen_width//5
            cat_y = screen_height//2 - screen_height//5
            cat_width = screen_width//2.5
            cat_height = screen_height//2.5

            # Check if click is on the cat
            if (cat_x <= mouse_x <= cat_x + cat_width and 
                cat_y <= mouse_y <= cat_y + cat_height):
                cats += click_power
                print(cats)

                # Play click sound
                if click_sound:
                    try:
                        click_sound.play()
                    except:
                        pass

                # Add click effect
                cat_scale_target = 1.2

                # Add floating text effect
                click_effects.append({
                    'x': mouse_x,
                    'y': mouse_y,
                    'alpha': 255,
                    'timer': 60,
                    'value': click_power
                })

            # Check if click is on upgrade buttons
            for i in range(max_visible_upgrades):
                if upgrade_scroll + i >= len(upgrades):
                    break

                upgrade = upgrades[upgrade_scroll + i]
                upgrade_x = screen_width - 250
                upgrade_y = 100 + i * 120
                upgrade_width = 200
                upgrade_height = 100

                if (upgrade_x <= mouse_x <= upgrade_x + upgrade_width and 
                    upgrade_y <= mouse_y <= upgrade_y + upgrade_height):
                    if cats >= upgrade['cost']:
                        cats -= upgrade['cost']
                        upgrade['owned'] += 1
                        upgrade['cost'] = int(upgrade['cost'] * 1.5)  # Increase cost

                        # Play purchase sound
                        if sound_enabled and purchase_sound:
                            try:
                                purchase_sound.play()
                            except Exception as e:
                                print(f"Error playing purchase sound: {e}")

                        # Update click power if it's the multiplier upgrade
                        if 'click_bonus' in upgrade:
                            click_power += upgrade['click_bonus']

                # Check tier upgrade buttons
                tier_x = upgrade_x + 210
                tier_width = 30
                tier_height = 30

                upgrade_name = upgrade['name']
                if (upgrade_name in upgrade_tiers and 
                    unlocked_tiers[upgrade_name] < len(upgrade_tiers[upgrade_name])):

                    tier_y = upgrade_y + 35
                    if (tier_x <= mouse_x <= tier_x + tier_width and 
                        tier_y <= mouse_y <= tier_y + tier_height):

                        tier_cost = upgrade['cost'] * 10
                        if cats >= tier_cost:
                            cats -= tier_cost
                            unlocked_tiers[upgrade_name] += 1

                            # Apply tier bonus
                            tier = upgrade_tiers[upgrade_name][unlocked_tiers[upgrade_name] - 1]
                            upgrade['cost'] = int(upgrade['cost'] * tier['cost_multiplier'])

            # Check if click is on advanced upgrade buttons (prestige shop)
            if prestige_level > 0:
                for i, upgrade in enumerate(advanced_upgrades):
                    adv_x = screen_width - 250
                    adv_y = 100 + (len(upgrades) + i + 1) * 60
                    adv_width = 240
                    adv_height = 50

                    if (adv_x <= mouse_x <= adv_x + adv_width and 
                        adv_y <= mouse_y <= adv_y + adv_height):
                        if prestige_points >= upgrade['cost']:
                            prestige_points -= upgrade['cost']
                            upgrade['owned'] += 1
                            upgrade['cost'] = int(upgrade['cost'] * 2)

            # Check if click is on prestige button
            prestige_x = 220
            prestige_y = screen_height - 50
            prestige_width = 120
            prestige_height = 40

            potential_points = calculate_prestige_points()
            if (potential_points > 0 and 
                prestige_x <= mouse_x <= prestige_x + prestige_width and 
                prestige_y <= mouse_y <= prestige_y + prestige_height):
                perform_prestige()

    # Game logic goes here

    # Update cat scale animation
    if cat_scale < cat_scale_target:
        cat_scale += 0.02
    elif cat_scale > cat_scale_target:
        cat_scale -= 0.02

    # Reset scale target back to normal
    if cat_scale_target > 1.0:
        cat_scale_target = 1.0

    # Auto clicker logic
    auto_click_timer += 1
    if auto_click_timer >= 60:  # 1 second at 60 FPS
        auto_click_timer = 0
        auto_cats = sum(upgrade['owned'] * upgrade.get('auto_rate', 0) for upgrade in upgrades)
        if auto_cats > 0:
            cats += auto_cats
            # Add floating text for auto clicks
            try:
                click_effects.append({
                    'x': cat_x + scaled_size[0]//2,
                    'y': cat_y,
                    'alpha': 255,
                    'timer': 60,
                    'value': auto_cats
                })
            except:
                pass

    # Rainbow cat spawning
    rainbow_cat_timer += 1
    if rainbow_cat_timer >= rainbow_cat_spawn_time:
        rainbow_cat_timer = 0
        rainbow_cat_spawn_time = random.randint(18000, 54000)  # 5-15 minutes at 60 FPS

        # Spawn rainbow cat at random position
        rainbow_cats.append({
            'x': random.randint(100, screen_width - 100),
            'y': random.randint(100, screen_height - 100),
            'size': 60,
            'timer': 600,  # 10 seconds lifetime
            'bounce_x': random.choice([-2, -1, 1, 2]),
            'bounce_y': random.choice([-2, -1, 1, 2]),
            'rainbow_offset': 0
        })

    # Update rainbow cats
    for rainbow_cat in rainbow_cats[:]:
        rainbow_cat['timer'] -= 1
        rainbow_cat['rainbow_offset'] += 0.1

        # Move rainbow cat
        rainbow_cat['x'] += rainbow_cat['bounce_x']
        rainbow_cat['y'] += rainbow_cat['bounce_y']

        # Bounce off edges
        if rainbow_cat['x'] <= 0 or rainbow_cat['x'] >= screen_width - rainbow_cat['size']:
            rainbow_cat['bounce_x'] *= -1
        if rainbow_cat['y'] <= 0 or rainbow_cat['y'] >= screen_height - rainbow_cat['size']:
            rainbow_cat['bounce_y'] *= -1

        # Remove if timer expires
        if rainbow_cat['timer'] <= 0:
            rainbow_cats.remove(rainbow_cat)

    # Auto-save every 5 seconds
    auto_save_timer += 1
    if auto_save_timer >= 300:  # 5 seconds at 60 FPS
        auto_save_timer = 0
        save_game()

    # Update click effects
    for effect in click_effects:
        effect['timer'] -= 1
        effect['y'] -= 2
        effect['alpha'] -= 4
        if effect['timer'] <= 0 or effect['alpha'] <= 0:
            click_effects.remove(effect)

    # Draw everything
    # Draw background
    background = load_image("background.png", (screen_width, screen_height), (135, 206, 235))
    screen.blit(background, (0, 0))
    # Add your drawing code here
    #blit cat.png to the screen
    base_size = (screen_width//2.5, screen_height//2.5)
    scaled_size = (int(base_size[0] * cat_scale), int(base_size[1] * cat_scale))
    cat = load_image("cat.png", scaled_size, (255, 180, 100))

    # Position cat more to the left
    cat_x = screen_width//4 - scaled_size[0]//2
    cat_y = screen_height//2 - scaled_size[1]//2
    screen.blit(cat, (cat_x, cat_y))

    # Draw rainbow cats
    for rainbow_cat in rainbow_cats:
        # Create rainbow effect
        colors = [
            (255, 0, 0),    # Red
            (255, 127, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (75, 0, 130),   # Indigo
            (148, 0, 211)   # Violet
        ]

        # Draw rainbow aura
        for i, color in enumerate(colors):
            offset = int(rainbow_cat['rainbow_offset'] * 10 + i * 15) % len(colors)
            aura_size = rainbow_cat['size'] + 10 + i * 3
            aura_alpha = 100 - i * 10

            aura_surface = pygame.Surface((aura_size, aura_size), pygame.SRCALPHA)
            pygame.draw.circle(aura_surface, (*colors[offset], aura_alpha), 
                             (aura_size//2, aura_size//2), aura_size//2)
            screen.blit(aura_surface, (rainbow_cat['x'] - i*3 - 5, rainbow_cat['y'] - i*3 - 5))

        # Draw the rainbow cat (use regular cat image with rainbow tint)
        rainbow_cat_img = load_image("cat.png", (rainbow_cat['size'], rainbow_cat['size']))

        # Add rainbow tint
        tint_surface = pygame.Surface((rainbow_cat['size'], rainbow_cat['size']), pygame.SRCALPHA)
        tint_color = colors[int(rainbow_cat['rainbow_offset'] * 5) % len(colors)]
        tint_surface.fill((*tint_color, 100))
        rainbow_cat_img.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        screen.blit(rainbow_cat_img, (rainbow_cat['x'], rainbow_cat['y']))

        # Draw timer bar
        bar_width = rainbow_cat['size']
        bar_height = 5
        bar_x = rainbow_cat['x']
        bar_y = rainbow_cat['y'] - 10

        # Background bar
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height))

        # Timer bar
        timer_percent = rainbow_cat['timer'] / 600
        timer_width = int(bar_width * timer_percent)
        bar_color = (255, int(255 * timer_percent), 0)  # Red to yellow
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, timer_width, bar_height))

    # Draw click effects
    for effect in click_effects:
        color = effect.get('color', (0, 200, 0))
        text_surface = click_font.render(f"+{effect['value']}", True, color)
        text_surface.set_alpha(effect['alpha'])
        screen.blit(text_surface, (effect['x'], effect['y']))

    # Display cat counter
    text = font.render("cats: " + str(cats), True, (0, 0, 0))
    screen.blit(text, (10, 10))

    # Display click power
    power_text = pygame.font.SysFont(None, 30).render(f"Click Power: {click_power}", True, (0, 0, 0))
    screen.blit(power_text, (10, 60))

    # Draw prestige information
    prestige_text = pygame.font.SysFont(None, 24).render(f"Prestige Level: {prestige_level}", True, (0, 0, 0))
    screen.blit(prestige_text, (10, 90))

    points_text = pygame.font.SysFont(None, 24).render(f"Prestige Points: {prestige_points}", True, (0, 0, 0))
    screen.blit(points_text, (10, 120))

    # Draw restart button
    restart_x = 10
    restart_y = screen_height - 50
    restart_width = 100
    restart_height = 40

    pygame.draw.rect(screen, (255, 100, 100), (restart_x, restart_y, restart_width, restart_height))
    pygame.draw.rect(screen, (0, 0, 0), (restart_x, restart_y, restart_width, restart_height), 2)

    restart_text = pygame.font.SysFont(None, 24).render("RESTART", True, (0, 0, 0))
    text_rect = restart_text.get_rect(center=(restart_x + restart_width//2, restart_y + restart_height//2))
    screen.blit(restart_text, text_rect)

    # Draw mute button (only if sound is enabled)
    if sound_enabled:
        mute_x = 120
        mute_y = screen_height - 50
        mute_width = 80
        mute_height = 40

        try:
            music_playing = pygame.mixer.music.get_busy()
        except:
            music_playing = False

        mute_color = (150, 150, 255) if music_playing else (255, 150, 150)
        pygame.draw.rect(screen, mute_color, (mute_x, mute_y, mute_width, mute_height))
        pygame.draw.rect(screen, (0, 0, 0), (mute_x, mute_y, mute_width, mute_height), 2)

        mute_text = "UNMUTE" if not music_playing else "MUTE"
        mute_text_surface = pygame.font.SysFont(None, 20).render(mute_text, True, (0, 0, 0))
        mute_text_rect = mute_text_surface.get_rect(center=(mute_x + mute_width//2, mute_y + mute_height//2))
        screen.blit(mute_text_surface, mute_text_rect)

    # Draw prestige button
    prestige_x = 220
    prestige_y = screen_height - 50
    prestige_width = 120
    prestige_height = 40

    potential_points = calculate_prestige_points()

    prestige_color = (200, 200, 255) if potential_points > 0 else (200, 200, 200)
    pygame.draw.rect(screen, prestige_color, (prestige_x, prestige_y, prestige_width, prestige_height))
    pygame.draw.rect(screen, (0, 0, 0), (prestige_x, prestige_y, prestige_width, prestige_height), 2)

    prestige_text = pygame.font.SysFont(None, 20).render(f"Prestige ({potential_points})", True, (0, 0, 0))
    text_rect = prestige_text.get_rect(center=(prestige_x + prestige_width//2, prestige_y + prestige_height//2))
    screen.blit(prestige_text, text_rect)

    # Draw upgrade area
    upgrade_title = font.render("Upgrades", True, (0, 0, 0))
    screen.blit(upgrade_title, (screen_width - 200, 20))

    # Draw scroll indicators
    if upgrade_scroll > 0:
        scroll_up_text = pygame.font.SysFont(None, 20).render("↑ Scroll Up", True, (0, 0, 0))
        screen.blit(scroll_up_text, (screen_width - 200, 70))

    if upgrade_scroll < len(upgrades) - max_visible_upgrades:
        scroll_down_text = pygame.font.SysFont(None, 20).render("↓ Scroll Down", True, (0, 0, 0))
        screen.blit(scroll_down_text, (screen_width - 200, screen_height - 30))

    # Draw visible upgrades
    for i in range(max_visible_upgrades):
        if upgrade_scroll + i >= len(upgrades):
            break

        upgrade = upgrades[upgrade_scroll + i]
        upgrade_x = screen_width - 250
        upgrade_y = 100 + i * 120
        upgrade_width = 200
        upgrade_height = 100

        # Draw upgrade background
        color = (200, 255, 200) if cats >= upgrade['cost'] else (255, 200, 200)
        pygame.draw.rect(screen, color, (upgrade_x, upgrade_y, upgrade_width, upgrade_height))
        pygame.draw.rect(screen, (0, 0, 0), (upgrade_x, upgrade_y, upgrade_width, upgrade_height), 2)

        # Draw upgrade icon
        icon = load_image(upgrade['icon'], (60, 60))
        screen.blit(icon, (upgrade_x + 10, upgrade_y + 10))

        # Draw upgrade text
        name_text = pygame.font.SysFont(None, 24).render(upgrade['name'], True, (0, 0, 0))
        screen.blit(name_text, (upgrade_x + 80, upgrade_y + 10))

        desc_text = pygame.font.SysFont(None, 16).render(upgrade['description'][:30] + "...", True, (0, 0, 0))
        screen.blit(desc_text, (upgrade_x + 80, upgrade_y + 30))

        cost_text = pygame.font.SysFont(None, 20).render(f"Cost: {upgrade['cost']}", True, (0, 0, 0))
        screen.blit(cost_text, (upgrade_x + 80, upgrade_y + 50))

        owned_text = pygame.font.SysFont(None, 20).render(f"Owned: {upgrade['owned']}", True, (0, 0, 0))
        screen.blit(owned_text, (upgrade_x + 80, upgrade_y + 70))

        # Draw tier upgrade button
        upgrade_name = upgrade['name']
        if (upgrade_name in upgrade_tiers and 
            unlocked_tiers[upgrade_name] < len(upgrade_tiers[upgrade_name])):

            tier_x = upgrade_x + upgrade_width + 10
            tier_y = upgrade_y + 35
            tier_width = 30
            tier_height = 30

            tier_color = (200, 255, 200) if cats >= upgrade['cost'] * 10 else (255, 200, 200)
            pygame.draw.rect(screen, tier_color, (tier_x, tier_y, tier_width, tier_height))
            pygame.draw.rect(screen, (0, 0, 0), (tier_x, tier_y, tier_width, tier_height), 2)

            tier_text = pygame.font.SysFont(None, 20).render("T", True, (0, 0, 0))
            tier_text_rect = tier_text.get_rect(center=(tier_x + tier_width//2, tier_y + tier_height//2))
            screen.blit(tier_text, tier_text_rect)

    # Draw advanced upgrades (prestige shop)
    if prestige_level > 0:
        adv_title = font.render("Advanced Upgrades", True, (0, 0, 0))
        screen.blit(adv_title, (screen_width - 240, 100 + len(upgrades) * 60))

        for i, upgrade in enumerate(advanced_upgrades):
            adv_x = screen_width - 250
            adv_y = 100 + (len(upgrades) + i + 1) * 60
            adv_width = 240
            adv_height = 50

            # Draw advanced upgrade background
            adv_color = (200, 255, 200) if prestige_points >= upgrade['cost'] else (255, 200, 200)
            pygame.draw.rect(screen, adv_color, (adv_x, adv_y, adv_width, adv_height))
            pygame.draw.rect(screen, (0, 0, 0), (adv_x, adv_y, adv_width, adv_height), 2)

            # Draw advanced upgrade text
            name_text = pygame.font.SysFont(None, 20).render(upgrade['name'], True, (0, 0, 0))
            screen.blit(name_text, (adv_x + 10, adv_y + 5))

            desc_text = pygame.font.SysFont(None, 14).render(upgrade['description'][:30] + "...", True, (0, 0, 0))
            screen.blit(desc_text, (adv_x + 10, adv_y + 25))

            cost_text = pygame.font.SysFont(None, 16).render(f"Cost: {upgrade['cost']}", True, (0, 0, 0))
            screen.blit(cost_text, (adv_x + 10, adv_y + 40))

    # Update the display
    pygame.display.flip()
    clock.tick(60)  # 60 FPS for smooth animation
#make sure the game buttons like restart and the prestiege button still display

# Quit Pygame
pygame.quit()