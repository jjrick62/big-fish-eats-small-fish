"""
大鱼吃小鱼 - Big Fish Eats Small Fish
鼠标控制鱼移动，吃小鱼长大，躲大鱼
"""
import pygame
import random
import math

# 初始化
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("大鱼吃小鱼")
clock = pygame.time.Clock()
# 字体：直接加载系统黑体
font_path = "C:/Windows/Fonts/simhei.ttf"
font = pygame.font.Font(font_path, 28)
big_font = pygame.font.Font(font_path, 60)

# 颜色
BLUE = (10, 30, 60)
LIGHT_BLUE = (30, 80, 140)
WHITE = (255, 255, 255)
GREEN = (50, 220, 100)
RED = (240, 80, 80)
YELLOW = (255, 230, 80)

# ============ 鱼 ============
class Fish:
    def __init__(self, x, y, radius, speed, color, is_player=False):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.color = color
        self.is_player = is_player
        self.angle = random.uniform(0, 2 * math.pi)
        self.target_x = x
        self.target_y = y
        # 身体比例
        self.body_len = radius * 2.2
        self.tail_len = radius * 1.2

    def draw(self, surf):
        angle = self.angle
        # 身体（椭圆）
        body_surf = pygame.Surface((self.body_len * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(body_surf, self.color, (0, 0, self.body_len * 2, self.radius * 2))
        # 眼睛
        eye_x = self.body_len * 1.3
        eye_y = self.radius * 0.5
        pygame.draw.circle(body_surf, WHITE, (int(eye_x), int(eye_y)), max(3, self.radius // 5))
        pygame.draw.circle(body_surf, (0, 0, 0), (int(eye_x), int(eye_y)), max(2, self.radius // 8))
        # 尾巴
        tail_points = [
            (0, self.radius),
            (int(-self.tail_len), int(self.radius - self.tail_len * 0.6)),
            (int(-self.tail_len), int(self.radius + self.tail_len * 0.6)),
        ]
        pygame.draw.polygon(body_surf, tuple(max(0, c - 30) for c in self.color), tail_points)
        # 旋转
        rotated = pygame.transform.rotate(body_surf, -math.degrees(angle) - 90)
        rect = rotated.get_rect(center=(self.x, self.y))
        surf.blit(rotated, rect.topleft)

    def move_to_mouse(self, mouse_pos):
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        dist = math.hypot(dx, dy)
        if dist > 5:
            self.x += (dx / dist) * min(self.speed, dist)
            self.y += (dy / dist) * min(self.speed, dist)
            self.angle = math.atan2(dy, dx)

    def move_ai(self, fishes, width, height):
        # 逃跑或追捕逻辑
        threat_near = None
        prey_near = None

        for other in fishes:
            if other is self:
                continue
            d = math.hypot(self.x - other.x, self.y - other.y)
            if d < 200 and d > 0:
                if other.radius > self.radius * 1.1:  # 威胁
                    if threat_near is None or d < math.hypot(self.x - threat_near.x, self.y - threat_near.y):
                        threat_near = other
                elif other.radius < self.radius * 0.9:  # 猎物
                    if prey_near is None or d < math.hypot(self.x - other.x, self.y - other.y):
                        prey_near = other

        if threat_near:
            # 逃跑
            dx = self.x - threat_near.x
            dy = self.y - threat_near.y
        elif prey_near:
            # 追捕
            dx = prey_near.x - self.x
            dy = prey_near.y - self.y
        else:
            # 闲逛
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            if abs(dx) < 30 and abs(dy) < 30:
                self.target_x = random.randint(50, width - 50)
                self.target_y = random.randint(50, height - 50)

        dist = math.hypot(dx, dy)
        if dist > 5:
            self.x += (dx / dist) * min(self.speed, dist)
            self.y += (dy / dist) * min(self.speed, dist)
            self.angle = math.atan2(dy, dx)

        # 边界反弹
        margin = self.radius * 2
        self.x = max(margin, min(width - margin, self.x))
        self.y = max(margin, min(height - margin, self.y))


# ============ 泡泡 ============
class Bubble:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT + random.randint(0, 20)
        self.r = random.randint(2, 6)
        self.speed = random.uniform(0.3, 1.0)
        self.wobble = random.uniform(0, 2 * math.pi)

    def update(self):
        self.y -= self.speed
        self.wobble += 0.02
        self.x += math.sin(self.wobble) * 0.3

    def draw(self, surf):
        alpha = max(0, min(255, int(255 * (1 - self.y / HEIGHT))))
        c = (*LIGHT_BLUE, alpha // 2)
        s = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, c, (self.r, self.r), self.r)
        pygame.draw.circle(s, (255, 255, 255, alpha // 3), (self.r - 1, self.r - 1), self.r // 3)
        surf.blit(s, (self.x - self.r, self.y - self.r))


# ============ 游戏主逻辑 ============
def spawn_fish(fishes, player):
    max_fish = 8 + int(player.radius) // 20
    if len(fishes) >= max_fish:
        return
    # 生成比玩家小或大的鱼
    pr = int(player.radius)
    if random.random() < 0.6:  # 小的
        r = random.randint(8, max(10, pr - 5))
        sp = random.uniform(1.0, 2.5)
    else:  # 大的
        r = random.randint(pr + 5, pr + 25)
        sp = random.uniform(0.8, 1.8)
    color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    fishes.append(Fish(x, y, r, sp, color))


def game_over_screen(score):
    screen.fill(BLUE)
    text1 = big_font.render("游戏结束", True, RED)
    text2 = font.render(f"得分: {score}", True, WHITE)
    text3 = font.render("按 R 重新开始 / ESC 退出", True, YELLOW)
    screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 - 80))
    screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2))
    screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2, HEIGHT // 2 + 60))
    pygame.display.flip()
    wait = True
    while wait:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return "restart"
                if e.key == pygame.K_ESCAPE:
                    return "quit"
        clock.tick(30)
    return "quit"


def main():
    player = Fish(WIDTH // 2, HEIGHT // 2, 18, 4.5, GREEN, is_player=True)
    fishes = [player]
    bubbles = [Bubble() for _ in range(30)]
    score = 0
    running = True

    for _ in range(12):
        spawn_fish(fishes, player)

    spawn_timer = 0

    while running:
        # 事件
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return

        # 鼠标控制
        mouse_pos = pygame.mouse.get_pos()
        player.move_to_mouse(mouse_pos)

        # AI 移动
        for f in fishes:
            if not f.is_player:
                f.move_ai(fishes, WIDTH, HEIGHT)

        # 碰撞检测：玩家吃鱼 / 被吃
        eaten = set()
        for f in fishes[:]:
            if f is player or f in eaten:
                continue
            d = math.hypot(player.x - f.x, player.y - f.y)
            if d < player.radius + f.radius:
                if player.radius > f.radius * 1.1:
                    score += f.radius
                    player.radius = min(80, player.radius + f.radius * 0.08)
                    player.speed = max(2.0, 4.5 - player.radius * 0.025)
                    player.body_len = player.radius * 2.2
                    player.tail_len = player.radius * 1.2
                    eaten.add(f)
                elif f.radius > player.radius * 1.1:
                    result = game_over_screen(score)
                    if result == "restart":
                        main()
                        return
                    else:
                        return

        # AI 互吃
        for f1 in fishes[:]:
            if f1 is player or f1 in eaten:
                continue
            for f2 in fishes[:]:
                if f2 is player or f2 is f1 or f2 in eaten:
                    continue
                d = math.hypot(f1.x - f2.x, f1.y - f2.y)
                if d < f1.radius + f2.radius:
                    if f1.radius > f2.radius * 1.2:
                        f1.radius = min(60, f1.radius + f2.radius * 0.05)
                        eaten.add(f2)
                    elif f2.radius > f1.radius * 1.2:
                        f2.radius = min(60, f2.radius + f1.radius * 0.05)
                        eaten.add(f1)

        fishes = [f for f in fishes if f not in eaten]

        # 生成鱼
        spawn_timer += 1
        if spawn_timer > 60:
            spawn_fish(fishes, player)
            spawn_timer = 0

        # 泡泡
        for b in bubbles:
            b.update()
        bubbles = [b for b in bubbles if b.y > -20]
        while len(bubbles) < 30:
            bubbles.append(Bubble())

        # 绘制
        screen.fill(BLUE)
        for b in bubbles:
            b.draw(screen)
        # 画鱼（玩家最后画，在上面）
        for f in fishes:
            if not f.is_player:
                f.draw(screen)
        player.draw(screen)

        # HUD
        score_text = font.render(f"得分: {score}  大小: {player.radius:.0f}", True, WHITE)
        tip_text = font.render("鼠标移动控制方向 | ESC退出", True, YELLOW)
        screen.blit(score_text, (15, 15))
        screen.blit(tip_text, (WIDTH - tip_text.get_width() - 15, HEIGHT - 35))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    try:
        main()
    finally:
        pygame.quit()
