import boopy, screeninfo, math

def calc_screen_size():
    screen = screeninfo.get_monitors()[0]
    width, height = screen.width, screen.height
    target_height = 12*8

    return int(width / (height / target_height)), target_height

screen_width, screen_height = calc_screen_size()
gravity = 0.3
min_tile_height = 10

class Player:
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.speed = 1
        self.velocity_y = 0
        self.jump_force = 3
        self.sprite = 0
    
    def collides_with_tile(self,x , y, debug=False):
        tile_x = round(x / 8)
        tile_y = math.ceil(y / 8)
        tile = tilemap_collision.get_tile(tile_x, tile_y)
        if debug:
            boopy.draw_rect(screen_width//2 - self.x + tile_x*8, screen_height//2 - self.y + tile_y*8, screen_width//2 - self.x + tile_x*8 + 8, screen_height//2 - self.y + tile_y*8 + 8)
        return tile != -1
        

    def physics(self):
        self.grounded = self.collides_with_tile(self.x, self.y + 1)
        if not self.grounded:
            self.velocity_y += gravity
        else:
            if self.velocity_y > 0:
                self.velocity_y = 0

    def move(self):
        if boopy.btn(boopy.K_d):
            self.x += 1
        if boopy.btn(boopy.K_a):
            self.x -= 1
        if boopy.btn(boopy.K_SPACE) and self.grounded:
            self.velocity_y = -self.jump_force

        new_y = self.y + self.velocity_y
        self.y = new_y
        if self.collides_with_tile(self.x, new_y, False):
            self.y = (math.ceil(new_y / 8) - 1)*8
            # if new physics update will result in player inside the ground, then only take the player to the ground

environment_spritesheet = boopy.Spritesheet("assets.png", 8, 8)
character_spritesheet = boopy.Spritesheet("characters.png", 8, 8)

tilemap_collision = boopy.Tilemap(environment_spritesheet, boopy.get_csv_file_as_lists("map/ingotown/ingotown_Collision.csv"),(255,0,0))
tilemap_decoration = boopy.Tilemap(environment_spritesheet, boopy.get_csv_file_as_lists("map/ingotown/ingotown_Decoration.csv"),(255,0,0))

player = Player()

def update():
    player.physics()
    player.move()
    boopy.cls((104,204,255))

    boopy.draw_tilemap(screen_width//2 - player.x,screen_height//2 - player.y,tilemap_decoration)
    boopy.draw_tilemap(screen_width//2 - player.x,screen_height//2 - player.y,tilemap_collision)
    boopy.draw_spritesheet(screen_width//2, screen_height//2, character_spritesheet, player.sprite)

boopy.run(update, screen_width=screen_width, screen_height=screen_height)