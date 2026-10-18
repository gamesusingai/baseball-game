
import asyncio
import math
import random
import pygame
from pathlib import Path

# ============================================================
# BATTING CHALLENGE
# Python + Pygame-CE + Pygbag
# ============================================================

# 設定
WIDTH = 960
HEIGHT = 540
FPS = 60

# Colors
SKY = (115, 190, 235)
GRASS = (52, 145, 76)
GRASS_DARK = (38, 119, 62)
DIRT = (184, 124, 72)
WHITE = (250, 250, 245)
BLACK = (25, 30, 35)
NAVY = (27, 48, 82)
YELLOW = (255, 220, 70)
RED = (220, 65, 65)
BLUE = (65, 135, 225)
ORANGE = (245, 155, 55)

# Game states
TITLE = "title"
PITCHING = "pitching"
FLIGHT = "flight"
RESULT = "result"
GAME_OVER = "game_over"
FORM_EDIT = "form_edit"  # バッティングフォーム編集画面



pygame.init()

# Logical canvas: keep the game layout stable when resized.
canvas = pygame.Surface((WIDTH, HEIGHT))
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("BATTING CHALLENGE")
clock = pygame.time.Clock()

# Japanese font fallback.
# If Japanese characters do not display in the browser build,
# bundle a Japanese font inside the project and load it here.
BASE_DIR = Path(__file__).resolve().parent
FONT_PATH = BASE_DIR / "assets" / "fonts" / "NotoSansJP-Regular.ttf"

def make_font(size, bold=False):
    font = pygame.font.Font(str(FONT_PATH), size)
    if bold:
        font.set_bold(True)
    return font

FONT_SMALL = make_font(19)
FONT_MEDIUM = make_font(27, True)
FONT_LARGE = make_font(43, True)
FONT_TITLE = make_font(54, True)

# Buttons are defined in logical canvas coordinates.
START_BUTTON = pygame.Rect(350, 365, 260, 62)
RETRY_BUTTON = pygame.Rect(350, 350, 260, 58)
TITLE_BUTTON = pygame.Rect(350, 425, 260, 50)
FORM_BUTTON = pygame.Rect(350, 435, 260, 48)
FORM_START_BUTTON = pygame.Rect(650, 455, 250, 52)
FORM_BACK_BUTTON = pygame.Rect(35, 455, 180, 52)

# バッティングフォームの調整パラメータ（数値を変更するとプレビューに反映）
FORM_PARAMS = {
    "stance_width": 1.0,  # 足幅倍率
    "knee_bend": 1.0,     # 膝の曲げ具合
    "lean": 1.0,          # 上半身の前傾・移動
    "arm_raise": 1.0,     # 腕を上げる量
    "arm_extend": 1.0,    # スイング時に腕を伸ばす量
    "bat_angle": -100,    # 通常時のバット角度（度）
    "bat_length": 55,     # バットの長さ
    "bat_pull": 1.0,      # バットの引き具合
    "face_angle": 0,      # 顔の向き（度）
    "front_leg_lift": 0,  # 前脚の上げ具合（ピクセル）
    "body_open": 0.0,     # 体の開き（左右方向のひねり量）
    "wobble": 0.0,        # 構えのふにゃふにゃ
    "jerk": 0.0,          # 構えのカクカク
    "body_bob": 0.0,      # 体の上下
    "spine_wiggle": 0.0,  # 背骨のくねり
    "leg_jitter": 0.0,    # 足の貧乏ゆすり
    "foot_flutter": 0.0,  # 足のパタパタ
    "reverse_joint": 0.0, # 逆関節
    "neck_stretch": 1.0,  # 首の伸縮
    "limb_length": 1.0,   # 手足の長さ
    "head_size": 1.0,     # 頭の大きさ
    "head_shake": 0.0,    # 頭を揺らす
    "neck_turn": 0.0,     # 首のガクッと振り向き
}
FORM_RANGES = {
    "stance_width": (0.5, 1.8, 0.1),
    "knee_bend": (0.0, 2.0, 0.1),
    "lean": (0.0, 2.0, 0.1),
    "arm_raise": (0.0, 2.0, 0.1),
    "arm_extend": (0.0, 2.0, 0.1),
    "bat_angle": (-150, 10, 5),
    "bat_length": (30, 90, 5),
    "bat_pull": (0.0, 2.0, 0.1),
    "face_angle": (-45, 45, 5),
    "front_leg_lift": (0, 28, 2),
    "body_open": (-1.0, 1.0, 0.1),
    "wobble": (0.0, 2.0, 0.1),
    "jerk": (0.0, 2.0, 0.1),
    "body_bob": (0.0, 2.0, 0.1),
    "spine_wiggle": (0.0, 2.0, 0.1),
    "leg_jitter": (0.0, 2.0, 0.1),
    "foot_flutter": (0.0, 2.0, 0.1),
    "reverse_joint": (0.0, 1.0, 0.1),
    "neck_stretch": (0.5, 1.8, 0.1),
    "limb_length": (0.75, 1.8, 0.1),
    "head_size": (0.5, 1.8, 0.1),
    "head_shake": (0.0, 2.0, 0.1),
    "neck_turn": (0.0, 2.0, 0.1),
}
FORM_LABELS = {
    "stance_width": "足幅",
    "knee_bend": "膝の曲げ具合",
    "lean": "上半身の前傾",
    "arm_raise": "腕を上げる量",
    "arm_extend": "スイング時の腕の伸び",
    "bat_angle": "通常時のバット角度",
    "bat_length": "バットの長さ",
    "bat_pull": "バットの引き具合",
    "face_angle": "顔の角度",
    "front_leg_lift": "前脚の上げ具合",
    "body_open": "体の開き",
    "wobble": "構えのふにゃふにゃ",
    "jerk": "構えのカクカク",
    "body_bob": "体上下",
    "spine_wiggle": "背骨くねり",
    "leg_jitter": "足震え",
    "foot_flutter": "足パタパタ",
    "reverse_joint": "逆関節",
    "neck_stretch": "首伸縮",
    "limb_length": "手足長さ",
    "head_size": "頭サイズ",
    "head_shake": "頭揺れ",
    "neck_turn": "首ガクッ",
}
FORM_ROWS = {}
for _i, _key in enumerate(FORM_PARAMS):
    _column = _i // 12
    _row = _i % 12
    _x = 20 + _column * 278
    _y = 88 + _row * 29
    FORM_ROWS[_key] = {
        "label_x": _x + 63,
        "minus": pygame.Rect(_x + 135, _y - 11, 28, 22),
        "value_x": _x + 193,
        "plus": pygame.Rect(_x + 217, _y - 11, 28, 22),
    }

