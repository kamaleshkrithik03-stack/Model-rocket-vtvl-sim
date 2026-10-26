import os
import sys
import pygame
import math
import random

pygame.init()
W, H = 1000, 700
win = pygame.display.set_mode((W, H))
pygame.display.set_caption("rocky_sim_phase5")

WHITE = (240, 240, 240)
BLUE = (30, 144, 255)
RED = (255, 69, 58)
ORANGE = (255, 140, 0)
GRAY = (120, 120, 120)
GREEN = (50, 255, 50)
CYAN = (0, 220, 220)
YELLOW = (255, 215, 0)

f_sm = pygame.font.SysFont("Consolas", 18)
f_lg = pygame.font.SysFont("Consolas", 26, bold=True)

DRAG_COEFF = 0.0005
PAD_X = W // 2
PAD_HALF_WIDTH = 35
CHUTE_ALT = 500.0
STEER_ACCEL = 30.0
GROUND_SCALE = 3.0
CLOUD_SCALE = 2.0
CHUTE_LINE_LEN = 70
BODY_L = 10.0
COM_OPTS = [("NOSE BALLAST", 4.0), ("NO BALLAST", 5.5)]
COP_OPTS = [("BIG FINS", 7.5), ("SMALL FINS", 5.5)]
FUEL_SHIFT = 1.5
TVC_K = 0.5
AERO_K = 0.08
PITCH_DAMP = 0.4
TILT_LIMIT = 30.0
GUST_MAX = 6.0

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_menu_bg():
    for name in ("launch_real.jpg",):
        path = os.path.join(BASE_DIR, name)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert()
                return pygame.transform.scale(img, (W, H))
            except pygame.error:
                pass
    print("menu background image not found- go to rep and download that as well guys or you are stuck with my colour hehe")
    return None

launch_bg = load_menu_bg()

def txt(s, color, x, y, font=f_sm):
    win.blit(font.render(s, True, color), (x, y))

def margin_at(com, cop, frac):
    return cop - (com + FUEL_SHIFT * frac)

def mcol(m):
    return GREEN if m >= 0.5 else (YELLOW if m >= 0 else RED)

