import pygame
import sys

pygame.init()

SCREEN_W = 900
SCREEN_H = 650
PANEL_H  = 60

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GRAY   = (200, 200, 200)
DGRAY  = (120, 120, 120)
LGRAY  = (240, 240, 240)

COLORS = [
    (0,   0,   0),
    (255, 255, 255),
    (220, 50,  50),
    (50,  180, 50),
    (50,  80,  220),
    (255, 200, 0),
    (255, 120, 0),
    (180, 50,  180),
    (0,   180, 180),
    (139, 90,  43),
    (255, 150, 180),
    (100, 100, 100),
]

TOOLS = ["Pen", "Line", "Rect", "Circle", "Eraser"]

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint")
clock  = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 16)

canvas = pygame.Surface((SCREEN_W, SCREEN_H - PANEL_H))
canvas.fill(WHITE)


def draw_panel(tool, color, size):
    panel = pygame.Rect(0, 0, SCREEN_W, PANEL_H)
    pygame.draw.rect(screen, LGRAY, panel)
    pygame.draw.line(screen, DGRAY, (0, PANEL_H), (SCREEN_W, PANEL_H), 1)

    x = 8
    for i, c in enumerate(COLORS):
        rect = pygame.Rect(x + i * 28, 10, 24, 24)
        pygame.draw.rect(screen, c, rect)
        pygame.draw.rect(screen, DGRAY, rect, 1)
        if c == color:
            pygame.draw.rect(screen, BLACK, rect, 3)

    x = 8
    for i, c in enumerate(COLORS):
        rect = pygame.Rect(x + i * 28, 36, 24, 14)
        pygame.draw.rect(screen, c, rect)
        pygame.draw.rect(screen, DGRAY, rect, 1)
        if c == color:
            pygame.draw.rect(screen, BLACK, rect.inflate(2, 2), 2)

    tx = 360
    for i, t in enumerate(TOOLS):
        rect = pygame.Rect(tx + i * 82, 12, 76, 36)
        bg = (180, 210, 255) if t == tool else GRAY
        pygame.draw.rect(screen, bg, rect, border_radius=5)
        pygame.draw.rect(screen, DGRAY, rect, 1, border_radius=5)
        label = font.render(t, True, BLACK)
        screen.blit(label, (rect.centerx - label.get_width() // 2,
                             rect.centery - label.get_height() // 2))

    sx = SCREEN_W - 160
    pygame.draw.rect(screen, LGRAY, (sx, 8, 150, 44), border_radius=4)
    pygame.draw.rect(screen, DGRAY, (sx, 8, 150, 44), 1, border_radius=4)
    s_label = font.render(f"Size: {size}", True, BLACK)
    screen.blit(s_label, (sx + 6, 12))
    pygame.draw.rect(screen, DGRAY, (sx + 6, 32, 138, 14), border_radius=3)
    fill_w = int(138 * (size - 1) / 49)
    pygame.draw.rect(screen, (50, 120, 220), (sx + 6, 32, fill_w, 14), border_radius=3)


def draw_preview(tool, start, end, color, size):
    if tool == "Line":
        pygame.draw.line(screen, color, start, end, size)
    elif tool == "Rect":
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        pygame.draw.rect(screen, color, (x, y, w, h), 2)
    elif tool == "Circle":
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        r  = max(abs(end[0] - start[0]), abs(end[1] - start[1])) // 2
        if r > 0:
            pygame.draw.circle(screen, color, (cx, cy), r, 2)


def apply_to_canvas(tool, start, end, color, size):
    if tool == "Line":
        pygame.draw.line(canvas, color, offset(start), offset(end), size)
    elif tool == "Rect":
        x = min(start[0], end[0])
        y = min(start[1], end[1]) - PANEL_H
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        pygame.draw.rect(canvas, color, (x, y, w, h), 2)
    elif tool == "Circle":
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2 - PANEL_H
        r  = max(abs(end[0] - start[0]), abs(end[1] - start[1])) // 2
        if r > 0:
            pygame.draw.circle(canvas, color, (cx, cy), r, 2)


def offset(pos):
    return (pos[0], pos[1] - PANEL_H)


def in_canvas(pos):
    return pos[1] > PANEL_H


def main():
    tool         = "Pen"
    color        = COLORS[0]
    size         = 4
    drawing      = False
    start_pos    = None
    drag_size    = False

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_c:
                    canvas.fill(WHITE)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                sx = SCREEN_W - 160
                if 32 <= my <= 46 and sx + 6 <= mx <= sx + 144:
                    drag_size = True
                    size = max(1, min(50, int((mx - sx - 6) / 138 * 49) + 1))
                    continue

                for i, c in enumerate(COLORS):
                    rx = 8 + i * 28
                    if rx <= mx <= rx + 24 and (10 <= my <= 34 or 36 <= my <= 50):
                        color = c
                        break

                tx = 360
                for i, t in enumerate(TOOLS):
                    rx = tx + i * 82
                    if rx <= mx <= rx + 76 and 12 <= my <= 48:
                        tool = t
                        break

                if in_canvas((mx, my)):
                    drawing   = True
                    start_pos = (mx, my)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                drag_size = False
                if drawing and start_pos and tool in ("Line", "Rect", "Circle"):
                    apply_to_canvas(tool, start_pos, (mx, my), color, size)
                drawing   = False
                start_pos = None

            if event.type == pygame.MOUSEMOTION:
                if drag_size:
                    sx = SCREEN_W - 160
                    size = max(1, min(50, int((mx - sx - 6) / 138 * 49) + 1))

        if drawing and in_canvas((mx, my)):
            if tool == "Pen":
                pygame.draw.circle(canvas, color, offset((mx, my)), size // 2)
            elif tool == "Eraser":
                pygame.draw.circle(canvas, WHITE, offset((mx, my)), size)

        screen.fill(LGRAY)
        screen.blit(canvas, (0, PANEL_H))
        draw_panel(tool, color, size)

        if drawing and start_pos and tool in ("Line", "Rect", "Circle"):
            draw_preview(tool, start_pos, (mx, my), color, size)

        if tool == "Eraser":
            pygame.draw.circle(screen, DGRAY, (mx, my), size, 1)
        else:
            pygame.draw.circle(screen, color, (mx, my), max(size // 2, 3))
            pygame.draw.circle(screen, BLACK,  (mx, my), max(size // 2, 3), 1)

        pygame.display.flip()


if __name__ == "__main__":
    main()