# Game state
state = TITLE
# ---- サイドビューのレイアウト ----
GROUND_Y = 462                          # 地面（足の高さ）
BATTER_SCALE = 2.2                      # バッターの拡大率
batter_x = 280
batter_y = GROUND_Y - int(63 * BATTER_SCALE)
Picher_x = 780                          # 投球の出所（ボールの初期位置）
Picher_y = 318
MOUND_Y = GROUND_Y - 18                 # 投手の足元
HIT_X = 425                             # ボールを打つべきx座標
HIT_Y = batter_y - 2                    # ボールが通る高さ
HIT_WINDOW = 80                         # 芯に当たる許容幅(px)
STRIKE_ZONE = pygame.Rect(HIT_X - 22, batter_y - 35, 44, 120)
ball_x = Picher_x
ball_y = Picher_y
pitch_start_time = 0.0 # 投球開始時間
pitch_duration = 1.45 # 投球時間
swing_used = False # スイング使用フラグ
result_timer = 0.0 # 結果表示タイマー
result_text = "" # 結果テキスト
result_color = WHITE # 結果テキストの色
last_distance = 0
last_timing = 0.0

balls = 0 # ボール数
strikes = 0 # スライク数
outs = 0 # アウト数
score = 0 # スコア
hits = 0 # ヒット数
home_runs = 0 # ホームラン数
at_bats = 0 # 打席数
message = "" # メッセージ
game_time = 0.0

# Base paths
top = (Picher_x, 80)
right = (Picher_x + 350, Picher_y + 50)
bottom = (Picher_x, batter_y)
left = (Picher_x - 350, Picher_y + 50)

# スイング
is_swinging = False # バッターがスイング中かどうか
swing_pending = False # スイングが保留されているかどうか
swing_judged = False
is_charging = False  # バットを構えているか
SWING_CONTACT_TIME = 150 # スイング判定のタイミング（ミリ秒）
swing_start_time = 0 # スイングを開始した時刻（ミリ秒）
SWING_DURATION = 300 # スイングの継続時間（ミリ秒）
bat_angle = -60 # バットの角度（度）



def reset_game():
    """Reset the complete game."""
    global is_charging
    global at_bats, message, game_time
    global is_swinging, swing_pending, swing_judged, bat_angle
    global state, ball_x, ball_y, pitch_start_time
    global swing_used, result_timer, result_text, result_color
    global last_distance, last_timing
    global balls, strikes, outs, score, hits, home_runs
    global at_bats, message, game_time

    state = TITLE
    ball_x = Picher_x # ボールの初期位置
    ball_y = Picher_y # ボールの初期位置
    pitch_start_time = 0.0 # 投球開始時間
    swing_used = False # スイング使用フラグ
    result_timer = 0.0 # 結果表示タイマー
    result_text = "" # 結果テキスト
    result_color = WHITE # 結果テキストの色
    last_distance = 0 # 最後の距離
    last_timing = 0.0 # 最後の.timing
    is_swinging = False
    swing_pending = False
    swing_judged = False
    is_charging = False
    bat_angle = -60

    balls = 0 # ボール数
    strikes = 0 # スライク数
    outs = 0 # アウト数
    score = 0 # スコア
    hits = 0 # ヒット数
    home_runs = 0 # ホームラン数
    at_bats = 0 # 打席数
    message = "" # メッセージ
    game_time = 0.0


def start_pitch():
    """Start the next pitch."""
    global state, ball_x, ball_y, pitch_start_time
    global pitch_duration, swing_used

    state = PITCHING
    ball_x = Picher_x # ボールの初期位置
    ball_y = Picher_y # ボールの初期位置
    pitch_start_time = game_time # 投球開始時間
    pitch_duration = random.uniform(1.15, 1.55) # 投球時間
    swing_used = False # スイング使用フラグ

result_duration = 1.0

def finish_result(text, color=WHITE, distance=0, duration=1.25):
    global state, result_text, result_color
    global result_timer, result_duration, last_distance

    state = RESULT
    result_text = text
    result_color = color
    result_timer = duration
    result_duration = duration
    last_distance = distance


def call_strike(text="ストライク！"):
    """Record a strike and handle a strikeout."""
    global strikes, outs, at_bats, balls, message

    strikes += 1

    if strikes >= 3:
        outs += 1
        at_bats += 1
        message = "三振！"

        # One strikeout ends the at-bat, not the whole game.
        balls = 0
        strikes = 0

        if outs >= 3:
            finish_result("三振！ 3アウト ゲーム終了", RED, duration=2.0)
            # Switch to game-over after showing the result.
            global next_state_after_result
            next_state_after_result = GAME_OVER
        else:
            finish_result("三振！ 次の打席へ", RED, duration=1.6)
            next_state_after_result = PITCHING
    else:
        message = text
        finish_result(text, YELLOW, duration=0.9)
        next_state_after_result = PITCHING


