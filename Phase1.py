import os, sys
import pygame

pygame.init()
W, H = 1000, 700
win = pygame.display.set_mode((W, H))
pygame.display.set_caption("rocky_sim_v2")

BLACK = (10, 10, 15)
WHITE = (240, 240, 240)
BLUE = (30, 144, 255)
RED = (255, 69, 58)

f_sm = pygame.font.SysFont("Consolas", 18)
f_lg = pygame.font.SysFont("Consolas", 28, bold=True)

def load_bgs():
    # loading the field & cloud assets
    bg1 = pygame.Surface((W, H))
    bg1.fill((20, 30, 45))
    if os.path.exists("field.jpg"):
        i1 = pygame.image.load("field.jpg")
        bg1 = pygame.transform.scale(i1, (W, H))
    
    bg2 = pygame.Surface((W, H))
    bg2.fill((100, 150, 200))
    if os.path.exists("Types_of_clouds.jpg"):
        i2 = pygame.image.load("Types_of_clouds.jpg")
        bg2 = pygame.transform.scale(i2, (W, H))

    return bg1, bg2

def main():
    clk = pygame.time.Clock()
    field_img, cloud_img = load_bgs()

    menu = True
    rx, ry = W // 2, H - 180
    th = 0.0
    gim = 0.0
    alt = 0.0

    print("running sim...")

    while True:
        dt = clk.tick(60) / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and menu:
                    menu = False
                    print("liftoff!!")
                elif e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            
        if not menu:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_w]: th = min(100.0, th + 60.0 * dt)
            elif keys[pygame.K_s]: th = max(0.0, th - 60.0 * dt)
            else: th = max(0.0, th - 15.0 * dt)

            if keys[pygame.K_a]: gim = max(-7.0, gim - 25.0 * dt)
            elif keys[pygame.K_d]: gim = min(7.0, gim + 25.0 * dt)
            else: gim *= 0.90

            alt += (th * 3.5) * dt
            ry -= (th * 1.5) * dt
            if ry < 220: ry = 220

        win.fill(BLACK)

        if menu:
            win.blit(field_img, (0, 0))
            ov = pygame.Surface((W, 400), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 160))
            win.blit(ov, (100, 150))

            win.blit(f_lg.render("Project rocky: outside version to suit the theme", True, WHITE), (140, 185))
            win.blit(f_sm.render("press [enter] to launch from the field", True, BLUE), (140, 245))
            win.blit(f_sm.render("controls: use w,a,s,d for throttle and the tvc gimbal controls!!", True, (180, 180, 180)), (140, 295))
        else:
            alpha = min(1.0, alt / 1200.0)

            win.blit(field_img, (0, 0))
            if alpha > 0:
                cloud_img.set_alpha(int(alpha * 255))
                win.blit(cloud_img, (0, 0))

            win.blit(f_lg.render("Flight stats(or telemetry for the nerdy ones)", True, BLUE), (50, 40))
            win.blit(f_sm.render(f"throttle: {th:.1f}%", True, WHITE), (50, 90))
            win.blit(f_sm.render(f"tvc gimbal: {gim:+.1f} deg", True, WHITE), (50, 120))
            win.blit(f_sm.render(f"altitude: {alt:.1f} m", True, (180, 180, 180)), (50, 150))

            r_surf = pygame.Surface((60, 120), pygame.SRCALPHA)
            pygame.draw.polygon(r_surf, RED, [(30, 5), (22, 25), (38, 25)])
            pygame.draw.rect(r_surf, WHITE, (22, 25, 16, 50))

            if th > 0:
                fh = int(th * 0.4)
                fx = 30 - (gim * 1.6)
                pygame.draw.polygon(r_surf, RED, [(23, 75), (37, 75), (int(fx), 75 + fh)])

            rot_r = pygame.transform.rotate(r_surf, -gim * 2.2)
            rect = rot_r.get_rect(center=(int(rx), int(ry)))
            win.blit(rot_r, rect.topleft)

        pygame.display.flip()

if __name__ == "__main__":
    main()