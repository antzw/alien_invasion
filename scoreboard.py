import pygame.font
from pygame.sprite import Group

from ship import Ship


class Scoreboard:
    """现实得分信息的类"""

    def __init__(self,ai_game) -> None:
        """初始化现实得分设计的属性"""
        self.ai_game = ai_game
        self.screen= ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats
        # 显示得分信息时使用的字体样式
        self.text_color = (30,30,30)
        self.font = pygame.font.SysFont(None, 48)
        
        # 准备初始得分图像
        self.prep_score()
        self.prep_high_score()

        self.prep_level()
        self.prep_ships()


    def prep_level(self):
        """准备游戏等级图像"""
        
        level_str ="LEVEL: "+ str(self.stats.level)
        self.level_image = self.font.render(level_str,True,
                                            self.text_color,
                                            ) #self.settings.bg_color
        
        # 设置等级显示位置
        self.level_rect=self.level_image.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top= self.score_rect.bottom +10

    def prep_score(self):
        """将得分转换为一幅渲染的图像"""
        # round() 指定精确到小数点前后的位数 负值表示小数点前的多少位
        rounded_score = round(self.stats.score, -1)
        # 这里是字符串格式设置命令，让python将数值转换为字符串时自动插入逗号，如100，000，000
        score_str ="SCORE: {:,}".format(rounded_score)
        self.score_image = self.font.render(score_str,True,
                                            self.text_color,
                                            self.settings.bg_color)
        # 在屏幕右上角显示得分
        self.score_rect=self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top= 20


    def prep_high_score(self):
        """将最高得分转换为一幅渲染的图像"""
        # round() 指定精确到小数点前后的位数 负值表示小数点前的多少位
        high_score = round(self.stats.high_score, -1)
        # 这里是字符串格式设置命令，让python将数值转换为字符串时自动插入逗号，如100，000，000
        high_score_str ="HIGH: {:,}".format(high_score)
        self.high_score_image = self.font.render(high_score_str,True,
                                            self.text_color,
                                            self.settings.bg_color)
        # 在屏幕右上角显示得分
        self.high_score_rect=self.high_score_image.get_rect()
        self.high_score_rect.center = self.screen_rect.center
        self.high_score_rect.top= self.score_rect.top

    def check_higt_score(self):
        """检查是否诞生了新的最高得分"""
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()

    def prep_ships(self):
        """"""
        self.ships = Group()
        for ship_number in range(self.stats.ships_left):
            ship = Ship(self.ai_game)
            ship.rect.x = 10 +ship_number * ship.rect.width
            ship.rect.y = 10
            self.ships.add(ship)
    
    def show_score(self):
        """在屏幕上显示得分及最高得分"""
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image,self.high_score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        self.ships.draw(self.screen)

    
    