import math
import os
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))

DELTA: dict[int, tuple[int, int]] = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し、真理値タプルを返す関数
    引数：
        obj_rct: こうかとん、または爆弾のRectオブジェクト
    戻り値：横方向、縦方向の判定結果（画面内：True/画面外：False）のタプル
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate

def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面（背景暗転と泣き顔のこうかとん）を表示し、5秒間待機する関数
    引数：
        screen: 描画対象のスクリーン（pg.Surface）
    戻り値：なし
    """
    black_surf = pg.Surface((WIDTH, HEIGHT))
    black_surf.set_alpha(150)
    black_surf.fill((0, 0, 0))
    screen.blit(black_surf, [0, 0])

    kk_cry_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    kk_cry_rct = kk_cry_img.get_rect()
    kk_cry_rct.center = WIDTH // 2-200, HEIGHT // 2
    screen.blit(kk_cry_img, kk_cry_rct)

    kk_cry_rct2 = kk_cry_img.get_rect()
    kk_cry_rct2.center = WIDTH // 2 + 200, HEIGHT // 2
    screen.blit(kk_cry_img, kk_cry_rct2)

    font = pg.font.Font(None, 80)
    txt = font.render("Game Over", True, (255, 255,255))
    screen.blit(txt, [WIDTH // 2-150, HEIGHT // 2-25 ])

    pg.display.update()
    time.sleep(5)

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    時間とともに拡大する爆弾Surfaceのリストと、加速倍率のリストを生成して返す関数
    引数：なし
    戻り値：(爆弾画像のリスト, 加速度のリスト) のタプル
    """
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r))
        bb_img.set_colorkey((0, 0, 0))
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs

def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量タプルをキー、飛ぶ方向に対応したこうかとん画像を値とする辞書を生成して返す関数
    引数：なし
    戻り値：移動量タプルとそれに対応するこうかとん画像(pg.Surface)の辞書
    """
    kk_img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)  
    kk_img1 = pg.transform.flip(kk_img0, True, False)  
    return {
        (0, 0): kk_img0,
        (+5, 0): kk_img1,
        (+5, -5): pg.transform.rotozoom(kk_img1, 45, 1.0),
        (0, -5): pg.transform.rotozoom(kk_img1, 90, 1.0),
        (-5, -5): pg.transform.rotozoom(kk_img0, -45, 1.0),
        (-5, 0): kk_img0,
        (-5, +5): pg.transform.rotozoom(kk_img0, 45, 1.0),
        (0, +5): pg.transform.rotozoom(kk_img1, -90, 1.0),
        (+5, +5): pg.transform.rotozoom(kk_img1, -45, 1.0),
    }

def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    爆弾からこうかとんへの方向ベクトルを計算し、正規化して返す関数
    引数：
        org: 爆弾のRect
        dst: こうかとんのRect
        current_xy: 現在の速度ベクトル
    戻り値：正規化された方向ベクトル、または計算前の速度ベクトル
    """
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery
    dist = math.sqrt(dx**2 + dy**2)
    
    if dist < 300:
        return current_xy
    
    norm = math.sqrt(50)
    if dist > 0:
        vx = dx / dist * norm
        vy = dy / dist * norm
        return vx, vy
    return current_xy

def main():
    """
    逃げろ！こうかとんのメイン処理を行う関数
    引数：なし
    戻り値：なし
    """
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.center = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
    vx, vy = +5, +5

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        if tuple(sum_mv) in kk_imgs:
            kk_img = kk_imgs[tuple(sum_mv)]

        screen.blit(kk_img, kk_rct)
        idx = min(tmr // 500, 9)
        bb_img = bb_imgs[idx]
        bb_rct = bb_img.get_rect(center=bb_rct.center)

        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        bb_rct.move_ip(avx, avy)

        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
            
        screen.blit(bb_img, bb_rct)

        pg.display.update()
        tmr += 1  
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