def call_ball():
    """Record a ball; four balls award a walk."""
    global balls, strikes, at_bats, message, score

    balls += 1

    if balls >= 4:
        at_bats += 1
        score += 1
        balls = 0
        strikes = 0
        message = "フォアボール！ 出塁！"
        finish_result(message, BLUE, duration=1.4)
    else:
        message = "ボール"
        finish_result(message, WHITE, duration=0.9)

    global next_state_after_result
    next_state_after_result = PITCHING

def start_charge():
    """ボタンやキーを押してバッターが構える。"""
    global is_charging, bat_angle

    if state != PITCHING or swing_used:
        return

    if is_swinging or is_charging:
        return

    is_charging = True
    bat_angle = -120

def release_swing():
    """ボタンやキーを離したときにスイングする。"""
    global is_charging

    if not is_charging:
        return

    is_charging = False
    swing_batter()

def swing_batter():
    """スイングを開始し、後で打撃判定を行う。"""
    global is_swinging, swing_start_time
    global swing_pending, swing_judged, bat_angle

    if is_swinging or state != PITCHING or swing_used:
        return

    is_swinging = True
    swing_pending = True
    swing_judged = False
    swing_start_time = pygame.time.get_ticks()

    # 構えの角度からスイングを開始
    bat_angle = -120

def update_swing():
    global is_swinging, bat_angle
    global swing_pending, swing_judged

    if not is_swinging:
        return

    elapsed = pygame.time.get_ticks() - swing_start_time

    # スイングの途中で打撃判定を行う
    if swing_pending and not swing_judged:
        if elapsed >= SWING_CONTACT_TIME:
            swing_pending = False
            swing_judged = True
            judge_swing()

    progress = min(elapsed / SWING_DURATION, 1.0)

    if progress < 0.7:
        phase = progress / 0.7
        # 構えた角度から前方へ振り抜く
        bat_angle = -120 + 210 * phase
    else:
        phase = (progress - 0.7) / 0.3
        # スイング後に構えの角度へ戻す
        bat_angle = 90 - 210 * phase

    if progress >= 1.0:
        is_swinging = False
        bat_angle = -60
        swing_judged = False

def judge_swing():
    """Judge swing timing based on distance from the ideal hit point."""
    global swing_used, last_timing, hits, home_runs
    global score, balls, strikes, at_bats, message
    global ball_x, ball_y

    if state != PITCHING or swing_used:
        return

    swing_used = True
    delta = HIT_X - ball_x
    timing_error = abs(delta)
    last_timing = timing_error

    # A swing too early is recorded, but the pitch continues.
    if delta < -HIT_WINDOW:
        message = "早すぎ！"
        return

    # A swing too late is a strike.
    if delta > HIT_WINDOW:
        call_strike("振り遅れ！ ストライク")
        return

    # Contact window: timing quality is between 0 and 1.
    quality = max(0.0, 1.0 - timing_error / HIT_WINDOW) # タイミングの品質
    at_bats += 1
    ball_x, ball_y = HIT_X, HIT_Y

    # Great contact produces stronger results more often.
    roll = random.random() # ランダムな値を生成

    if quality >= 0.82 and roll < 0.38:
        home_runs += 1
        hits += 1
        score += 4
        distance = random.randint(105, 135)
        message = "ホームラン！！"
        finish_result(message, YELLOW, distance, 1.6)

    elif quality >= 0.60 and roll < 0.72:
        hits += 1
        score += 2
        distance = random.randint(70, 100)
        message = "二塁打！"
        finish_result(message, ORANGE, distance, 1.4)

    elif quality >= 0.30 and roll < 0.82:
        hits += 1
        score += 1
        distance = random.randint(35, 65)
        message = "ヒット！"
        finish_result(message, BLUE, distance, 1.2)

    elif quality >= 0.12 and roll < 0.90:
        # Weak contact is treated as a foul.
        message = "ファウル！"
        strikes = min(2, strikes + 1)
        finish_result(message, WHITE, random.randint(5, 25), 1.0)

    else:
        # Poor contact is an out.
        message = "打ち取られた！ アウト"
        global outs
        outs += 1

        if outs >= 3:
            finish_result("アウト！ 3アウト ゲーム終了", RED, duration=1.8)
            global next_state_after_result
            next_state_after_result = GAME_OVER
        else:
            finish_result("アウト！", RED, duration=1.2)
            next_state_after_result = PITCHING

    # A completed hit ends the at-bat; reset the count.
    balls = 0
    strikes = 0

    # Unless the result already specified a game-over transition,
    # proceed to the next pitch after the result display.
    if state == RESULT and "next_state_after_result" not in globals():
        next_state_after_result = PITCHING


next_state_after_result = PITCHING


def update_game(dt):
    """Update game state and animations."""
    global game_time, ball_x, ball_y, state
    global result_timer, next_state_after_result, message

    game_time += dt # ゲーム時間を更新

    if state == PITCHING:
        elapsed = game_time - pitch_start_time
        progress = min(1.0, elapsed / pitch_duration)

        # スイング判定が終わるまでは、投球を完全に終了させない
        if swing_pending and progress >= 1.0:
            progress = 0.98

        # Ease the ball toward the plate.
        ball_x = lerp(Picher_x, HIT_X, progress)
        ball_y = lerp(Picher_y, HIT_Y, progress) - 20 * math.sin(math.pi * progress)

        if progress >= 1.0:
            if swing_used:
                # An early swing still becomes a strike at the plate.
                call_strike("空振り！ ストライク")
            else:
                # A take is randomly called a ball or a strike.
                if random.random() < 0.35:
                    call_ball()
                else:
                    call_strike("見逃しストライク")

    elif state == FLIGHT:
        # Reserved for future animated ball flight.
        pass

    elif state == RESULT:
        result_timer -= dt

        if result_timer <= 0:
            if next_state_after_result == GAME_OVER:
                state = GAME_OVER
            else:
                start_pitch()


