import sys
import subprocess

def ensure_requirements():
    required = ["pygame", "numpy", "Pillow"]
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            print(f"Installing missing package: {pkg}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# Ensure requirements before anything else
ensure_requirements()

# Initialize Pygame
import pygame
import math
import random
import time
import json
import os
from PIL import Image, ImageDraw
import numpy as np
import threading
import socket

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

# --- UI COLORS & STYLES ---
BG_COLOR = (245, 245, 255)
BUTTON_COLOR = (120, 180, 255)
BUTTON_HOVER = (100, 160, 230)
BUTTON_TEXT = (30, 30, 60)
SHADOW_COLOR = (200, 200, 220)
CHAT_BG = (255, 255, 255)
CHAT_BORDER = (180, 180, 200)
CHAT_TEXT = (40, 40, 40)

# --- IN-SCRIPT SOUND EFFECTS ---
def generate_beep(frequency=440, duration=0.1, volume=0.5):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(frequency * t * 2 * np.pi)
    audio = (tone * 32767 * volume).astype(np.int16)
    sound = pygame.sndarray.make_sound(audio)
    return sound

def generate_chime():
    return generate_beep(880, 0.15, 0.4)

def generate_click():
    return generate_beep(660, 0.05, 0.3)

# Use generated sounds
click_sound = generate_click()
purchase_sound = generate_chime()
rainbow_click_sound = generate_beep(1200, 0.12, 0.4)

# --- MULTIPLAYER STRUCTURE ---
multiplayer_mode = False
multiplayer_host = False
join_code = ''
chat_messages = []
chat_input = ''
chat_active = False
player_id = None
player_progress = {}
multiplayer_socket = None
multiplayer_thread = None

# --- MULTIPLAYER NETWORKING ---
def start_multiplayer_server():
    global multiplayer_socket, join_code, player_id, player_progress
    multiplayer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    multiplayer_socket.bind(('0.0.0.0', 0))
    multiplayer_socket.listen(5)
    join_code = str(multiplayer_socket.getsockname()[1])  # Use port as join code
    player_id = 'host'
    player_progress[player_id] = save_current_progress()
    threading.Thread(target=accept_clients, daemon=True).start()

def accept_clients():
    while True:
        client, addr = multiplayer_socket.accept()
        threading.Thread(target=handle_client, args=(client,), daemon=True).start()

def handle_client(client):
    global player_progress
    client_id = client.recv(1024).decode()
    player_progress[client_id] = save_current_progress()
    while True:
        try:
            data = client.recv(4096)
            if not data:
                break
            msg = data.decode()
            if msg.startswith('CHAT:'):
                chat_messages.append(msg[5:])
            elif msg.startswith('PROGRESS:'):
                # Update progress for this client
                player_progress[client_id] = json.loads(msg[9:])
        except:
            break
    client.close()
    del player_progress[client_id]

def connect_to_multiplayer_server(code):
    global multiplayer_socket, player_id, player_progress
    multiplayer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    multiplayer_socket.connect(('127.0.0.1', int(code)))
    player_id = f'player{random.randint(1000,9999)}'
    multiplayer_socket.sendall(player_id.encode())
    player_progress[player_id] = save_current_progress()
    threading.Thread(target=listen_to_server, daemon=True).start()

def listen_to_server():
    while True:
        try:
            data = multiplayer_socket.recv(4096)
            if not data:
                break
            msg = data.decode()
            if msg.startswith('CHAT:'):
                chat_messages.append(msg[5:])
            elif msg.startswith('PROGRESS:'):
                # Update progress for all players
                all_progress = json.loads(msg[9:])
                for pid, prog in all_progress.items():
                    player_progress[pid] = prog
        except:
            break

def save_current_progress():
    return {
        'cats': cats,
        'upgrades': upgrades,
        'click_power': click_power,
        'prestige_level': prestige_level,
        'prestige_points': prestige_points,
        'base_cats_for_prestige': base_cats_for_prestige,
        'unlocked_tiers': unlocked_tiers,
        'advanced_upgrades': advanced_upgrades
    }

def restore_progress(progress):
    global cats, upgrades, click_power, prestige_level, prestige_points, base_cats_for_prestige, unlocked_tiers, advanced_upgrades
    cats = progress['cats']
    upgrades = progress['upgrades']
    click_power = progress['click_power']
    prestige_level = progress['prestige_level']
    prestige_points = progress['prestige_points']
    base_cats_for_prestige = progress['base_cats_for_prestige']
    unlocked_tiers = progress['unlocked_tiers']
    advanced_upgrades = progress['advanced_upgrades']

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

# Add game state for menu navigation
show_prestige_menu = False
cat_army_timer = 0
cat_portal_timer = 0
cat_army_burst = 0
cat_portal_bonus = 0

# Add new upgrades
upgrades.extend([
    {
        'name': 'Cat Magnet',
        'description': 'Increases rainbow cat spawn chance',
        'cost': 2500,
        'owned': 0,
        'magnet_bonus': 1,
        'icon': 'cat_upgrade6.png'
    },
    {
        'name': 'Cat Army',
        'description': 'Gives a burst of 100 cats every minute',
        'cost': 5000,
        'owned': 0,
        'army_burst': 100,
        'icon': 'cat_upgrade7.png'
    },
    {
        'name': 'Cat Portal',
        'description': 'Gives a random bonus every 5 minutes',
        'cost': 20000,
        'owned': 0,
        'portal_bonus': 1,
        'icon': 'cat_upgrade8.png'
    }
])

# --- CATNIP & GARDEN SYSTEM ---
catnip = 0
catnip_planted = 0
catnip_grow_timer = 0
catnip_grow_time = 600  # 10 seconds per plant
catnip_max_plots = 6
in_garden_mode = False
catnip_boost_active = False
catnip_boost_timer = 0
catnip_boost_duration = 180  # 3 minutes (in seconds)

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
def load_cat_image(size=None):
    try:
        image = pygame.image.load("cat.png")
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except:
        # fallback: draw a simple cat face
        surface = pygame.Surface(size or (64, 64), pygame.SRCALPHA)
        pygame.draw.ellipse(surface, (255, 180, 100), (0, 0, surface.get_width(), surface.get_height()))
        pygame.draw.circle(surface, (0,0,0), (surface.get_width()//3, surface.get_height()//2), 6)
        pygame.draw.circle(surface, (0,0,0), (2*surface.get_width()//3, surface.get_height()//2), 6)
        pygame.draw.arc(surface, (0,0,0), (surface.get_width()//3, surface.get_height()//2, surface.get_width()//3, surface.get_height()//3), 3.14, 0, 2)
        return surface

# Scrolling variables
upgrade_scroll = 0
max_visible_upgrades = 4

# --- UI REFACTORING ---
def draw_rounded_rect(surface, color, rect, radius=12, border=0, border_color=(0,0,0)):
    x, y, w, h = rect
    pygame.draw.rect(surface, color, (x+radius, y, w-2*radius, h))
    pygame.draw.rect(surface, color, (x, y+radius, w, h-2*radius))
    pygame.draw.circle(surface, color, (x+radius, y+radius), radius)
    pygame.draw.circle(surface, color, (x+w-radius, y+radius), radius)
    pygame.draw.circle(surface, color, (x+radius, y+h-radius), radius)
    pygame.draw.circle(surface, color, (x+w-radius, y+h-radius), radius)
    if border:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)

# --- CHAT UI DRAWING ---
def draw_chat(surface, x, y, w, h, messages, input_text, active):
    pygame.draw.rect(surface, CHAT_BG, (x, y, w, h), border_radius=10)
    pygame.draw.rect(surface, CHAT_BORDER, (x, y, w, h), 2, border_radius=10)
    # Draw messages (last 8)
    font_chat = pygame.font.SysFont(None, 22)
    display_msgs = messages[-8:]
    for i, msg in enumerate(display_msgs):
        txt = font_chat.render(msg, True, CHAT_TEXT)
        surface.blit(txt, (x+10, y+10+i*22))
    # Draw input box
    input_y = y + h - 32
    pygame.draw.rect(surface, (240,240,255) if active else (220,220,220), (x+5, input_y, w-10, 26), border_radius=8)
    pygame.draw.rect(surface, CHAT_BORDER, (x+5, input_y, w-10, 26), 1, border_radius=8)
    input_txt = font_chat.render(input_text, True, (0,0,0))
    surface.blit(input_txt, (x+12, input_y+4))

# --- PLAYER LIST DRAWING ---
def draw_player_list(surface, x, y, w, h, players):
    pygame.draw.rect(surface, (255,255,255), (x, y, w, h), border_radius=10)
    pygame.draw.rect(surface, (180,180,200), (x, y, w, h), 2, border_radius=10)
    font_player = pygame.font.SysFont(None, 22)
    for i, pid in enumerate(players):
        txt = font_player.render(f"{pid}", True, (40,40,40))
        surface.blit(txt, (x+10, y+10+i*22))

# --- UI POLISH HELPERS ---
def draw_button(surface, rect, text, font, color, hover, border=2, radius=12):
    x, y, w, h = rect
    base = BUTTON_HOVER if hover else color
    pygame.draw.rect(surface, base, rect, border_radius=radius)
    pygame.draw.rect(surface, (60,60,90), rect, border, border_radius=radius)
    txt = font.render(text, True, BUTTON_TEXT)
    txt_rect = txt.get_rect(center=(x+w//2, y+h//2))
    surface.blit(txt, txt_rect)

def draw_tooltip(surface, text, pos):
    font_tip = pygame.font.SysFont(None, 20)
    tip = font_tip.render(text, True, (30,30,30))
    w, h = tip.get_size()
    pygame.draw.rect(surface, (255,255,220), (pos[0], pos[1]-h-8, w+12, h+8), border_radius=8)
    pygame.draw.rect(surface, (180,180,120), (pos[0], pos[1]-h-8, w+12, h+8), 1, border_radius=8)
    surface.blit(tip, (pos[0]+6, pos[1]-h-4))

# Game loop
running = True
while running:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    hovered_upgrade = None
    hovered_button = None
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game()  # Save before quitting
            running = False

        # --- GARDEN MODE TOGGLE ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                in_garden_mode = not in_garden_mode

        # --- GARDEN MODE EVENTS ---
        if in_garden_mode:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Plant catnip if empty plot clicked
                for i in range(catnip_max_plots):
                    plot_x = 120 + i*90
                    plot_y = screen_height//2
                    if (plot_x <= mouse_x <= plot_x+64 and plot_y <= mouse_y <= plot_y+64):
                        if catnip_planted < catnip_max_plots:
                            catnip_planted += 1
                            break
                # Harvest catnip if grown
                for i in range(catnip_planted):
                    plot_x = 120 + i*90
                    plot_y = screen_height//2
                    if (plot_x <= mouse_x <= plot_x+64 and plot_y <= mouse_y <= plot_y+64):
                        if catnip_grow_timer >= catnip_grow_time:
                            catnip += 1
                            catnip_planted -= 1
                            catnip_grow_timer = 0
                            break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                in_garden_mode = False
            continue  # Skip rest of event handling if in garden mode

        # --- MAIN GAME: USE CATNIP BOOST ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c and catnip > 0 and not catnip_boost_active:
                catnip -= 1
                catnip_boost_active = True
                catnip_boost_timer = catnip_boost_duration * 60  # convert to frames

    # --- GARDEN LOGIC ---
    if in_garden_mode and catnip_planted > 0:
        catnip_grow_timer += 1
        if catnip_grow_timer >= catnip_grow_time:
            catnip_grow_timer = catnip_grow_time  # Ready to harvest

    # --- CATNIP BOOST LOGIC ---
    if catnip_boost_active:
        catnip_boost_timer -= 1
        if catnip_boost_timer <= 0:
            catnip_boost_active = False

    # --- MAIN GAME LOGIC MODIFICATION ---
    boost_mult = 5 if catnip_boost_active else 1
    # When adding cats (clicks, auto), multiply by boost_mult
    # Example: cats += click_power * boost_mult
    # Example: cats += auto_cats * boost_mult

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
            cats += auto_cats * boost_mult
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

    # Cat Magnet: increase rainbow cat spawn chance
    magnet_bonus = sum(upg['owned'] * upg.get('magnet_bonus', 0) for upg in upgrades)
    effective_min = max(18000 - 1000 * magnet_bonus, 1000)
    effective_max = max(54000 - 2000 * magnet_bonus, 2000)
    # Only update spawn time if rainbow_cat_timer resets
    if rainbow_cat_timer == 0:
        rainbow_cat_spawn_time = random.randint(effective_min, effective_max)

    # Cat Army: burst every minute
    army_burst = sum(upg['owned'] * upg.get('army_burst', 0) for upg in upgrades)
    cat_army_timer += 1
    if cat_army_timer >= 3600:  # 1 minute at 60 FPS
        cat_army_timer = 0
        if army_burst > 0:
            cats += army_burst * boost_mult
            click_effects.append({'x': cat_x + scaled_size[0]//2, 'y': cat_y, 'alpha': 255, 'timer': 60, 'value': army_burst, 'color': (255, 100, 100)})

    # Cat Portal: random bonus every 5 minutes
    portal_bonus = sum(upg['owned'] * upg.get('portal_bonus', 0) for upg in upgrades)
    cat_portal_timer += 1
    if cat_portal_timer >= 18000:  # 5 minutes at 60 FPS
        cat_portal_timer = 0
        if portal_bonus > 0:
            bonus_type = random.choice(['cats', 'click_power', 'prestige'])
            if bonus_type == 'cats':
                cats += 500 * portal_bonus * boost_mult
                click_effects.append({'x': cat_x + scaled_size[0]//2, 'y': cat_y, 'alpha': 255, 'timer': 60, 'value': 500 * portal_bonus, 'color': (100, 100, 255)})
            elif bonus_type == 'click_power':
                click_power += 2 * portal_bonus
            elif bonus_type == 'prestige':
                prestige_points += 1 * portal_bonus

    # Draw everything
    # Draw background
    screen.fill((135, 206, 235))
    # Add your drawing code here
    #blit cat.png to the screen
    base_size = (screen_width//2.5, screen_height//2.5)
    scaled_size = (int(base_size[0] * cat_scale), int(base_size[1] * cat_scale))
    cat = load_cat_image(scaled_size)

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
        rainbow_cat_img = load_cat_image((rainbow_cat['size'], rainbow_cat['size']))

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

    # Draw upgrades with polish
    for i in range(max_visible_upgrades):
        if upgrade_scroll + i >= len(upgrades):
            break
        upgrade = upgrades[upgrade_scroll + i]
        upgrade_x = screen_width - 250
        upgrade_y = 100 + i * 120
        upgrade_width = 200
        upgrade_height = 100
        rect = (upgrade_x, upgrade_y, upgrade_width, upgrade_height)
        is_hover = (upgrade_x <= mouse_x <= upgrade_x+upgrade_width and upgrade_y <= mouse_y <= upgrade_y+upgrade_height)
        draw_button(screen, rect, upgrade['name'], pygame.font.SysFont(None, 24), (200,255,200) if cats >= upgrade['cost'] else (255,200,200), is_hover)
        # Draw upgrade icon (draw a colored circle instead of loading an image)
        icon_color = [(120,180,255), (255,200,100), (180,255,180), (255,120,120), (200,200,255), (255,255,120), (180,180,255), (255,180,255)][i%8]
        pygame.draw.circle(screen, icon_color, (upgrade_x+40, upgrade_y+40), 28)
        icon_txt = pygame.font.SysFont(None, 24).render(upgrade['name'][0], True, (40,40,40))
        screen.blit(icon_txt, (upgrade_x+28, upgrade_y+28))
        # Draw cost/owned
        cost_text = pygame.font.SysFont(None, 20).render(f"Cost: {upgrade['cost']}", True, (0, 0, 0))
        screen.blit(cost_text, (upgrade_x + 80, upgrade_y + 50))
        owned_text = pygame.font.SysFont(None, 20).render(f"Owned: {upgrade['owned']}", True, (0, 0, 0))
        screen.blit(owned_text, (upgrade_x + 80, upgrade_y + 70))
        if is_hover:
            hovered_upgrade = upgrade

    # Draw tooltips for upgrades
    if hovered_upgrade:
        draw_tooltip(screen, hovered_upgrade['description'], (mouse_x, mouse_y))

    # Draw buttons with polish
    draw_button(screen, (restart_x, restart_y, restart_width, restart_height), "RESTART", pygame.font.SysFont(None, 24), (255,100,100), restart_x <= mouse_x <= restart_x+restart_width and restart_y <= mouse_y <= restart_y+restart_height)
    if sound_enabled:
        draw_button(screen, (mute_x, mute_y, mute_width, mute_height), "MUTE" if music_playing else "UNMUTE", pygame.font.SysFont(None, 20), (150,150,255) if music_playing else (255,150,150), mute_x <= mouse_x <= mute_x+mute_width and mute_y <= mouse_y <= mute_y+mute_height)
    draw_button(screen, (prestige_x, prestige_y, prestige_width, prestige_height), f"Prestige ({potential_points})", pygame.font.SysFont(None, 20), prestige_color, prestige_x <= mouse_x <= prestige_x+prestige_width and prestige_y <= mouse_y <= prestige_y+prestige_height)

    # Draw catnip boost status with polish
    if catnip_boost_active:
        boost_time_left = catnip_boost_timer // 60
        draw_button(screen, (screen_width//2-120, 10, 240, 40), f"CATNIP BOOST! {boost_time_left}s", pygame.font.SysFont(None, 32), (180,255,180), False)

    # Draw catnip garden if in garden mode
    if in_garden_mode:
        # Draw garden background
        screen.fill((180, 255, 180))
        garden_title = font.render("Catnip Garden", True, (40, 80, 40))
        screen.blit(garden_title, (screen_width//2 - 120, 40))
        # Draw plots
        for i in range(catnip_max_plots):
            plot_x = 120 + i*90
            plot_y = screen_height//2
            is_hover = (plot_x <= mouse_x <= plot_x+64 and plot_y <= mouse_y <= plot_y+64)
            pygame.draw.rect(screen, (120, 200, 120), (plot_x, plot_y, 64, 64), border_radius=12)
            if i < catnip_planted:
                # Growing or ready
                if catnip_grow_timer >= catnip_grow_time:
                    pygame.draw.ellipse(screen, (80, 255, 80), (plot_x+12, plot_y+12, 40, 40))
                    ready_txt = pygame.font.SysFont(None, 18).render("Ready!", True, (0,80,0))
                    screen.blit(ready_txt, (plot_x+8, plot_y+48))
                else:
                    pygame.draw.ellipse(screen, (120, 220, 120), (plot_x+16, plot_y+20, 32, 28))
                    grow_txt = pygame.font.SysFont(None, 16).render(f"{(catnip_grow_time-catnip_grow_timer)//60}s", True, (0,80,0))
                    screen.blit(grow_txt, (plot_x+16, plot_y+48))
            if is_hover:
                draw_tooltip(screen, "Click to plant/harvest catnip", (mouse_x, mouse_y))
        catnip_txt = pygame.font.SysFont(None, 32).render(f"Catnip: {catnip}", True, (0, 100, 0))
        screen.blit(catnip_txt, (screen_width//2 - 60, screen_height - 80))
        instr = pygame.font.SysFont(None, 20).render("Click empty plot to plant, grown plot to harvest. ESC to exit.", True, (0,0,0))
        screen.blit(instr, (screen_width//2 - 180, screen_height - 40))
        pygame.display.flip()
        clock.tick(60)
        continue

    # Update the display
    pygame.display.flip()
    clock.tick(60)  # 60 FPS for smooth animation
#make sure the game buttons like restart and the prestiege button still display

# Quit Pygame
pygame.quit()