def main():
    clk = pygame.time.Clock()
    state = "menu"

    rx, ry = W // 2, H - 138
    h_vel = 0.0
    th = 0.0
    gim = 0.0
    alt = 0.0
    vel = 0.0

    selected_fuel = 100.0
    fuel = selected_fuel

    wind_speed = 0.0
    target_apogee = 1000.0
    max_alt = 0.0
    ang = 0.0
    om = 0.0
    max_tilt = 0.0
    com_pos = 4.0
    cop_pos = 7.5
    gust = 0.0
    gust_target = 0.0
    gust_timer = 0.0
    log = []
    log_t = 0.0
    log_acc = 0.0
    show_graph = False
    scored = False
    score = 0.0
    rating = "C"
    apogee_error = 0.0
    lateral_offset = 0.0
    on_pad = False

    dragging_fuel = False
    dragging_wind = False
    dragging_apogee = False
    dragging_com = False
    dragging_cop = False

    COM_MIN = 3.0
    COM_MAX = 6.5
    COP_MIN = 4.5
    COP_MAX = 9.0  # beyond this i think that the rocket is not a rocket anymore

    clouds = []
    cloud_data = [
        {"x": 150, "y": -300, "w": 120, "h": 40},
        {"x": 500, "y": -500, "w": 100, "h": 35},
        {"x": 650, "y": -700, "w": 180, "h": 50},
        {"x": 850, "y": -1000, "w": 130, "h": 40},
        {"x": 300, "y": -1200, "w": 150, "h": 45},
        {"x": 80, "y": -1500, "w": 160, "h": 45},
        {"x": 750, "y": -1800, "w": 200, "h": 60},
        {"x": 450, "y": -2100, "w": 170, "h": 50},
        {"x": 200, "y": -2500, "w": 140, "h": 40},
        {"x": 600, "y": -3000, "w": 180, "h": 55},
        {"x": 250, "y": -3600, "w": 150, "h": 45},
        {"x": 800, "y": -4200, "w": 190, "h": 55},
    ]
    for c in cloud_data:
        surf = pygame.Surface((c["w"], c["h"]), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (255, 255, 255, 255), (0, 0, c["w"], c["h"]))
        clouds.append({"x": c["x"], "y": c["y"], "surf": surf})

    print("now this sim is better than the last one(maybe) -dont you scrutinize this from last one")

    while True:
        dt = min(clk.tick(60) / 1000.0, 0.05)

        if state != "menu":
            frac = fuel / selected_fuel
        else:
            frac = 1.0

        cog = com_pos + FUEL_SHIFT * frac
        cop = cop_pos
        margin = cop - cog

        if state == "boost" or state == "coast":
            gust_timer -= dt
            if gust_timer <= 0.0:
                gust_target = random.uniform(-GUST_MAX, GUST_MAX)
                gust_timer = random.uniform(2.0, 3.5)
            gust += (gust_target - gust) * 2.0 * dt

        wind_eff = wind_speed + gust

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif state == "menu":
                    if e.key == pygame.K_RETURN:
                        state = "boost"
                        fuel = selected_fuel
                        th = 50.0
                        vel = 5.0
                        max_alt = 0.0
                        ang = 0.0
                        om = 0.0
                        max_tilt = 0.0
                        gust = 0.0
                        gust_target = 0.0
                        gust_timer = 0.0
                        log = []
                        log_t = 0.0
                        log_acc = 0.0
                        show_graph = False
                        scored = False
                        print("liftoff gng - i would say congrats but this is not a real rocket")
                elif e.key == pygame.K_r and (state == "landed" or state == "descent"):
                    state = "menu"
                    alt = 0.0
                    vel = 0.0
                    h_vel = 0.0  # i added horizontal velocity this time cuz it shows how TVC affects the horizontal drift as well
                    th = 0.0
                    gim = 0.0
                    ang = 0.0
                    om = 0.0
                    max_tilt = 0.0
                    max_alt = 0.0
                    rx = W // 2
                    ry = H - 138
                    print("returning to normal menu (why normal)")
                elif e.key == pygame.K_g and state == "landed":
                    if show_graph:
                        show_graph = False
                    else:
                        show_graph = True
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if state == "menu":
                    if e.pos[0] >= 135 and e.pos[0] <= 435 and e.pos[1] >= 240 and e.pos[1] <= 270:
                        dragging_fuel = True
                    elif e.pos[0] >= 135 and e.pos[0] <= 435 and e.pos[1] >= 315 and e.pos[1] <= 345:
                        dragging_wind = True
                    elif e.pos[0] >= 135 and e.pos[0] <= 435 and e.pos[1] >= 390 and e.pos[1] <= 420:
                        dragging_apogee = True
                    elif e.pos[0] >= 135 and e.pos[0] <= 435 and abs(e.pos[1] - 495) <= 15:
                        dragging_com = True
                    elif e.pos[0] >= 135 and e.pos[0] <= 435 and abs(e.pos[1] - 555) <= 15:
                        dragging_cop = True
            elif e.type == pygame.MOUSEBUTTONUP:
                dragging_fuel = False
                dragging_wind = False
                dragging_apogee = False
                dragging_com = False
                dragging_cop = False
            elif e.type == pygame.MOUSEMOTION:
                if state == "menu":
                    if dragging_fuel:
                        rel_x = max(0, min(300, e.pos[0] - 135))
                        selected_fuel = 25.0 + (rel_x / 300.0) * (250.0 - 25.0)
                    if dragging_wind:
                        rel_x = max(0, min(300, e.pos[0] - 135))
                        wind_speed = -20.0 + (rel_x / 300.0) * 40.0
                    if dragging_apogee:
                        rel_x = max(0, min(300, e.pos[0] - 135))
                        target_apogee = 200.0 + (rel_x / 300.0) * (3000.0 - 200.0)
                    if dragging_com:
                        rel_x = max(0, min(300, e.pos[0] - 135))
                        com_pos = COM_MIN + (rel_x / 300.0) * (COM_MAX - COM_MIN)
                    if dragging_cop:
                        rel_x = max(0, min(300, e.pos[0] - 135))
                        cop_pos = COP_MIN + (rel_x / 300.0) * (COP_MAX - COP_MIN)
                    
        keys = pygame.key.get_pressed()

        if state == "boost":
            if fuel > 0:
                if keys[pygame.K_w]:
                    th = min(100.0, th + 60.0 * dt)
                elif keys[pygame.K_s]:
                    th = max(0.0, th - 60.0 * dt)
                else:
                    th = max(0.0, th - 15.0 * dt)

                fuel = max(0.0, fuel - (th * 0.08) * dt)
                if fuel <= 0:
                    th = 0.0
                    state = "coast"
                    print("ok now we are starting to coast(like life) as you have run out of fuel(i told you to be careful). Now hope that the momentum carries you to your home(apogee)")
            else:
                th = 0.0
                state = "coast"

            if keys[pygame.K_a]:
                gim = max(-7.0, gim - 25.0 * dt)
            elif keys[pygame.K_d]:
                gim = min(7.0, gim + 25.0 * dt)
            else:
                gim *= (0.85 ** (dt * 60.0))
            
            thrust_vert = th * 0.3 * math.cos(math.radians(ang))
            thrust_horiz = th * 0.3 * math.sin(math.radians(ang)) 

            drag_v = -DRAG_COEFF * vel * abs(vel)
            accel = thrust_vert - 9.8 + drag_v

            vel += accel * dt
            alt += vel * dt

            if alt > 0.0:
                h_vel += (thrust_horiz + (wind_eff - h_vel) * 1.5) * dt
                rx += h_vel * dt

            if alt <= 0.0:
                alt = 0.0
                if vel < 0:
                    vel = 0.0
                else:
                    vel = vel

            if vel <= 0 and alt > 5.0:
                th = 0.0
                state = "coast"

        elif state == "coast":
            th = 0.0
            gim *= (0.85 ** (dt * 60.0))
            drag_v = -DRAG_COEFF * vel * abs(vel)  # ok so this bit till line 198 is ai coded as idk the math of drag or wind
            vel += (-9.8 + drag_v) * dt
            alt += vel * dt

            h_vel += (wind_eff - h_vel) * 0.8 * dt
            rx += h_vel * dt

            if vel < 0:
                state = "descent"
                print("ok good that is good(those who know, know) you have hit apogee and now we are free falling(trust the process) until low alt chute deployement")
        
        elif state == "descent":
            th = 0.0
            gim *= (0.85 ** (dt * 60.0))
            ang *= (0.9 ** (dt * 60.0))
            om = 0.0
            drag_v = -DRAG_COEFF * vel * abs(vel)  # again ai till line 220 and i copy pasted no worries no inflation of time

            if alt > CHUTE_ALT:
                vel += (-9.8 + drag_v) * dt
            else:
                target_descent_vel = -8.0
                vel += (target_descent_vel - vel) * 0.8 * dt

            alt += vel * dt

            if keys[pygame.K_d]:
                steer = 1
            elif keys[pygame.K_a]:
                steer = -1
            else:
                steer = 0

            h_vel += steer * STEER_ACCEL * dt
            h_vel += (wind_speed * 0.5 - h_vel) * 2.0 * dt
            rx += h_vel * dt

            if alt <= 0.0:
                alt = 0.0
                vel = 0.0
                h_vel = 0.0
                state = "landed"
                print("touchdown now dont you rejoice just yet well see your stats(for nerds:Telemetry )")
            
        # AI-assisted till line 316(no worries all ai assited code is copy pasted)
        if state == "boost" or state == "coast":
            hrel = h_vel - wind_eff
            alpha = max(-90.0, min(90.0, ang - math.degrees(math.atan2(hrel, max(abs(vel), 1.0)))))
            q = DRAG_COEFF * (vel * vel + hrel * hrel)
            om += (-AERO_K * q * alpha * margin + (gim / 7.0) * th * TVC_K * (BODY_L - cog) / BODY_L) * dt
            om *= (1.0 - PITCH_DAMP * dt)
            ang = (ang + om * dt + 180.0) % 360.0 - 180.0
            if alt <= 0.0:
                ang = 0.0
                om = 0.0
            if abs(ang) > max_tilt:
                max_tilt = abs(ang)
            
        if state == "boost" or state == "coast" or state == "descent":
            log_t += dt
            log_acc += dt
            if log_acc >= 0.1:
                log_acc -= 0.1
                log.append((log_t, alt, ang))

        if state == "landed" and not scored:
            log.append((log_t, alt, ang))
            apogee_error = abs(max_alt - target_apogee)
            lateral_offset = abs(rx - PAD_X)
            if lateral_offset <= PAD_HALF_WIDTH:
                on_pad = True
            else:
                on_pad = False
            
            # Ai coded bit from 324 to 328
            apogee_score_part = max(0.0, 1.0 - apogee_error / (0.25 * target_apogee))
            tilt_score_part = max(0.0, 1.0 - max_tilt / 90.0)
            fuel_score_part = fuel / selected_fuel
            if on_pad:
                pad_score_part = 1.0
            else:
                pad_score_part = max(0.0, 1.0 - lateral_offset / 300.0)

            score = (45 * apogee_score_part + 30 * tilt_score_part + 15 * fuel_score_part + 10 * pad_score_part)
            
            if score >= 90:
                rating = "S"
            elif score >= 75:
                rating = "A"
            elif score >= 55:
                rating = "B"
            else:
                rating = "C"
            scored = True

        if alt > max_alt:
            max_alt = alt
        
        if rx < 50:
            rx = 50
        elif rx > W - 50:
            rx = W - 50

        if state == "menu":
            if launch_bg:
                win.blit(launch_bg, (0, 0))
            else:
                win.fill((20, 25, 35))
        else:
            sky_factor = min(1.0, alt / 2500.0)
            r_col = int(30 * (1 - sky_factor) + 10 * sky_factor)
            g_col = int(144 * (1 - sky_factor) + 10 * sky_factor)
            b_col = int(255 * (1 - sky_factor) + 15 * sky_factor)
            win.fill((r_col, g_col, b_col))

            ground_y = H - 120 + int(alt * GROUND_SCALE)  # cmn guys this is basic math of scalin
            if ground_y < H + 100:
                pygame.draw.rect(win, (34, 139, 34), (0, ground_y, W, H - ground_y))
                pygame.draw.line(win, (200, 200, 200), (0, ground_y), (W, ground_y), 3)
                pygame.draw.rect(win, RED, (PAD_X - PAD_HALF_WIDTH, ground_y - 3, PAD_HALF_WIDTH * 2, 6))

            cloud_alpha = int(220 * max(0.0, 1.0 - alt / 5000.0))
            for c in clouds:
                cloud_screen_y = (H - 250) + int((c["y"] + alt) * CLOUD_SCALE)
                if cloud_screen_y > -100 and cloud_screen_y < H + 100:
                    c["surf"].set_alpha(cloud_alpha)
                    win.blit(c["surf"], (c["x"], cloud_screen_y))

            if state != "landed" and abs(vel) > 25.0:
                streak_len = int(min(80, abs(vel) * 0.4))
                for i in range(10):
                    sx = (i * 97 + 53) % W
                    sy = int((i * 131 + alt * GROUND_SCALE * 1.5) % (H + 80)) - 40
                    pygame.draw.line(win, (220, 235, 255), (sx, sy), (sx, sy + streak_len), 2)
                
        if state != "menu" and state != "landed":
            if state != "landed":
                phase_color = ORANGE
            else:
                phase_color = GREEN
            win.blit(f_sm.render(f"flight phase: {state.upper()} (if you dont know this get outa here you are not a rocketeer)", True, phase_color), (50, 75))
            win.blit(f_sm.render(f"altitude: {alt:.1f} m", True, WHITE), (50, 105))
            win.blit(f_sm.render(f"vertical velocity: {vel:.1f} m/s", True, WHITE), (50, 130))
            
            if fuel > 20:
                fuel_color = BLUE
            else:
                fuel_color = RED
            win.blit(f_sm.render(f"fuel remaining: {fuel:.1f} kg   (ok now be careful with fuel consumption if red else its chill man)", True, fuel_color), (50, 155))
            win.blit(f_sm.render(f"max altitude: {max_alt:.1f} m (ok you be the judge your majesty)", True, YELLOW), (50, 180))
            win.blit(f_sm.render(f"wind: {wind_eff:+.1f} m/s", True, CYAN), (50, 205))
            win.blit(f_sm.render(f"pad offset: {rx - PAD_X:+.0f} px", True, CYAN), (50, 230))
            
            if abs(ang) < TILT_LIMIT:
                tilt_color = GREEN
            else:
                tilt_color = RED
            txt(f"tilt: {ang:+.1f} deg (keep it under {TILT_LIMIT:.0f})", tilt_color, 50, 255)
            txt(f"stability: {margin:+.2f} cal  COG {cog:.2f} m (green dot)  COP {cop:.2f} m (cyan ring)", mcol(margin), 50, 280)
        
        if state == "menu":
            ov = pygame.Surface((800, 480), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 210))
            win.blit(ov, (100, 130))
            win.blit(f_sm.render("rocky rockets game(or you decide the name) configuration", True, WHITE), (135, 155))

            win.blit(f_sm.render(f"fuel load: {selected_fuel:.1f} kg", True, BLUE), (135, 215))
            pygame.draw.rect(win, GRAY, (135, 251, 300, 8))
            fuel_pos = 135 + int(((selected_fuel - 25.0) / (250.0 - 25.0)) * 300)
            pygame.draw.circle(win, BLUE, (fuel_pos, 255), 10)

            win.blit(f_sm.render(f"wind speed: {wind_speed:.1f} m/s", True, CYAN), (135, 290))
            pygame.draw.rect(win, GRAY, (135, 326, 300, 8))
            wind_pos = 135 + int(((wind_speed + 20.0) / 40.0) * 300)
            pygame.draw.circle(win, CYAN, (wind_pos, 330), 10)

            win.blit(f_sm.render(f"target apogee: {target_apogee:.0f} m", True, YELLOW), (135, 365))
            pygame.draw.rect(win, GRAY, (135, 401, 300, 8))
            apogee_pos = 135 + int(((target_apogee - 200.0) / (3000.0 - 200.0)) * 300)
            pygame.draw.circle(win, YELLOW, (apogee_pos, 405), 10)
            win.blit(f_sm.render("(normally i suggest to aim for the stars but in this case DONT)", True, YELLOW), (135, 425))

            win.blit(f_sm.render(f"COM (when dry): {com_pos:.1f} m from nose", True, GREEN), (135, 455))
            pygame.draw.rect(win, GRAY, (135, 491, 300, 8))
            com_x = 135 + int(((com_pos - COM_MIN) / (COM_MAX - COM_MIN)) * 300)
            pygame.draw.circle(win, GREEN, (com_x, 495), 10)

            win.blit(f_sm.render(f"COP: {cop_pos:.1f} m from nose", True, CYAN), (135, 515))
            pygame.draw.rect(win, GRAY, (135, 551, 300, 8))
            cop_x = 135 + int(((cop_pos - COP_MIN) / (COP_MAX - COP_MIN)) * 300)
            pygame.draw.circle(win, CYAN, (cop_x, 555), 10)

            win.blit(f_sm.render("press [enter] to launch", True, GREEN), (135, 590))

            win.blit(f_sm.render("Controls are w, a, s, d", True, WHITE), (540, 215))
            win.blit(f_sm.render("if you dont know this as well", True, WHITE), (540, 240))
            win.blit(f_sm.render("you are not a gamer", True, WHITE), (540, 265))
            win.blit(f_sm.render("[R] to return back to menu", True, WHITE), (540, 320))
            win.blit(f_sm.render("[ESC] to escape(its there in", True, WHITE), (540, 350))
            win.blit(f_sm.render("the name im not explaining)", True, WHITE), (540, 372))
            win.blit(f_sm.render("goal: hit your apogee and", True, GRAY), (540, 410))
            win.blit(f_sm.render("stay stable (tilt under 30 deg)", True, GRAY), (540, 432))
            win.blit(f_sm.render("as i have upped the heat guys enjoyy ", True, GRAY), (540, 454))

            m_full = margin_at(com_pos, cop_pos, 1.0)
            m_empty = margin_at(com_pos, cop_pos, 0.0)
            txt("stability (cal, +ve is stable)", WHITE, 540, 480)
            txt(f"full tank:  {m_full:+.1f}", mcol(m_full), 540, 505)
            txt(f"empty tank: {m_empty:+.1f} enjoyy", mcol(m_empty), 540, 530)

        if state != "menu":
            ox = 25
            oy = CHUTE_LINE_LEN + 25
            r_surf = pygame.Surface((100, oy + 120), pygame.SRCALPHA)
            pygame.draw.polygon(r_surf, RED, [(ox + 25, oy + 5), (ox + 12, oy + 28), (ox + 38, oy + 28)])
            pygame.draw.rect(r_surf, WHITE, (ox + 12, oy + 28, 26, 50))

            if state == "descent" or state == "landed":
                cx = ox + 25
                canopy_y = 4
                canopy_h = 50
                canopy_mid = canopy_y + canopy_h // 2
                pygame.draw.arc(r_surf, ORANGE, (cx - 45, canopy_y, 90, canopy_h), 0, 3.14, 5)  # i used ai from here to line 330 and only line 335 
                pygame.draw.line(r_surf, GRAY, (cx - 45, canopy_mid), (ox + 14, oy + 28), 1)
                pygame.draw.line(r_surf, GRAY, (cx + 45, canopy_mid), (ox + 36, oy + 28), 1)
                pygame.draw.line(r_surf, GRAY, (cx - 22, canopy_y + 7), (ox + 20, oy + 28), 1)
                pygame.draw.line(r_surf, GRAY, (cx + 22, canopy_y + 7), (ox + 30, oy + 28), 1)

            if th > 0 and fuel > 0:
                fh = int(th * 0.35)
                fx = 25 - (gim * 1.4)
                pygame.draw.polygon(r_surf, RED, [(ox + 15, oy + 78), (ox + 35, oy + 78), (int(ox + fx), oy + 78 + fh)])

            pygame.draw.circle(r_surf, GREEN, (ox + 25, int(oy + 5 + cog * 7.3)), 5)
            pygame.draw.circle(r_surf, CYAN, (ox + 25, int(oy + 5 + cop * 7.3)), 8, 2)
            rot_r = pygame.transform.rotate(r_surf, -ang)  # i know these from my actual rocket
            body_offset = (oy + 53) - r_surf.get_height() // 2
            rect = rot_r.get_rect(center=(int(rx), int(ry) - 7 - body_offset))
            win.blit(rot_r, rect.topleft)

        if state == "landed":
            ov = pygame.Surface((880, 430), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 210))
            win.blit(ov, (80, 150))

            if show_graph and len(log) >= 2:
                x0 = 100
                y0 = 210
                gw = 800
                gh = 250
                total_t = max(log[-1][0], 0.1)
                max_a = max(max(p[1] for p in log), 1.0)
                txt("flight graph: yellow = altitude, cyan = tilt", WHITE, 100, 165)
                pygame.draw.rect(win, GRAY, (x0, y0, gw, gh), 2)
                for sgn in (-1, 1):
                    ly = y0 + gh // 2 - int(sgn * TILT_LIMIT / 90.0 * (gh / 2))
                    pygame.draw.line(win, RED, (x0, ly), (x0 + gw, ly), 1)
                if target_apogee <= max_a:
                    ty = y0 + gh - int(target_apogee / max_a * gh)
                    pygame.draw.line(win, WHITE, (x0, ty), (x0 + gw, ty), 1)
                
                alt_pts = []
                tilt_pts = []
                for t, a, g in log:
                    pt_x = x0 + int(t / total_t * gw)
                    pt_alt_y = y0 + gh - int(a / max_a * gh)
                    alt_pts.append((pt_x, pt_alt_y))
                    
                    clamped_g = max(-90.0, min(90.0, g))
                    pt_tilt_y = y0 + gh // 2 - int(clamped_g / 90.0 * (gh / 2))
                    tilt_pts.append((pt_x, pt_tilt_y))

                pygame.draw.lines(win, YELLOW, False, alt_pts, 2)
                pygame.draw.lines(win, CYAN, False, tilt_pts, 2)
                txt(f"peak {max_a:.0f} m", YELLOW, x0 + 5, y0 + 4)
                txt("0 s", WHITE, x0, y0 + gh + 6)
                txt(f"{total_t:.0f} s", WHITE, x0 + gw - 50, y0 + gh + 6)
                txt("white line = target apogee(dont aim for stars gng), red lines = tilt limit", GRAY, 100, 495)
                txt("[G] back to results", WHITE, 100, 520)
            else:
                if max_tilt < TILT_LIMIT:
                    stable = True
                else:
                    stable = False

                if stable and apogee_error <= 0.05 * target_apogee:
                    goal = True
                else:
                    goal = False

                win.blit(f_lg.render("ok i guess you did it- touchdown", True, GREEN), (100, 165))
                win.blit(f_sm.render("(im jeleous no worries ill make it impossible to win next time im not kidding)", True, GREEN), (100, 205))
                win.blit(f_sm.render(f"lets see your apogee: {max_alt:.1f} m", True, YELLOW), (100, 245))
                win.blit(f_sm.render("now compare with your target apogee(if you didnt achieve it then very good", True, WHITE), (100, 280))
                win.blit(f_sm.render(f"i will not have to make it harder): {target_apogee:.1f} m (Error: {apogee_error:.1f} m)", True, WHITE), (100, 302))
                win.blit(f_sm.render(f"pad offset: {lateral_offset:.1f} px (i.e how much you screwed up)", True, CYAN), (100, 340))
                
                if on_pad:
                    pad_text = "PAD HIT!"
                    pad_color = GREEN
                else:
                    pad_text = "PAD MISSED"
                    pad_color = RED
                win.blit(f_sm.render(pad_text, True, pad_color), (100, 375))

                if stable:
                    stab_desc = "Stable flight- good"
                else:
                    stab_desc = "Tumbled-RIP rocket"
                txt(f"max tilt: {max_tilt:.1f} deg  ->  {stab_desc}", GREEN if stable else RED, 100, 400)

                if goal:
                    goal_desc = "goal met you did it even after i made it harder"
                else:
                    goal_desc = "goal not met gng keep tryin and i see that my method worked"
                txt(goal_desc, GREEN if goal else RED, 100, 425)

                if rating == "S":
                    rate_color = GREEN
                elif rating == "A":
                    rate_color = YELLOW
                elif rating == "B":
                    rate_color = ORANGE
                else:
                    rate_color = RED
                txt(f"score: {score:.0f}/100 rating: {rating}", rate_color, 100, 455, f_lg)
                
                win.blit(f_sm.render("press [R] to return to menu or [ESC] to exit(dont you dare i wnat you to play again)", True, WHITE), (100, 495))
                txt("press [G] to see your flight graph(hopefully not too shabby)", GRAY, 100, 520)
                if goal:
                    txt("Damn you did it come back next week for final boss level", RED, 100, 545)

        pygame.display.flip()

if __name__ == "__main__":
    main()
    