def draw_text(surface, text, font, color, center):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=center)
    surface.blit(rendered, rect)


def draw_button(surface, rect, label, color=BLUE):
    pygame.draw.rect(surface, color, rect, border_radius=12)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=12)
    draw_text(surface, label, FONT_MEDIUM, WHITE, rect.center)


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


_field_bg = None

def draw_field(surface):
    """サイドビューの球場（背景は一度だけ作ってキャッシュ）。"""
    global _field_bg
    if _field_bg is None:
        bg = pygame.Surface((WIDTH, HEIGHT))
        bg.fill(SKY)
        pygame.draw.rect(bg, (74, 98, 138), (0, 215, WIDTH, 90))      # スタンド
        for row in range(5):                                           # 観客
            for i in range(0, WIDTH, 16):
                c = (200 + (i * 7 + row * 31) % 55,
                     150 + (i * 13 + row * 17) % 90,
                     120 + (i * 5 + row * 23) % 100)
                pygame.draw.circle(bg, c, (i + 8 + (row % 2) * 8, 228 + row * 15), 5)
        pygame.draw.rect(bg, (30, 85, 60), (0, 300, WIDTH, 10))        # フェンス
        pygame.draw.rect(bg, GRASS, (0, 310, WIDTH, HEIGHT - 310))     # 芝
        for sx in range(0, WIDTH, 120):
            pygame.draw.rect(bg, GRASS_DARK, (sx, 310, 60, HEIGHT - 310))
        pygame.draw.rect(bg, DIRT, (230, GROUND_Y - 6, 600, 26), border_radius=13)
        pygame.draw.ellipse(bg, DIRT, (Picher_x - 50, MOUND_Y - 8, 140, 30))
        pygame.draw.rect(bg, WHITE, (HIT_X - 24, GROUND_Y + 2, 48, 6)) # ホームベース
        _field_bg = bg
    surface.blit(_field_bg, (0, 0))


def draw_pitcher(surface, x, y, batter=False):
    """Draw a simple pitcher using geometric shapes."""
    # Legs
    pygame.draw.line(surface, WHITE, (x - 5, y + 24), (x - 10, y + 43), 6)
    pygame.draw.line(surface, WHITE, (x + 5, y + 24), (x + 10, y + 43), 6)

    # Body / uniform
    body_color = NAVY if batter else RED
    pygame.draw.rect(surface, body_color, (x - 13, y - 3, 26, 32),
                     border_radius=5)

    # Head and cap
    pygame.draw.circle(surface, (235, 185, 145), (x, y - 15), 12)
    pygame.draw.rect(surface, body_color, (x - 13, y - 29, 26, 7))
    pygame.draw.rect(surface, body_color, (x - 7, y - 35, 14, 8))

    if batter:
        # バットの支点
        pivot_x = x + 9
        pivot_y = y + 3

        # 角度をラジアンに変換する
        angle_rad = math.radians(bat_angle)

        # バットの長さ
        bat_length = FORM_PARAMS["bat_length"]

        # 角度に応じてバットの先端座標を計算する
        tip_x = pivot_x + math.cos(angle_rad) * bat_length
        tip_y = pivot_y + math.sin(angle_rad) * bat_length

        # 支点から先端までバットを描画する
        pygame.draw.line(
            surface,
            (115, 70, 35),
            (pivot_x, pivot_y),
            (int(tip_x), int(tip_y)),
            7
        )


def draw_pitcher_side(surface, x, foot_y, k=1.6):
    """既存の投手を拡大して描く（仮。後で横向きにできる）。"""
    buf = pygame.Surface((60, 90), pygame.SRCALPHA)
    draw_pitcher(buf, 30, 40, batter=False)
    big = pygame.transform.smoothscale(buf, (int(60 * k), int(90 * k)))
    surface.blit(big, (int(x - 30 * k), int(foot_y - 83 * k)))


def draw_ball(surface, x, y):
    x, y = int(x), int(y)
    pygame.draw.ellipse(surface, (140, 92, 55), (x - 12, GROUND_Y + 8, 24, 8))  # 影
    pygame.draw.circle(surface, WHITE, (x, y), 11)
    pygame.draw.line(surface, RED, (x - 6, y - 4), (x + 6, y + 4), 2)


def flight_position():
    """打球の位置。バットに当たった点から弧を描いて飛ぶ。"""
    t = min(1.0, 1.0 - max(0.0, result_timer) / max(0.01, result_duration))
    peak = min(240.0, 40 + last_distance * 1.6)
    x = HIT_X + last_distance * 5.0 * t
    y = HIT_Y + (GROUND_Y - 12 - HIT_Y) * t - 4 * peak * t * (1 - t)
    return x, y


def two_bone_ik(a, b, l1, l2, bend=-1):
    """付け根a・先端bから中間関節（膝/肘）の位置を求める。bend=-1で前方(右)に曲がる。"""
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy)
    d = max(abs(l1 - l2) + 0.01, min(d, l1 + l2 - 0.01))
    cos_a = max(-1.0, min(1.0, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)))
    ang = math.atan2(dy, dx) + bend * math.acos(cos_a)
    return (a[0] + math.cos(ang) * l1, a[1] + math.sin(ang) * l1)


