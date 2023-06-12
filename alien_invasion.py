import sys
from time import sleep


import pygame


from settings import Settings
from game_stats import GameState
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien



class AlienInvasion:
    """管理游戏资源和行为的类"""

    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()
        self.settings = Settings()
        #设置游戏窗口模式
        if self.settings.screen_mode==1:
            self.screen = pygame.display.set_mode(
                (self.settings.screen_width, self.settings.screen_height)
            )
        else:
            self.screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
            self.settings.screen_width = self.screen.get_rect().width
            self.settings.screen_height = self.screen.get_rect().height

        pygame.display.set_caption("Alien Invasion")
        
        # 创建一个用于储存游戏统计信息的实例
        # 并创建记分牌
        self.stats= GameState(self)
        self.sb = Scoreboard(self)
        # 创建飞船类的实例
        self.ship = Ship(self)
        #设置窗口图标
        pygame.display.set_icon(self.ship.image)
        #添加子弹编组，实际上是一个列表
        self.bullets=pygame.sprite.Group()
        #self.fire = False #是否自动开火
        #创建外星人的实例
        self.aliens=pygame.sprite.Group()
        self._create_fleet()

        #创建Play按钮
        self.play_button = Button(self,"Play")




    def run_game(self):
        """开始游戏主循环"""
        while True:
            self._check_events()

            if self.stats.game_active:
                #游戏活动时才更新的内容
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                #self._fire_bullet() 自动开火

            self._update_screen()
            
            

    def _check_events(self):
        """响应键盘和鼠标事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
    
    def _check_play_button(self, mouse_pos):
        """在玩家单机Play按钮时开始新游戏"""
        if (self.play_button.rect.collidepoint(mouse_pos) and
             not self.stats.game_active):
            # 重置游戏
            self._start_game()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            



    
    def _check_keydown_events(self, event):
        """响应按键按下"""
        if event.key == pygame.K_RIGHT:         
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_p and not self.stats.game_active:
            self._start_game()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
            #一下为作弊模式
            #self.fire=True
    
    def _check_keyup_events(self, event):
        """响应按键抬起事件"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        #elif event.key == pygame.K_SPACE:
            #self.fire=False

    def _start_game(self):
        """重新开始游戏"""
        #重置游戏统计信息
        self.stats.reset_stats()
        self.stats.game_active = True
        self.settings.initialize_dynamic_settings()
        self.sb.prep_score()

        #清空余下的外星人和子弹
        self.aliens.empty()
        self.bullets.empty()

        #创建一群新的外星人并让飞船居中
        self._create_fleet()
        self.ship.center_ship()

        # 隐藏鼠标光标
        pygame.mouse.set_visible(False)
    
    def _fire_bullet(self):
        """创建一颗子弹,并将其加入编组bullets中"""
        #if self.fire: #作弊模式
        if len(self.bullets) <self.settings.bullet_allowed:
            new_bullet =Bullet(self)
            self.bullets.add(new_bullet)


    def _update_bullets(self):
        """更新子弹的位置并删除消失的子弹"""
        # 更新子弹的位置
        self.bullets.update()

        #删除消失的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <=0:
                self.bullets.remove(bullet)
        #测试子弹是否真的被删除
        #print(len(self.bullets))
        self._check_bullet_alien_collisions()
        
    
    def _check_bullet_alien_collisions(self):
        #检查是否有子弹击中了外星人
        #如果是，就删除相应的子弹和外星人
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True
        )
        if collisions:
            for aliens in collisions.values():
                # collisions 是一个字典
                #其中每个子弹都是一个key，而每个valus都是和这个子弹对应的一个列表
                # 列表中包含和这个子弹发生碰撞的外星人个数
                self.stats.score += self.settings.alien_points *len(aliens)
                self.sb.prep_score()
                self.sb.check_higt_score()
        if not self.aliens: #如果外星人被打光 
            # 删除现有的子弹并新建一群外星人
            self.bullets.empty()
            self._create_fleet()
            # 并加速游戏
            self.settings.increase_speed()
            # 提高等级
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        """
        检查是否有外星人位于屏幕边缘，
        并更新外星人群中所有外星人的位置
        """
        self._check_fleet_edges()
        self.aliens.update()
        #检测外星人和飞船之间的碰撞
        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            # print("Ship hit!!!")
            self._ship_hit()
        #检查是否有外星人达到了屏幕底端
        self._check_aliens_bottom()

    def _ship_hit(self):
        """响应飞船被外星人撞到"""
        # 将ships_left减一
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            #清空余下的外星人和子弹
            self.aliens.empty()
            self.bullets.empty()

            # 创建一群新的外星人，并将飞船放到屏幕底端的中央
            self._create_fleet()
            self.ship.center_ship()

            # 暂停0.5秒
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)


    def _check_aliens_bottom(self):
        """检查是否有外星人到达了屏幕底端"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # 和飞船被撞到一样处理。
                self._ship_hit()
                break

    def _create_fleet(self):
        """创建外星人群"""
        #创建一个外星人并计算一行可容纳多少个外星人
        #外星人的间距为外星人的宽度
        alien = Alien(self)
        alien_width,alien_height=alien.rect.size
        available_space_x = self.settings.screen_width - (2* alien_width)
        number_aliens_x = available_space_x //(2*alien_width)
        #计算屏幕可容纳多少行外星人
        ship_height = self.ship.rect.height
        available_space_y =(self.settings.screen_height -
                             (3*alien_height) -
                               ship_height)
        number_rows=available_space_y //(2* alien_height)

        #创建外星人矩阵
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number,row_number)
    
    def _create_alien(self, alien_number,row_number):
        """创建一个外星人并将其加入当前行"""
        alien = Alien(self)
        alien_width,alien_height=alien.rect.size
        
        alien.x = alien_width + 2*alien_width * alien_number
        alien.y = alien_height + 2*alien_height * row_number
        alien.rect.x = alien.x
        alien.rect.y = alien.y
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """检查当外星人处于屏幕边缘时采取相应措施"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        """将整个外星人下移，并改变他们的方向"""
        for alien in self.aliens.sprites():
            alien.rect.y +=self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

        


    def _update_screen(self):
        """更新屏幕上的图像，并切换到新屏幕"""
        # 每次循环时都重绘屏幕
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        #循环在屏幕上绘制Bullets编组中的每个子弹
        for bullet in self.bullets.sprites(): #返回一个列表，其中包含bullets中的所以精灵
            bullet.draw_bullet()
        # 在窗口绘制外星人分组
        self.aliens.draw(self.screen)

        #显示记分牌
        self.sb.show_score()
        
        #如果游戏处于非活动状态，就绘制Play按钮
        if not self.stats.game_active:
            self.play_button.draw_button()

        # 让最近绘制的屏幕可见
        pygame.display.flip()



if __name__ == "__main__":
    # 创建游戏实例并运行游戏
    ai = AlienInvasion()
    ai.run_game()
