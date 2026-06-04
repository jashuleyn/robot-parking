import pygame
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import threading
import math

SCALE = 64
WIDTH, HEIGHT = 11 * SCALE, 11 * SCALE
FPS = 60

BG       = (30,  30,  40)
ROAD     = (50,  50,  65)
LANE     = (70,  70,  90)
FREE     = (40, 180,  80)
OCCUPIED = (220, 60,  60)
TARGET   = (255, 200,   0)
CAR_COL  = (80, 160, 255)
CAR_BODY = (60, 130, 220)
WHEEL_C  = (20,  20,  30)
TEXT_C   = (220, 220, 240)
PANEL_BG = (20,  20,  30)
WHITE    = (255, 255, 255)
GRAY     = (120, 120, 140)
RESET_C  = (255, 140,   0)


def ros_to_screen(x, y):
    return int(x * SCALE), int(HEIGHT - y * SCALE)


def draw_car(surface, x, y, angle, color=CAR_COL, alpha=255):
    car_w, car_h = 36, 22
    car_surf = pygame.Surface((car_w, car_h), pygame.SRCALPHA)
    car_surf.set_alpha(alpha)
    pygame.draw.rect(car_surf, color, (0, 3, car_w, car_h - 6), border_radius=6)
    pygame.draw.rect(car_surf, CAR_BODY, (8, 0, car_w - 18, car_h - 8), border_radius=4)
    pygame.draw.rect(car_surf, (180, 220, 255, 160), (10, 2, 10, car_h - 12), border_radius=2)
    pygame.draw.rect(car_surf, (180, 220, 255, 120), (car_w - 20, 2, 8, car_h - 12), border_radius=2)
    for wx, wy in [(4, 2), (4, car_h - 6), (car_w - 10, 2), (car_w - 10, car_h - 6)]:
        pygame.draw.rect(car_surf, WHEEL_C, (wx, wy, 8, 4), border_radius=2)
    pygame.draw.rect(car_surf, (255, 240, 100), (car_w - 4, 4, 4, 4), border_radius=1)
    pygame.draw.rect(car_surf, (255, 240, 100), (car_w - 4, car_h - 10, 4, 4), border_radius=1)
    rotated = pygame.transform.rotate(car_surf, math.degrees(angle))
    rect = rotated.get_rect(center=(x, y))
    surface.blit(rotated, rect.topleft)


def draw_parked_cars(surface, spots):
    for spot in spots:
        if spot["occupied"]:
            sx, sy = ros_to_screen(spot["x"], spot["y"])
            draw_car(surface, sx, sy, math.pi / 2, color=(160, 80, 80), alpha=180)


def draw_parking_spot(surface, sx, sy, spot, is_target, font_small):
    sw, sh = 52, 36
    rect = pygame.Rect(sx - sw // 2, sy - sh // 2, sw, sh)
    color = TARGET if is_target else (OCCUPIED if spot["occupied"] else FREE)
    pygame.draw.rect(surface, color, rect, border_radius=6)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=6)
    label = font_small.render("P" + str(spot["id"] + 1), True, (10, 10, 20))
    surface.blit(label, label.get_rect(center=(sx, sy)))


def draw_panel(surface, font, font_small, state, width):
    panel_w = 220
    panel = pygame.Rect(width - panel_w - 10, 10, panel_w, 230)
    pygame.draw.rect(surface, PANEL_BG, panel, border_radius=10)
    pygame.draw.rect(surface, GRAY, panel, 1, border_radius=10)
    title = font.render("Parking Sim", True, TEXT_C)
    surface.blit(title, (width - panel_w + 10, 22))
    if state:
        resetting = state.get("resetting", False)
        parked = state.get("parked", False)
        if resetting:
            status_text = "RESETTING..."
            status_color = RESET_C
        elif parked:
            status_text = "PARKED ✓"
            status_color = FREE
        else:
            status_text = "Searching..."
            status_color = TEXT_C
        spots = state.get("spots", [])
        free = sum(1 for s in spots if not s["occupied"])
        lines = [
            ("Car X:  " + str(state.get("x", 0)), TEXT_C),
            ("Car Y:  " + str(state.get("y", 0)), TEXT_C),
            ("Target: Spot " + str(state.get("target", 0) + 1), TEXT_C),
            ("Status: " + status_text, status_color),
            ("Free:   " + str(free) + "/" + str(len(spots)) + " spots", TEXT_C),
            ("Parked: " + str(state.get("park_count", 0)) + " times", TARGET),
        ]
        for i, (line, color) in enumerate(lines):
            txt = font_small.render(line, True, color)
            surface.blit(txt, (width - panel_w + 10, 55 + i * 28))
    else:
        txt = font_small.render("Waiting for ROS2...", True, GRAY)
        surface.blit(txt, (width - panel_w + 10, 55))


class VisualizerNode(Node):
    def __init__(self):
        super().__init__("parking_visualizer")
        self.state = None
        self.create_subscription(String, "/parking_status", self.cb, 10)

    def cb(self, msg):
        try:
            self.state = json.loads(msg.data)
        except Exception:
            pass


def ros_thread(node):
    rclpy.spin(node)


def main():
    rclpy.init()
    node = VisualizerNode()
    threading.Thread(target=ros_thread, args=(node,), daemon=True).start()

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ROS2 Parking Simulator")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("segoeui", 18, bold=True)
    font_small = pygame.font.SysFont("segoeui", 14)

    DEFAULT_SPOTS = [
        {"id": 0, "x": 2.0, "y": 8.0, "occupied": True},
        {"id": 1, "x": 5.5, "y": 8.0, "occupied": False},
        {"id": 2, "x": 9.0, "y": 8.0, "occupied": True},
        {"id": 3, "x": 2.0, "y": 2.0, "occupied": False},
        {"id": 4, "x": 5.5, "y": 2.0, "occupied": True},
        {"id": 5, "x": 9.0, "y": 2.0, "occupied": False},
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BG)
        pygame.draw.rect(screen, ROAD, (0, HEIGHT // 2 - 40, WIDTH, 80))
        pygame.draw.line(screen, LANE, (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 2)

        state = node.state
        spots = state.get("spots", DEFAULT_SPOTS) if state else DEFAULT_SPOTS
        target_id = state.get("target", -1) if state else -1

        draw_parked_cars(screen, spots)

        for spot in spots:
            sx, sy = ros_to_screen(spot["x"], spot["y"])
            draw_parking_spot(screen, sx, sy, spot, spot["id"] == target_id, font_small)

        if state:
            resetting = state.get("resetting", False)
            cx, cy = ros_to_screen(state["x"], state["y"])
            color = RESET_C if resetting else CAR_COL
            draw_car(screen, cx, cy, state["theta"], color=color)

        for i, (color, label) in enumerate([
            (FREE, "Free"), (OCCUPIED, "Occupied"),
            (TARGET, "Target"), (RESET_C, "Resetting")
        ]):
            lx, ly = 14, HEIGHT - 100 + i * 22
            pygame.draw.rect(screen, color, (lx, ly, 16, 14), border_radius=3)
            txt = font_small.render(label, True, TEXT_C)
            screen.blit(txt, (lx + 22, ly))

        draw_panel(screen, font, font_small, state, WIDTH)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
