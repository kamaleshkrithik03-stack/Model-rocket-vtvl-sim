import sys
import pygame

pygame.init()
W, H = 1000, 700
win = pygame.display.set_mode((W, H))
pygame.display.set_caption("rocky_sim_phase2")

BLACK = (10, 10, 15)
WHITE = (240, 240, 240)
BLUE = (30, 144, 255)
RED = (255, 69, 58)
ORANGE = (255, 140, 0)
GRAY = (120, 120, 120)

f_sm = pygame.font.SysFont("Consolas", 18)
f_lg = pygame.font.SysFont("Consolas", 26, bold=True)

def main():
    clk = pygame.time.Clock()

    state = "menu"

    rx, ry = W // 2, H - 200
    th = 0.0
    gim = 0.0
    alt = 0.0
    vel = 0.0
    fuel = 100.0
    max_alt = 0.0

    clouds = [
        {"x": 150, "y": -300, "w": 120, "h": 40},
        {"x": 650, "y": -700, "w": 180, "h": 50},
        {"x": 300, "y": -1200, "w": 150, "h": 45},
        {"x": 750, "y": -1800, "w": 200, "h": 60},
        {"x": 200, "y": -2500, "w": 140, "h": 40},
    ]

    print("running phase 2 simulatioon..")

    while True:
        dt = clk.tick(60) / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and state == "menu":
                    state = "boost"
                    th = 50.0
                    vel = 5.0
                    print("liftoff! fuel is burning gng so chopchop1")
                elif e.key == pygame.K_r and state in ["landed", "descent"]:
                    state = "boost"
                    alt = 0.0
                    vel = 5.0
                    fuel = 100.0
                    th = 50.0
                    max_alt = 0.0
                    ry = H - 200
                    print("resetting flight settins")
                elif e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
        if state == "boost":
            keys = pygame.key.get_pressed()
            if fuel > 0:
                if keys[pygame.K_w]: th = min(100.0, th + 60.0 * dt)
                elif keys[pygame.K_s]: th = max(0.0, th - 60.0 * dt)
                else: th = max(0.0, th - 15.0 * dt)

                fuel = max(0.0, fuel - (th * 0.08) * dt)
                if fuel <= 0:
                    th = 0.0
                    state = "coast"
                    print("max engine has been cuttof - just hope that coastin(like life) gets you to your desired apogee")
            else:
                th = 0.0
                state = "coast"

            if keys[pygame.K_a]: gim = max(-7.0, gim - 25.0 * dt)
            elif keys[pygame.K_d]: gim = min(7.0, gim + 25.0 * dt)
            else: gim *= 0.9

            accel = (th * 2.8) - 9.8
            vel += accel * dt
            alt += vel * dt

            if vel <= 0 and alt > 5.0:
                state = "coast"
            
        elif state == "coast":
            vel -= 9.8 * dt
            alt += vel * dt

            if alt > max_alt:
                max_alt = alt
            
            if vel < 0:
                state = "descent"
                print("apogee hit, chute out!")

        elif state == "descent":
            target_descent_vel = -8.0
            vel += (target_descent_vel - vel) * 3.0 * dt
            alt += vel * dt

            if alt <= 0.0:
                alt = 0.0
                vel = 0.0
                state = "landed"
                print("touchdown! i guess you made it down safely!!")

        sky_factor = min(1.0, alt / 2500.0)
        r_col = int(30 * (1 - sky_factor) + 10 * sky_factor)
        g_col = int(144 * (1 - sky_factor) + 10 * sky_factor)
        b_col = int(255 * (1 - sky_factor) + 15 * sky_factor)
        win.fill((r_col, g_col, b_col))

        ground_y = H - 120 + int(alt * 0.5)
        if ground_y < H + 100:
            pygame.draw.rect(win, (34, 139, 34), (0, ground_y, W, H - ground_y))
            pygame.draw.line(win, (200, 200, 200), (0, ground_y), (W, ground_y), 3)

        for c in clouds:
            cloud_screen_y = (H - 250) - int((c["y"] + alt) * 0.4)
            if -100 < cloud_screen_y < H + 100:
                c_alpha = int(250 * max(0.0, 1.0 - (alt / 3500.0)))
                c_surf = pygame.Surface((c["w"], c["h"]), pygame.SRCALPHA)
                pygame.draw.ellipse(c_surf, (255, 255, 255, c_alpha), (0, 0, c["w"], c["h"]))
                win.blit(c_surf, (c["x"], cloud_screen_y))

        win.blit(f_lg.render("hmm ok lets see your flight stats (for phase 2 ofc)", True, WHITE), (50, 30))
        win.blit(f_sm.render(f"flight phase(if you dont know this- get outta here you are not a rocketeer my friend): {state.upper()}", True, ORANGE if state != "landed" else (50, 255, 50)), (50, 75))
        win.blit(f_sm.render(f"altitude: {alt:.1f} m", True, WHITE), (50, 105))
        win.blit(f_sm.render(f"vertical velocity(did you reach mach?): {vel:.1f} m/s", True, WHITE), (50, 130))
        win.blit(f_sm.render(f"fuel remaining(dont exhaust your fuel too much else you are in big trouble): {fuel:.1f}%", True, BLUE if fuel > 20 else RED), (50, 155))
        win.blit(f_sm.render(f"throttle: {th:.1f}%", True, WHITE), (50, 180))

        if state == "menu":
            ov = pygame.Surface((W, 350), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 200))
            win.blit(ov, (100, 180))
            win.blit(f_lg.render("hmm now lets see we are at phase 2 guys", True, WHITE), (135, 215))
            win.blit(f_sm.render("press enter for the majestic ascension your majesty", True, BLUE), (135, 315))
            win.blit(f_sm.render("controls-guys its obvious you are using w,a,s,d its a game whyy", True, GRAY), (135, 345))
        elif state == "landed":
            win.blit(f_lg.render("Touchdown! finally flight complete", True, (50, 255, 50)), (280, 260))
            win.blit(f_sm.render("press r to reset and fly again(have some more fun bruv) or esc to escape", True, WHITE), (290, 310))
        
        if state != "menu":
            r_surf = pygame.Surface((50, 110), pygame.SRCALPHA)
            pygame.draw.polygon(r_surf, RED, [(25, 5), (12, 28), (38, 28)])
            pygame.draw.rect(r_surf, WHITE, (12, 28, 26, 50))

            if state in ["descent", "landed"]:
                pygame.draw.arc(r_surf, ORANGE, (2, 0, 46, 35), 0, 3.14, 4)
                pygame.draw.line(r_surf, GRAY, (15, 18), (15, 28), 1)
                pygame.draw.line(r_surf, GRAY, (35, 18), (35, 28), 1)
            
            if th > 0 and fuel > 0:
                fh = int(th * 0.35)
                fx = 25 - (gim * 1.4)
                pygame.draw.polygon(r_surf, RED, [(15, 78), (35, 78), (int(fx), 78 + fh)])

            rot_r = pygame.transform.rotate(r_surf, -gim * 2.0)
            rect = rot_r.get_rect(center=(int(rx), int(ry)))
            win.blit(rot_r, rect.topleft)

        pygame.display.flip()
    
if __name__ == "__main__":
    main()