import boopy, screeninfo, math

def calc_screen_size():
    screen = screeninfo.get_monitors()[0]
    width, height = screen.width, screen.height
    target_height = 18*8

    return int(width / (height / target_height)), target_height

screen_width, screen_height = calc_screen_size()
gravity = 0.13
min_tile_height = 10

left_key = [boopy.K_a, boopy.K_LEFT]
right_key = [boopy.K_d, boopy.K_RIGHT]
up_key = [boopy.K_w, boopy.K_SPACE, boopy.K_UP]
down_key = [boopy.K_s, boopy.K_DOWN]

class Location:
    def __init__(self, name:str, camera_follow, camera_offset_x, camera_offset_y) -> None:
        self.name = name
        self.camera_follow = camera_follow
        self.camera_offset_x = camera_offset_x
        self.camera_offset_y = camera_offset_y

    def load(self):
        tilemap_collision = boopy.Tilemap(environment_spritesheet, boopy.get_csv_file_as_lists(f"map/{self.name}_Collision.csv"),(255,0,0))
        tilemap_decoration = boopy.Tilemap(environment_spritesheet, boopy.get_csv_file_as_lists(f"map/{self.name}_Decoration.csv"),(255,0,0))
        tilemap_singleway = boopy.Tilemap(environment_spritesheet, boopy.get_csv_file_as_lists(f"map/{self.name}_Single Way Collision.csv"),(255,0,0))

        return tilemap_collision, tilemap_decoration, tilemap_singleway

class Locations:
    ingotown = Location("ingotown",True,0,-130)
    testtown = Location("ingotown",False,-130,-130)

class Player:
    def __init__(self) -> None:
        self.x = 15 * 8
        self.y = 19 * 8
        self.speed = 1
        self.velocity_y = 0
        self.jump_force = 2
        self.sprite = 0
    
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
                tile = tilemap_collision.get_tile(tile_x, tile_y)
                if debug:
                    sx, sy = world_to_screen(tile_x*8, tile_y*8)
                    boopy.draw_rect(sx, sy, sx+8, sy+8, (133,0,133))
                if tile != -1:
                    return True
        
        return False
        

    def physics(self):
        self.velocity_y += gravity

    def move(self):
        new_x = self.x
        new_y = self.y
        if boopy.btn(right_key):
            new_x += self.speed
        if boopy.btn(left_key):
            new_x -= self.speed
        if boopy.btn(up_key) and self.grounded:
            self.velocity_y = -self.jump_force

        new_y += self.velocity_y
        
        # stop player from moving inside tiles on X axis
        if self.collides_with_tile(new_x, self.y):
            if new_x < self.x: # moving left
                new_x = (math.ceil(new_x/8))*8
            elif new_x > self.x: # moving right
                new_x = (int(new_x/8))*8

        # stop player from moving inside tiles on Y axis
        if self.collides_with_tile(new_x, new_y):
            if new_y < self.y: # moving up
                new_y = (math.ceil(new_y/8))*8
            elif new_y > self.y: # moving down
                new_y = (int(new_y/8))*8
            if self.velocity_y > 0:
                self.velocity_y = 0
            self.grounded = True
        else:
            self.grounded = False

        self.y = new_y
        self.x = new_x

environment_spritesheet = boopy.Spritesheet("assets.png", 8, 8)
character_spritesheet = boopy.Spritesheet("characters.png", 8, 8)
location = Locations.ingotown

tilemap_collision, tilemap_decoration, tilemap_singleway = location.load()

player = Player()

def world_to_screen(x, y):
    if location.camera_follow:
        return screen_width//2 - int(player.x) + x + location.camera_offset_x, screen_height//2 + y + location.camera_offset_y
    return screen_width//2 + x + location.camera_offset_x, screen_height//2 + y + location.camera_offset_y

def update():
    
    boopy.cls((104,204,255))

    tilemap_x, tilemap_y = world_to_screen(0,0)
    boopy.draw_tilemap(tilemap_x, tilemap_y,tilemap_decoration)
    boopy.draw_tilemap(tilemap_x, tilemap_y,tilemap_collision)
    boopy.draw_tilemap(tilemap_x, tilemap_y,tilemap_singleway)

    if location.camera_follow:
        boopy.draw_spritesheet(screen_width//2 + location.camera_offset_x, screen_height//2+ player.y + location.camera_offset_y, character_spritesheet, player.sprite)
    else:
        boopy.draw_spritesheet(screen_width//2 +player.x + location.camera_offset_x, screen_height//2 + player.y + location.camera_offset_y, character_spritesheet, player.sprite)
    
    player.physics()
    player.move()
    boopy.draw_text(0,0,f"FPS: {boopy.get_fps()}")

boopy.run(update, screen_width=screen_width, screen_height=screen_height, fullscreen=True, fps_cap=None, vsync=True)