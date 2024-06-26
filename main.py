import boopy, screeninfo, math

def calc_screen_size():
    screen = screeninfo.get_monitors()[0]
    width, height = screen.width, screen.height
    target_height = 18*8

    return int(width / (height / target_height)), target_height

screen_width, screen_height = calc_screen_size()

gravity = 0.13
deceleration_x = 1.4

text_time = 160

left_key = [boopy.K_a, boopy.K_LEFT]
right_key = [boopy.K_d, boopy.K_RIGHT]
up_key = [boopy.K_w, boopy.K_SPACE, boopy.K_UP]
down_key = [boopy.K_s, boopy.K_DOWN]
sprint_key = [boopy.K_LSHIFT, boopy.K_RSHIFT]
interact_key = [boopy.K_e, boopy.K_RETURN]
attack_key = [boopy.K_f]

class Location:
    def __init__(self, name:str, camera_follow, camera_offset_x, camera_offset_y, start_tile_x, start_tile_y, characters) -> None:
        self.name = name
        self.camera_follow = camera_follow
        self.camera_offset_x = camera_offset_x
        self.camera_offset_y = camera_offset_y
        self.start_tile_x = start_tile_x
        self.start_tile_y = start_tile_y
        self.characters = characters

    def load(self):
        tilemap_collision = boopy.Tilemap(environment_spritesheet, boopy.get_csv_file_as_lists(f"map/{self.name}_Collision.csv"),(255,0,0))
        tilemap_decoration = boopy.Tilemap(environment_spritesheet, boopy.get_csv_file_as_lists(f"map/{self.name}_Decoration.csv"),(255,0,0))
        tilemap_singleway = boopy.Tilemap(environment_spritesheet, boopy.get_csv_file_as_lists(f"map/{self.name}_Single Way Collision.csv"),(255,0,0))
        player.x = self.start_tile_x * 8
        player.y = self.start_tile_y * 8

        return tilemap_collision, tilemap_decoration, tilemap_singleway, self.characters

class Tiletype:
    decoration=0
    collision=1
    singleway=2