def draw_limb(surface, color, a, b, width):
    pa = (int(a[0]), int(a[1]))
    pb = (int(b[0]), int(b[1]))
    pygame.draw.line(surface, color, pa, pb, width)
    pygame.draw.circle(surface, color, pb, width // 2)


def bat_angles(theta_deg):
    """画面内の角度(度)を仰角と方位に変換する。"""
    th = math.radians(theta_deg)
    e = math.degrees(math.atan2(-math.sin(th), abs(math.cos(th))))
    phi = 0.0 if math.cos(th) >= 0 else 180.0
    return e, phi


def bat_back_deg():
    """溜めたときにバットを後ろへ倒す角度（度）。"""
    return 35 * FORM_PARAMS["bat_pull"]


def bat_swing_pose(p):
    """スイング進行度 p(0-1) でのバットの仰角・方位を返す。"""
    th0 = FORM_PARAMS["bat_angle"]
    e_s, f_s = bat_angles(th0 - bat_back_deg())
    e_i, f_i = bat_angles(th0)
    if f_i == 180.0:
        f_i = -180.0
    f_drop = 140 + 30 * min(FORM_PARAMS["bat_pull"], 1.5)
    keys = [
        (0.00, e_s, f_s),
        (0.20, 12, f_drop),
        (0.50, 5, 35),
        (0.78, 45, -110),
        (1.00, e_i, f_i),
    ]
    for (p0, e0, f0), (p1, e1, f1) in zip(keys, keys[1:]):
        if p <= p1:
            t = (p - p0) / (p1 - p0)
            if p0 >= 0.78:
                t = ease(t)
            return lerp(e0, e1, t), lerp(f0, f1, t)
    return e_i, f_i


def _rnd(n, salt):
    v = math.sin(n * 12.9898 + salt * 78.233) * 43758.5453
    return (v - math.floor(v)) * 2.0 - 1.0


def stance_fx(calm):
    """構え中の体・背骨・足・頭の動きを返す。"""
    w = FORM_PARAMS["wobble"] * calm
    j = FORM_PARAMS["jerk"] * calm
    bob = FORM_PARAMS["body_bob"] * calm
    spine = FORM_PARAMS["spine_wiggle"] * calm
    leg = FORM_PARAMS["leg_jitter"] * calm
    flutter = FORM_PARAMS["foot_flutter"] * calm
    head_shake = FORM_PARAMS["head_shake"] * calm
    t = pygame.time.get_ticks() / 1000.0
    n = int(t / 0.14)

    def s(freq, phase=0.0):
        return math.sin(2 * math.pi * freq * t + phase)

    return {
        "hip_x": 3.0 * w * s(1.1) + 3.0 * j * _rnd(n, 1),
        "hip_y": 3.5 * w * s(1.7, 0.8) + 3.0 * j * abs(_rnd(n, 2)),
        "tilt": 9.0 * w * s(0.9, 1.0) + 10.0 * j * _rnd(n, 3),
        "hand_dx": 3.0 * w * s(1.9) + 3.5 * j * _rnd(n, 5),
        "hand_dy": 3.0 * w * s(1.5, 1.57) + 3.5 * j * _rnd(n, 6),
        "bat": 12.0 * w * s(1.6, 0.5) + 16.0 * j * _rnd(n, 7),
        "body_bob": 5.0 * bob * s(1.8, 0.4),
        "spine": 6.0 * spine * s(1.35, 0.6),
        "leg_x": 2.5 * leg * s(8.0),
        "foot_lift": 4.0 * flutter * max(0.0, s(7.0)),
        "head_dx": 2.5 * head_shake * s(2.2, 0.7),
        "head_dy": 2.0 * head_shake * s(2.8, 1.4),
        "head": 14.0 * w * s(1.3, 2.0) + 18.0 * j * _rnd(n, 4)
                + 10.0 * head_shake * s(2.0, 0.3),
        "neck_turn": 32.0 * FORM_PARAMS["neck_turn"] * calm
                     * (1 if _rnd(int(t / 0.65), 8) > 0 else -1),
    }


def batter_motion():
    """(load, sw, fo, bat, calm) を返す。calm は構えの揺れの強さ。"""
    lb, sw, fo, p = 0.0, 0.0, 0.0, None
    calm = 1.0

    if state == FORM_EDIT:
        t = pygame.time.get_ticks() % 2400
        if t < 1400:
            lb = 1.0
        elif t < 1400 + SWING_DURATION:
            p = (t - 1400) / SWING_DURATION
    elif is_charging:
        lb = 1.0
    elif is_swinging:
        p = (pygame.time.get_ticks() - swing_start_time) / SWING_DURATION

    if p is not None:
        p = max(0.0, min(1.0, p))
        lb = 1.0 - ease(p / 0.4)
        if p < 0.5:
            sw = ease(p / 0.5)
        elif p < 0.78:
            sw, fo = 1.0, ease((p - 0.5) / 0.28)
        else:
            sw = fo = 1.0 - ease((p - 0.78) / 0.22)
        if p < 0.2:
            calm = 1.0 - ease(p / 0.2)
        elif p < 0.85:
            calm = 0.0
        else:
            calm = ease((p - 0.85) / 0.15)
        e, f = bat_swing_pose(p)
    else:
        e, f = bat_angles(FORM_PARAMS["bat_angle"] - bat_back_deg() * lb)

    er, fr = math.radians(e), math.radians(f)
    vx = math.cos(er) * math.cos(fr)
    up = math.sin(er)
    vz = math.cos(er) * math.sin(fr)
    bat = (vx, -up + 0.3 * vz, vz)
    return 0.3 + 0.7 * lb, sw, fo, bat, calm


def draw_batter(surface, x, y, batter=True, k=1.0):
    """右向きの横向きバッターを描画する。(x, y)=基準点、k=拡大率。"""
    P = FORM_PARAMS
    load, sw, fo, bat, calm = batter_motion()
    fx = stance_fx(calm)
    lb = (load - 0.3) / 0.7

    ox, oy = x, y          # 画面上の基準点
    x = y = 0.0            # 以降の座標は基準点からの相対値

    def T(p):
        return (int(ox + p[0] * k), int(oy + p[1] * k))

    def limb(color, a, b, w):
        w = max(1, int(w * k))
        pygame.draw.line(surface, color, T(a), T(b), w)
        pygame.draw.circle(surface, color, T(b), w // 2)

    def line(color, a, b, w):
        pygame.draw.line(surface, color, T(a), T(b), max(1, int(w * k)))

    def dot(color, p, r):
        pygame.draw.circle(surface, color, T(p), max(1, int(r * k)))

    def poly(color, pts):
        pygame.draw.polygon(surface, color, [T(p) for p in pts])

    skin, skin_far = (235, 185, 145), (205, 158, 122)
    pants, pants_far = (240, 240, 235), (200, 200, 195)
    jersey, shoes, wood = NAVY, (35, 35, 40), (115, 70, 35)

    # ---- 下半身（足は地面に固定、膝はIK）----
    ground = y + 62
    hip = (x - 4 * lb + 5 * sw + fx["hip_x"],
           y + 22 + 6 * P["knee_bend"] * load + fx["hip_y"] + fx["body_bob"])
    hip_b = (hip[0] - 3, hip[1])
    hip_f = (hip[0] + 3, hip[1])
    limb_scale = P["limb_length"]
    foot_b = (x - 17 * P["stance_width"] + fx["leg_x"],
              ground - fx["foot_lift"])
    foot_f = (x + 17 * P["stance_width"] + 10 * P["body_open"] + 6 * sw + fx["leg_x"],
              ground - P["front_leg_lift"] * lb - fx["foot_lift"])
    knee_b_normal = two_bone_ik(hip_b, foot_b, 26 * limb_scale, 26 * limb_scale)
    knee_b_reverse = two_bone_ik(hip_b, foot_b, 26 * limb_scale, 26 * limb_scale, bend=1)
    knee_f_normal = two_bone_ik(hip_f, foot_f, 26 * limb_scale, 26 * limb_scale)
    knee_f_reverse = two_bone_ik(hip_f, foot_f, 26 * limb_scale, 26 * limb_scale, bend=1)
    reverse = P["reverse_joint"]
    knee_b = (lerp(knee_b_normal[0], knee_b_reverse[0], reverse),
              lerp(knee_b_normal[1], knee_b_reverse[1], reverse))
    knee_f = (lerp(knee_f_normal[0], knee_f_reverse[0], reverse),
              lerp(knee_f_normal[1], knee_f_reverse[1], reverse))
    limb(pants_far, hip_b, knee_b, 11)
    limb(pants_far, knee_b, foot_b, 9)
    limb(pants, hip_f, knee_f, 11)
    limb(pants, knee_f, foot_f, 9)
    for foot_x, foot_y in (foot_b, foot_f):
        sx, sy = T((foot_x - 6, foot_y - 3))
        pygame.draw.ellipse(surface, shoes,
                            (sx, sy, max(1, int(22 * k)), max(1, int(9 * k))))

    # ---- 胴体の向きと肩 ----
    tilt = math.radians(P["lean"] * (6 + 8 * lb + 4 * sw) + fx["tilt"])
    ux, uy = math.sin(tilt), -math.cos(tilt)
    px, py = -uy, ux
    S = (hip[0] + ux * 34 + fx["spine"], hip[1] + uy * 34)

    # ---- 腕のキーフレーム（奥の腕は胴体より先に描く）----
    g0 = (-6 - 4 * load - 6 * (P["bat_pull"] - 1) * lb,
          -5 - 7 * P["arm_raise"] * (0.4 + 0.6 * load))
    g1 = (18 + 6 * P["arm_extend"], 4)
    e0, e1 = (-12, 4), (10, 12)
    hand = (S[0] + lerp(g0[0], g1[0], sw) * limb_scale + fx["hand_dx"],
            S[1] + lerp(g0[1], g1[1], sw) * limb_scale - 8 * fo + fx["hand_dy"])
    elbow = (S[0] + lerp(e0[0], e1[0], sw) * limb_scale + fx["hand_dx"] * 0.5,
             S[1] + lerp(e0[1], e1[1], sw) * limb_scale - 6 * fo + fx["hand_dy"] * 0.5)
    hand_far = (hand[0] - 3, hand[1] + 1)
    elbow_far = (elbow[0] - 3, elbow[1] + 2)
    limb(skin_far, S, elbow_far, 8)
    limb(skin_far, elbow_far, hand_far, 7)

    # ---- バットは背中側なら胴体の後ろに描く ----
    ba = math.radians(fx["bat"])
    bdx = bat[0] * math.cos(ba) - bat[1] * math.sin(ba)
    bdy = bat[0] * math.sin(ba) + bat[1] * math.cos(ba)
    bz = bat[2]
    L = P["bat_length"]
    knob = (hand[0] - 10 * bdx, hand[1] - 10 * bdy)
    mid = (hand[0] + 0.3 * L * bdx, hand[1] + 0.3 * L * bdy)
    tip = (hand[0] + L * bdx, hand[1] + L * bdy)

    def draw_bat():
        line(wood, knob, mid, 4)
        line(wood, mid, tip, 8)
        dot(wood, tip, 4)
        dot(wood, knob, 3)

    if bz < 0:
        draw_bat()

    # ---- 胴体 ----
    hl = (hip[0] - px * 7, hip[1] - py * 7)
    hr = (hip[0] + px * 7, hip[1] + py * 7)
    spine_mid = (hip[0] + ux * 17 + fx["spine"] * 0.55,
                 hip[1] + uy * 17)
    spine_left = (spine_mid[0] - px * 8, spine_mid[1] - py * 8)
    spine_right = (spine_mid[0] + px * 8, spine_mid[1] + py * 8)
    poly(jersey, [hl, hr, (S[0] + px * 8, S[1] + py * 8),
                  spine_right, spine_left, (S[0] - px * 8, S[1] - py * 8)])
    dot(jersey, S, 8)
    line((25, 25, 35), hl, hr, 3)

    # ---- 頭（face_angle で顔ごと回転）----
    neck_scale = P["neck_stretch"]
    head_angle = tilt + 0.3 + math.radians(fx["neck_turn"])
    nx, ny = math.sin(head_angle), -math.cos(head_angle)
    neck = (S[0] + nx * 7 * neck_scale, S[1] + ny * 7 * neck_scale)
    hc = (S[0] + nx * 17 * neck_scale + fx["head_dx"],
          S[1] + ny * 17 * neck_scale + fx["head_dy"])
    limb(skin, S, neck, 6)
    head_scale = P["head_size"]
    dot(skin, hc, 10 * head_scale)

    fa = math.radians(P["face_angle"] + fx["head"] + fx["neck_turn"])
    ca, sa = math.cos(fa), math.sin(fa)

    def hp(dx, dy):
        dx *= head_scale
        dy *= head_scale
        return (hc[0] + dx * ca - dy * sa, hc[1] + dx * sa + dy * ca)

    dot(skin, hp(10, 1), 3 * head_scale)     # 鼻
    dot(BLACK, hp(5, -1), 2 * head_scale)    # 目
    mouth = (120, 40, 40)
    if sw > 0.15:
        dot(mouth, hp(6, 5), (1.5 + 2.0 * sw) * head_scale)
    else:
        line(mouth, hp(3.5, 5.5), hp(8, 4.5), 1.5)
    poly(jersey, [hp(-10, -1), hp(-9, -8), hp(-3, -12), hp(5, -11),
                  hp(10, -6), hp(10, -3)])                    # 帽子
    poly(jersey, [hp(9, -5), hp(19, -3), hp(19, -1), hp(9, -2)])  # つば

    # ---- 手前の腕 → バット（グリップは手に固定）→ 手 ----
    limb(skin, S, elbow, 8)
    limb(skin, elbow, hand, 7)

    if bz >= 0:
        draw_bat()
    dot(skin, hand, 5)

def draw_hud(surface):
    """Draw score and current baseball count."""
    pygame.draw.rect(surface, NAVY, (15, 15, 350, 76), border_radius=10)
    draw_text(surface, f"SCORE  {score}", FONT_MEDIUM, WHITE, (115, 40))
    draw_text(surface, f"HITS  {hits}    HR  {home_runs}",
              FONT_SMALL, WHITE, (185, 70))

    pygame.draw.rect(surface, NAVY, (720, 15, 225, 76), border_radius=10)
    draw_text(surface, f"OUT  {outs}/3", FONT_MEDIUM, WHITE, (832, 40))
    draw_text(surface, f"B {balls}   S {strikes}",
              FONT_MEDIUM, YELLOW, (832, 70))


def draw_title(surface):
    draw_field(surface)
    pygame.draw.rect(surface, NAVY, (160, 75, 640, 260), border_radius=22)
    pygame.draw.rect(surface, YELLOW, (160, 75, 640, 260), 4,
                     border_radius=22)

    draw_text(surface, "BATTING", FONT_TITLE, YELLOW, (480, 135))
    draw_text(surface, "CHALLENGE", FONT_TITLE, WHITE, (480, 192))
    draw_text(surface, "タイミングよくボールを打ち返そう！",
              FONT_MEDIUM, WHITE, (480, 250))
    draw_text(surface, "クリック / SPACEキー でスイング",
              FONT_SMALL, WHITE, (480, 292))

    draw_button(surface, START_BUTTON, "ゲームスタート", GRASS_DARK)
    draw_button(surface, FORM_BUTTON, "フォームを編集", BLUE)


def draw_form_editor(surface):
    """数値を調整しながらフォームをプレビューする画面。"""
    draw_field(surface)
    pygame.draw.rect(surface, NAVY, (15, 18, 555, 440), border_radius=14)
    pygame.draw.rect(surface, YELLOW, (15, 18, 555, 440), 2, border_radius=14)
    draw_text(surface, "バッティングフォーム設定", FONT_MEDIUM, YELLOW, (292, 42))
    draw_text(surface, "− / ＋で調整。右側でフォームを確認できます。",
              FONT_SMALL, WHITE, (292, 65))

    for key, row in FORM_ROWS.items():
        y = row["minus"].centery
        value = FORM_PARAMS[key]
        value_text = f"{value:.1f}" if isinstance(value, float) else str(value)
        draw_text(surface, FORM_LABELS[key], FONT_SMALL, WHITE, (row["label_x"], y))
        draw_button(surface, row["minus"], "−", RED)
        draw_text(surface, value_text, FONT_SMALL, YELLOW, (row["value_x"], y))
        draw_button(surface, row["plus"], "+", GRASS_DARK)

    pygame.draw.rect(surface, NAVY, (590, 18, 350, 430), border_radius=14)
    pygame.draw.rect(surface, YELLOW, (590, 18, 350, 430), 2, border_radius=14)
    draw_text(surface, "フォームプレビュー", FONT_MEDIUM, YELLOW, (765, 48))
    pygame.draw.line(surface, GRASS_DARK, (615, 392), (915, 392), 4)  # 地面
    draw_batter(surface, 705, 262, True, 2.0)
    draw_text(surface, "※構え → スイングを繰り返し表示中", FONT_SMALL, WHITE, (765, 410))
    draw_button(surface, FORM_BACK_BUTTON, "タイトルへ戻る", BLUE)
    draw_button(surface, FORM_START_BUTTON, "このフォームで開始", GRASS_DARK)


def draw_game(surface):
    draw_field(surface)
    draw_hud(surface)

    band = pygame.Surface((HIT_WINDOW * 2, STRIKE_ZONE.height), pygame.SRCALPHA)
    band.fill((255, 220, 70, 45))
    surface.blit(band, (HIT_X - HIT_WINDOW, STRIKE_ZONE.top))
    pygame.draw.line(surface, YELLOW, (HIT_X, STRIKE_ZONE.top),
                     (HIT_X, STRIKE_ZONE.bottom), 1)
    pygame.draw.rect(surface, YELLOW, STRIKE_ZONE, 2)

    draw_pitcher_side(surface, Picher_x + 20, MOUND_Y + 2)
    draw_batter(surface, batter_x, batter_y, True, BATTER_SCALE)

    flying = state == RESULT and last_distance > 0
    if not flying:
        draw_ball(surface, ball_x, ball_y)

    if state == PITCHING:
        draw_text(surface, "押して構える → 離してスイング",
                  FONT_SMALL, WHITE, (480, 510))
        if message:
            draw_text(surface, message, FONT_MEDIUM, YELLOW, (480, 125))

    elif state == RESULT:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 70))
        surface.blit(overlay, (0, 0))
        draw_text(surface, result_text, FONT_LARGE, result_color, (480, 140))
        if last_distance > 0:
            draw_text(surface, f"飛距離：{last_distance} m",
                      FONT_MEDIUM, WHITE, (480, 190))
            bx, by = flight_position()
            draw_ball(surface, bx, by)


