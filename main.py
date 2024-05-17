import boopy, screeninfo, math

def calc_screen_size():
    screen = screeninfo.get_monitors()[0]
    width, height = screen.width, screen.height
    target_height = 18*8

    return int(width / (height / target_height)), target_height

screen_width, screen_height = calc_screen_size()

gravity = 0.13
deceleration_x = 1.4

left_key = [boopy.K_a, boopy.K_LEFT]
right_key = [boopy.K_d, boopy.K_RIGHT]
up_key = [boopy.K_w, boopy.K_SPACE, boopy.K_UP]
down_key = [boopy.K_s, boopy.K_DOWN]
sprint_key = [boopy.K_LSHIFT]

class Location:
    def __init__(self, name:str, camera_follow, camera_offset_x, camera_offset_y, start_tile_x, start_tile_y) -> None:
        self.name = name
        self.camera_follow = camera_follow
        self.camera_offset_x = camera_offset_x
        self.camera_offset_y = camera_offset_y
        self.start_tile_x = start_tile_x
        self.start_tile_y = start_tile_y

    def load(self):
        tilemap_collision = boopy.Tilemap(environment_spritesheet, boopy.get_csv_file_as_lists(f"map/{self.name}_Collision.csv"),(255,0,0))
        tilemap_decoration = boopy.Tilemap(environment_spritesheet, boopy.get_csv_file_as_lists(f"map/{self.name}_Decoration.csv"),(255,0,0))
        tilemap_singleway = boopy.Tilemap(environment_spritesheet, boopy.get_csv_file_as_lists(f"map/{self.name}_Single Way Collision.csv"),(255,0,0))
        player.x = self.start_tile_x * 8
        player.y = self.start_tile_y * 8

        return tilemap_collision, tilemap_decoration, tilemap_singleway

class Tiletype:
    decoration=0
    collision=1
    singleway=2

class Locations:
    ingotown = Location("ingotown",True,0,-130,15,19)
    testtown = Location("ingotown",False,-130,-130,15,19)

class Character:
    def __init__(self, x, y, sprite) -> None:
        self.x = x
        self.y = y
        self.speed = 1
        self.velocity_x = 0
        self.velocity_y = 0
        self.jump_force = 2
        self.sprite = sprite

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
        

class Player(Character):
    def __init__(self) -> None:
        super().__init__(0,0,0)
        self.speed = 0.3
        self.sprint_speed_multiplier = 3

    def physics(self):
        new_x = self.x
        new_y = self.y

        self.velocity_x = clamp(self.velocity_x, -7, 7)
        if -0.1 < self.velocity_x < 0.1:
            self.velocity_x = 0

        velocity_y = self.velocity_y
        velocity_x = round(self.velocity_x)

        new_y += velocity_y
        new_x += velocity_x
        
        # stop player from moving inside tiles on X axis
        colliding_tile = self.collides_with_tile(new_x, self.y)
        if colliding_tile:
            if new_x < self.x: # moving left
                new_x = (math.ceil(new_x/8))*8
            elif new_x > self.x: # moving right
                new_x = (int(new_x/8))*8

        # stop player from moving inside tiles on Y axis
        colliding_tile = self.collides_with_tile(new_x, new_y)
        if colliding_tile:
            if new_y < self.y: # moving up
                new_y = (math.ceil(new_y/8))*8
            elif new_y > self.y: # moving down
                new_y = (int(new_y/8))*8
                self.grounded = True
            self.velocity_y = 0

            # allow player to go downwards through singleway platform
            if colliding_tile == Tiletype.singleway:
                if boopy.btnp(down_key):
                    new_y += 5
                    self.grounded = False
        else:
            self.grounded = False

        self.y = new_y
        self.x = new_x

        self.velocity_y += gravity
        self.velocity_x /= deceleration_x

    def move(self):
        sprint = self.sprint_speed_multiplier if boopy.btn(sprint_key) else 1
        if boopy.btn(right_key):
            self.velocity_x += self.speed * sprint
        if boopy.btn(left_key):
            self.velocity_x -= self.speed * sprint
        if boopy.btn(up_key) and self.grounded:
            self.velocity_y = -self.jump_force

environment_spritesheet = boopy.Spritesheet("assets.png", 8, 8)
character_spritesheet = boopy.Spritesheet("characters.png", 8, 8)
location = Locations.ingotown

player = Player()

tilemap_collision, tilemap_decoration, tilemap_singleway = location.load()

def clamp(value, min_val, max_val):
    return max(min(value, max_val), min_val)

def world_to_screen(x, y):
    if location.camera_follow:
        sx = screen_width//2 - int(player.x) + x + location.camera_offset_x
        sy = screen_height//2 + y + location.camera_offset_y

        return sx, sy
    return screen_width//2 + x + location.camera_offset_x, screen_height//2 + y + location.camera_offset_y

def update():
    boopy.cls((104,204,255))

    tilemap_x, tilemap_y = world_to_screen(0,0)
    boopy.draw_tilemap(tilemap_x, tilemap_y,tilemap_decoration)
    boopy.draw_tilemap(tilemap_x, tilemap_y,tilemap_collision)
    boopy.draw_tilemap(tilemap_x, tilemap_y,tilemap_singleway)

    
    px, py = world_to_screen(player.x, player.y)
    boopy.draw_spritesheet(px, py, character_spritesheet, player.sprite)
    boopy.draw_text(0,0,f"FPS: {boopy.get_fps()}")
    
    player.move()
    player.physics()

boopy.run(update, screen_width=screen_width, screen_height=screen_height, fullscreen=False, fps_cap=None, vsync=True)