class Character:
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.speed = 1
        self.velocity_x = 0
        self.velocity_y = 0
        self.jump_force = 2
        self.sprite = 0
        self.width = 1
        self.height = 1
        self.facing_left = False

        self.text_timer = 0
        self.text = ""

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x}, {self.y})"

    def say(self, text):
        self.text_timer = text_time
        self.text = text

    def interact(self):
        pass

    def physics(self):
        new_x = self.x
        new_y = self.y

        if self.velocity_x < 0:
            self.facing_left = True
        elif self.velocity_x > 0:
            self.facing_left = False

        self.velocity_x = clamp(self.velocity_x, -7, 7)
        if -0.1 < self.velocity_x < 0.1:
            self.velocity_x = 0

        velocity_y = self.velocity_y
        velocity_x = round(self.velocity_x)

        new_y += velocity_y
        new_x += velocity_x

        # stop character from moving inside tiles on X axis
        colliding_tile = self.collides_with_tile(new_x, self.y)
        if colliding_tile:
            if new_x < self.x: # moving left
                new_x = (math.ceil(new_x/8))*8
            elif new_x > self.x: # moving right
                new_x = (int(new_x/8))*8

        # stop character from moving inside tiles on Y axis
        colliding_tile = self.collides_with_tile(new_x, new_y)
        if colliding_tile:
            if new_y < self.y: # moving up
                new_y = (math.ceil(new_y/8))*8
            elif new_y > self.y: # moving down
                new_y = (int(new_y/8))*8
                self.grounded = True
                self.ground_type = colliding_tile
            self.velocity_y = 0
        else:
            self.grounded = False
            self.ground_type = -1

        self.y = new_y
        self.x = new_x

        self.velocity_y += gravity
        self.velocity_x /= deceleration_x

    def get_interactable_npc(self):
        x_offset = -8 if self.facing_left else 8
        for character in characters+[player]:
            if character == self:
                continue
            if self.x + x_offset - 8 < character.x < self.x + x_offset + 8:
                if self.y + - 8 < character.y < self.y + 8:
                    return character

        return None

    def collides_with_tile(self, x, y, debug = False):
        tile_x_min = int(x / 8)
        tile_x_max = math.ceil(x / 8)
        tiles_x = [tile_x_min, tile_x_max]

        tile_y_min = int(y / 8)
        tile_y_max = math.ceil(y / 8)
        tiles_y = [tile_y_min, tile_y_max]

        # most of the time, the coordinate we're checking is between two or more tiles, therefore we check the tiles we're tied between.

        # in case the coordinate is not in between tiles, no need to check multiple
        if tile_x_min == tile_x_max:
            tiles_x = [tile_x_min]

        if tile_y_min == tile_y_max:
            tiles_y = [tile_y_min]

        for tile_x in tiles_x:
            for tile_y in tiles_y:
                if debug:
                    sx, sy = world_to_screen(tile_x*8, tile_y*8)
                    boopy.draw_rect(sx, sy, sx+8, sy+8, (44,77,244))

                tile = tilemap_collision.get_tile(tile_x, tile_y)
                if tile != -1:
                    return Tiletype.collision

                # check if there is a single way platform to collide with
                # but first check that the player is above it and traveling downwards
                if self.velocity_y > 0 and round(y/8) < tile_y:
                    tile = tilemap_singleway.get_tile(tile_x, tile_y)
                    if tile != -1:
                        return Tiletype.singleway

        return False

    def draw_speech_text(self):
            text_width, _ = boopy.get_text_size(self.text)
            sx, sy = world_to_screen(self.x - text_width // 2 + (self.width / 2 * 8), self.y - self.height*8)
            boopy.draw_rect(sx - 1, sy, sx + text_width + 2, sy + 10, (255,255,255))
            boopy.draw_text(sx + 1, sy - 4, self.text, (0,0,0))

    def update(self):
        if self.text_timer > 0:
            self.text_timer -= 1
            self.draw_speech_text()

class Birdman(Character):
    def __init__(self) -> None:
        super().__init__()
        self.sprite = 64
        self.x = 67 * 8
        self.y = 20 * 8
        self.width = 2
        self.height = 2

    def interact(self):
        self.say("lil guy, i'm busy")

class Characters:
    dave = Birdman()

class Locations:
    ingotown = Location("ingotown",True,0,-130,25,19,[Characters.dave])
    testtown = Location("ingotown",False,-130,-130,15,19,[])

class Player(Character):
    def __init__(self) -> None:
        super().__init__()
        self.sprite = 0
        self.speed = 0.3
        self.jump_force = 2.13
        self.sprint_speed_multiplier = 3

    def update(self):
        sprint = self.sprint_speed_multiplier if boopy.btn(sprint_key) else 1
        if boopy.btn(right_key):
            self.velocity_x += self.speed * sprint
        if boopy.btn(left_key):
            self.velocity_x -= self.speed * sprint
        if boopy.btn(up_key) and self.grounded:
            self.velocity_y = -self.jump_force

        if boopy.btnp(down_key) and self.ground_type == 2:
            self.y += 5
            self.grounded = False
            self.ground_type = -1

        interactable_npc = self.get_interactable_npc()
        if boopy.btnp(interact_key):
            if interactable_npc:
                interactable_npc.interact()

environment_spritesheet = boopy.Spritesheet("assets.png", 8, 8)
character_spritesheet = boopy.Spritesheet("characters.png", 8, 8)
location = Locations.ingotown

player = Player()

tilemap_collision, tilemap_decoration, tilemap_singleway, characters = location.load()

def clamp(value, min_val, max_val):
    return max(min(value, max_val), min_val)

def world_to_screen(x, y):
    if location.camera_follow:
        offset_x = location.camera_offset_x
        if player.x < screen_width // 2 + location.camera_offset_x:
            offset_x = player.x - (screen_width // 2)
        elif player.x > tilemap_collision.map_width * 8 - screen_width // 2 + location.camera_offset_x:
            offset_x = player.x - (tilemap_collision.map_width * 8 - screen_width // 2)
        else:
            offset_x = location.camera_offset_x


        sx = screen_width // 2 - int(player.x) + x + offset_x
        sy = screen_height // 2 + y + location.camera_offset_y

        return sx, sy
    return screen_width // 2 + x + location.camera_offset_x, screen_height // 2 + y + location.camera_offset_y

def update():
    boopy.cls((104,204,255))

    tilemap_x, tilemap_y = world_to_screen(0,0)
    boopy.draw_tilemap(tilemap_x, tilemap_y,tilemap_decoration)
    boopy.draw_tilemap(tilemap_x, tilemap_y,tilemap_collision)
    boopy.draw_tilemap(tilemap_x, tilemap_y,tilemap_singleway)

    for character in characters+[player]:
        for x in range(character.width):
            for y in range(character.height):
                px, py = world_to_screen(character.x + x*8, character.y + y*8 - (character.height-1) * 8)
                tx, ty = character_spritesheet.get_sprite_coordinate_by_index(character.sprite)
                boopy.draw_spritesheet_from_coordinate(px, py, character_spritesheet, tx + x, ty + y)

        character.update()
        character.physics()
    boopy.draw_text(0,0,f"FPS: {boopy.get_fps()}")

boopy.run(update, screen_width=screen_width, screen_height=screen_height, fullscreen=False, fps_cap=None, vsync=True)