def draw_game_over(surface):
    draw_field(surface)

    pygame.draw.rect(surface, NAVY, (180, 70, 600, 270), border_radius=20)
    pygame.draw.rect(surface, RED, (180, 70, 600, 270), 4,
                     border_radius=20)

    draw_text(surface, "GAME OVER", FONT_TITLE, RED, (480, 125))
    draw_text(surface, f"最終スコア：{score}", FONT_LARGE, YELLOW, (480, 190))
    draw_text(surface, f"ヒット：{hits}    ホームラン：{home_runs}",
              FONT_MEDIUM, WHITE, (480, 250))
    draw_text(surface, f"打席数：{at_bats}    アウト：{outs}",
              FONT_MEDIUM, WHITE, (480, 290))

    draw_button(surface, RETRY_BUTTON, "もう一度プレイ", BLUE)
    draw_button(surface, TITLE_BUTTON, "タイトルへ戻る", GRASS_DARK)


def draw_frame():
    """Draw the current screen to the logical canvas."""
    if state == TITLE:
        draw_title(canvas)
    elif state == FORM_EDIT:
        draw_form_editor(canvas)
    elif state in (PITCHING, FLIGHT, RESULT):
        draw_game(canvas)
    elif state == GAME_OVER:
        draw_game_over(canvas)

    # Scale logical canvas to the actual window size.
    screen_size = screen.get_size()
    if screen_size[0] > 0 and screen_size[1] > 0:
        scaled = pygame.transform.smoothscale(canvas, screen_size)
        screen.blit(scaled, (0, 0))

    pygame.display.flip()


