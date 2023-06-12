class GameState:
    """跟踪游戏的统计信息"""


    def __init__(self, ai_game):
        """初始化游戏的状态参数"""
        self.settings = ai_game.settings
        self.reset_stats()
        # 游戏的活动状态，启动时为True
        self.game_active = False
        # high_score 在这里初始化，使其不被重置
        self.high_score = 0
        

    def reset_stats(self):
        """重新开始时设置游戏的初始状态"""
        self.ships_left = self.settings.ship_limit
        #在这里初始化属性score 可以在每次开始游戏时都重置得分
        # 所以并不是所有的属性都要在__init__()中初始化
        self.score = 0
        self.level = 1

