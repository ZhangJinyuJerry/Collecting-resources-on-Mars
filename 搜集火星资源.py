import random
import arcade
import datetime
import math
import os
from RLDungeonGenerator import RLDungeonGenerator,Room
import time

'''用于缩小放大物体的比例尺'''
WALL_SPRITE_SCALING = 1
PLAYER_SPRITE_SCALING = 0.15
MATERIAL_SPRITE_SCALING  = 1
ALIEN_SPRITE_SCALING = 0.2
WALL_SPRITE_SIZE = int(100 * WALL_SPRITE_SCALING)

'''迷宫大小'''
'''数值越大，迷宫越大'''
GRID_WIDTH = 50
GRID_HEIGHT = 20

AREA_WIDTH = GRID_WIDTH * WALL_SPRITE_SIZE
AREA_HEIGHT = GRID_HEIGHT * WALL_SPRITE_SIZE

CAVE_MAX_SIZE = 10 #洞穴大小的最大值，数值越大，空间的尺寸就越大

'''小地图参数'''
MAP_WIDTH = 200
MAP_HEIGHT = 150
MAP_SCALE = 4

'''移动速度'''
MOVEMENT_SPEED = 5

'''玩家与窗口边界的最小距离'''
VIEWPORT_MARGIN = 300

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "火星探索"

'''晶石数量'''
NUM_MATERIALS = 10
class InstructionView(arcade.View):
    global start_time
    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture("封面.png")
    def on_draw(self):
        self.window.clear()
        def on_draw(self):
            arcade.start_render()
            arcade.draw_texture_rectangle(
                WINDOW_WIDTH / 2, 
                WINDOW_HEIGHT / 2, 
                self.texture.width, 
                self.texture.height, 
                self.texture, 
                0
            )
        on_draw(self)
        # self.texture.draw(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
        #                         WINDOW_WIDTH, WINDOW_HEIGHT)
        arcade.draw_text("搜集火星资源", self.window.width / 2, self.window.height / 2,
                         arcade.color.WHITE, font_size=50, anchor_x="center",font_name='5013.ttf')
        arcade.draw_text("点击屏幕 开始探索", self.window.width / 2, self.window.height / 2-75, 
                         arcade.color.WHITE, font_size=20, anchor_x="center", font_name='5013.ttf')

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        global start_time
        '''如果用户点击按钮，则跳转到游戏主界面'''
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)
        start_time = datetime.datetime.now()

class GameOverView(arcade.View):
    def __init__(self):
        super().__init__()
        
        '''设计游戏结局封面'''
        self.texture = arcade.load_texture("结局.png")
        arcade.set_viewport(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

    def on_draw(self):
        self.window.clear()
        def on_draw(self):
            arcade.start_render()
            arcade.draw_texture_rectangle(
                WINDOW_WIDTH / 2, 
                WINDOW_HEIGHT / 2, 
                self.texture.width, 
                self.texture.height, 
                self.texture, 
                0
            )
        on_draw(self)
        # self.texture.draw(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
        #                         WINDOW_WIDTH, WINDOW_HEIGHT)
    '''重开游戏'''
    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)
    

class GameLoseOverView(arcade.View):
    def __init__(self):
        super().__init__()
        
        '''设计游戏结局封面'''
        self.texture = arcade.load_texture("结局失败.png")
        arcade.set_viewport(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

    def on_draw(self):
        self.window.clear()
        def on_draw(self):
            arcade.start_render()
            arcade.draw_texture_rectangle(
                WINDOW_WIDTH / 2, 
                WINDOW_HEIGHT / 2, 
                self.texture.width, 
                self.texture.height, 
                self.texture, 
                0
            )
        on_draw(self)
        # self.texture.draw(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
        #                         WINDOW_WIDTH, WINDOW_HEIGHT)
    '''重开游戏'''
    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)