def to_logical_position(pos):
    """Convert mouse coordinates to logical canvas coordinates."""
    sw, sh = screen.get_size()
    if sw <= 0 or sh <= 0:
        return pos
    return (int(pos[0] * WIDTH / sw), int(pos[1] * HEIGHT / sh))


def handle_click(pos):
    global state

    x, y = pos

    if state == TITLE:
        if START_BUTTON.collidepoint(x, y):
            start_pitch()
        elif FORM_BUTTON.collidepoint(x, y):
            state = FORM_EDIT

    elif state == FORM_EDIT:
        if FORM_BACK_BUTTON.collidepoint(x, y):
            state = TITLE
        elif FORM_START_BUTTON.collidepoint(x, y):
            start_pitch()
        else:
            for key, row in FORM_ROWS.items():
                low, high, step = FORM_RANGES[key]
                if row["minus"].collidepoint(x, y):
                    FORM_PARAMS[key] = max(low, round(FORM_PARAMS[key] - step, 2))
                elif row["plus"].collidepoint(x, y):
                    FORM_PARAMS[key] = min(high, round(FORM_PARAMS[key] + step, 2))

    elif state == PITCHING:
        start_charge()

    elif state == GAME_OVER:
        if RETRY_BUTTON.collidepoint(x, y):
            reset_game()
            start_pitch()
        elif TITLE_BUTTON.collidepoint(x, y):
            reset_game()


async def main():
    global state

    running = True
    # ゲームループ
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        for event in pygame.event.get():
            # Handle window events
            if event.type == pygame.QUIT:
                running = False

            # Handle window resize events
            elif event.type == pygame.VIDEORESIZE:
                # The logical canvas remains 960x540.
                screen = pygame.display.get_surface()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    handle_click(to_logical_position(event.pos))

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    release_swing()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state != TITLE:
                        reset_game()
                    else:
                        running = False

                elif event.key == pygame.K_SPACE:
                    if state == TITLE:
                        start_pitch()
                    elif state == FORM_EDIT:
                        start_pitch()
                    elif state == PITCHING:
                        start_charge()
                    elif state == GAME_OVER:
                        reset_game()
                        start_pitch()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    release_swing()

        # スイングアニメーションと打撃判定を更新
        update_swing()
        # ボールやゲーム状態を更新
        update_game(dt)
        # 画面を描画
        draw_frame()

        # Required to yield control to the browser runtime in Pygbag.
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