class GameView(arcade.View):
    global start_time
    global time_text
    def __init__(self):
        super().__init__()
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.grid = None
        self.wall_list = None
        self.player_list = None
        
        self.player_sprite = None
        self.view_bottom = 0
        self.view_left = 0
        self.physics_engine = None
        
        self.material_list = None

        '''获得的晶石数量'''
        self.collect_materials = 0
        
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        '''设置墙壁、玩家、晶石'''
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.player_list = arcade.SpriteList()
        self.material_list = arcade.SpriteList()
        self.alien_list = arcade.SpriteList()
        
        '''随机生成地图，不需要了解具体实现原理'''
        dg = RLDungeonGenerator(GRID_WIDTH, GRID_HEIGHT,CAVE_MAX_SIZE)
        dg.generate_map()
        
        '''根据生成的地图在指定位置放置砖块'''
        for row in range(dg.height):
            for column in range(dg.width):
                value = dg.dungeon[row][column]
                if value == '#':
                    wall = arcade.Sprite("砖块.gif", WALL_SPRITE_SCALING)
                    wall.center_x = column * WALL_SPRITE_SIZE + WALL_SPRITE_SIZE / 2
                    wall.center_y = row * WALL_SPRITE_SIZE + WALL_SPRITE_SIZE / 2
                    self.wall_list.append(wall)

        '''设置宇航员的外观'''
        self.player_sprite = arcade.Sprite("宇航员.gif",
                                           PLAYER_SPRITE_SCALING)
        
        self.player_list.append(self.player_sprite)
        '''随机放置宇航员，如果放的位置是墙壁，则循环执行放置操作，直到宇航员不在墙内'''
        placed = False
        while not placed:
            self.player_sprite.center_x = random.randrange(AREA_WIDTH)
            self.player_sprite.center_y = random.randrange(AREA_HEIGHT)
            '''使用碰撞检测是否在墙内'''
            walls_hit = arcade.check_for_collision_with_list(self.player_sprite, self.wall_list)
            if len(walls_hit) == 0:
                '''碰撞实体数量为0，说明不在墙内'''
                placed = True
        
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite,
                                                         self.wall_list)

        for _ in range(NUM_MATERIALS):
            material_sprite = arcade.Sprite("能源晶石.gif",
                                               MATERIAL_SPRITE_SCALING)
            '''随机放置晶石'''
            material_placed = False
            while not material_placed:
                material_sprite.center_x = random.randrange(AREA_WIDTH)
                material_sprite.center_y = random.randrange(AREA_HEIGHT)
                walls_hit = arcade.check_for_collision_with_list(material_sprite, self.wall_list)
                if len(walls_hit) == 0:
                    material_placed = True
            self.material_list.append(material_sprite)


        for _ in range(NUM_MATERIALS):
            alien_sprite = arcade.Sprite("外星人.gif",
                                               ALIEN_SPRITE_SCALING)
            '''随机放置外星人'''
            alien_placed = False
            while not alien_placed:
                alien_sprite.center_x = random.randrange(AREA_WIDTH)
                alien_sprite.center_y = random.randrange(AREA_HEIGHT)
                colliding_sprites = arcade.check_for_collision_with_list(alien_sprite, self.wall_list, 100)
                if colliding_sprites:
                    print("Collisions detected!")
                    for sprite in colliding_sprites:
                        print(f"Collided with {sprite}")
                else:
                    print("No collisions detected.")
                    alien_placed = True
            self.alien_list.append(alien_sprite)
            
    '''绘制小地图'''
    def draw_mini_map(self):   
        arcade.draw_rectangle_filled(
            self.view_left + WINDOW_WIDTH - MAP_WIDTH//2 - 10,
            self.view_bottom + WINDOW_HEIGHT - MAP_HEIGHT//2 - 10,
            MAP_WIDTH,MAP_HEIGHT,
            arcade.color.DARK_BLUE_GRAY
        )
        
        '''绘制玩家位置'''
        player_map_x = int((self.player_sprite.center_x / AREA_WIDTH) * MAP_WIDTH) + self.view_left + WINDOW_WIDTH - MAP_WIDTH - 10
        player_map_y = int((self.player_sprite.center_y / AREA_HEIGHT) * MAP_HEIGHT) + self.view_bottom + WINDOW_HEIGHT - MAP_HEIGHT - 10
        arcade.draw_circle_filled(
            player_map_x,
            player_map_y,
            5,
            arcade.color.BABY_BLUE
        )
        
        '''绘制晶石位置'''
        for material_sprite in self.material_list:
            material_map_x = int((material_sprite.center_x / AREA_WIDTH) * MAP_WIDTH) + self.view_left + WINDOW_WIDTH - MAP_WIDTH - 10
            material_map_y = int((material_sprite.center_y / AREA_HEIGHT) * MAP_HEIGHT) + self.view_bottom + WINDOW_HEIGHT - MAP_HEIGHT - 10
            arcade.draw_circle_filled(
                material_map_x,
                material_map_y,
                3,
                arcade.color.GREEN
            )

        '''绘制外星人位置'''
        for alien_sprite in self.alien_list:
            alien_map_x = int((alien_sprite.center_x / AREA_WIDTH) * MAP_WIDTH) + self.view_left + WINDOW_WIDTH - MAP_WIDTH - 10
            alien_map_y = int((alien_sprite.center_y / AREA_HEIGHT) * MAP_HEIGHT) + self.view_bottom + WINDOW_HEIGHT - MAP_HEIGHT - 10
            arcade.draw_circle_filled(
                alien_map_x,
                alien_map_y,
                3,
                arcade.color.RED
            )
            
    def on_draw(self):
        global start_time
        global time_text
        '''渲染游戏'''
        self.window.clear()

        '''绘制墙壁、玩家、晶石'''
        self.wall_list.draw()
        self.player_list.draw()
        self.material_list.draw()
        self.alien_list.draw()
        
        '''绘制小地图'''
        self.draw_mini_map()
        output = f"已获得的晶石个数: {self.collect_materials}/10"
        arcade.draw_text(output,
                         self.view_left + 20,
                         WINDOW_HEIGHT - 40 + self.view_bottom, 
                         arcade.color.WHITE, 16,font_name = '5013.ttf')

    '''键盘侦测'''
    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED

        if key == arcade.key.SPACE:
            '''检查玩家与晶石之间的碰撞'''
            materials_hit = arcade.check_for_collision_with_list(self.player_sprite, self.material_list)
            if len(materials_hit) > 0:
                '''如果有碰撞，则从列表中移除第一个碰撞到的晶石'''
                material = materials_hit[0]
                self.material_list.remove(material)
                self.collect_materials += 1
        
    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        self.physics_engine.update()
        '''检测是否需要移动视角'''
        changed = False

        '''视角左移'''
        left_bndry = self.view_left + VIEWPORT_MARGIN
        if self.player_sprite.left < left_bndry:
            self.view_left -= left_bndry - self.player_sprite.left
            changed = True

        '''视角右移'''
        right_bndry = self.view_left + WINDOW_WIDTH - VIEWPORT_MARGIN
        if self.player_sprite.right > right_bndry:
            self.view_left += self.player_sprite.right - right_bndry
            changed = True

        '''视角上移'''
        top_bndry = self.view_bottom + WINDOW_HEIGHT - VIEWPORT_MARGIN
        if self.player_sprite.top > top_bndry:
            self.view_bottom += self.player_sprite.top - top_bndry
            changed = True

        '''视角下移'''
        bottom_bndry = self.view_bottom + VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_bndry:
            self.view_bottom -= bottom_bndry - self.player_sprite.bottom
            changed = True

        if changed:
            
            arcade.set_viewport(self.view_left,
                                WINDOW_WIDTH + self.view_left,
                                self.view_bottom,
                                WINDOW_HEIGHT + self.view_bottom)

        if len(self.material_list) == 0:
            view = GameOverView()
            self.window.show_view(view)

        '''检查玩家与外星人之间的碰撞'''
        materials_hit = arcade.check_for_collision_with_list(self.player_sprite, self.alien_list)
        if len(materials_hit) > 0:
            '''如果有碰撞，则失败'''
            view = GameLoseOverView()
            self.window.show_view(view)

def bgm():
    # 加载并播放背景音乐
    background_music = arcade.load_sound("Xenogenesis.wav")
    arcade.play_sound(background_music, looping=True)
    
'''主程序'''
def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    start_view = InstructionView()
    window.show_view(start_view)
    bgm()
    arcade.run()
    

if __name__ == "__main__":
    main()
