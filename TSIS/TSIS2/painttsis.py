import pygame
import sys
from collections import deque
from datetime import datetime

pygame.init()

SCREEN_W = 900
SCREEN_H  = 650
PANEL_H   = 70

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

# All tools including new ones
TOOLS = ["Pen", "Line", "Rect", "Circle", "Eraser", "Fill", "Text",
         "Square", "RTriangle", "EqTriangle", "Rhombus"]

TOOL_LABELS = {
    "Pen": "Pen",
    "Line": "Line",
    "Rect": "Rect",
    "Circle": "Circle",
    "Eraser": "Eraser",
    "Fill": "Fill",
    "Text": "Text",
    "Square": "Square",
    "RTriangle": "R.Tri",
    "EqTriangle": "Tri",
    "Rhombus": "Rhombus",
}

# Brush sizes: small, medium, large
BRUSH_SIZES = [2, 5, 10]

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint Extended")
clock = pygame.time.Clock()

font       = pygame.font.SysFont("Arial", 14)
font_large = pygame.font.SysFont("Arial", 20)

canvas = pygame.Surface((SCREEN_W, SCREEN_H - PANEL_H))
canvas.fill(WHITE)


# ── Flood Fill ────────────────────────────────────────────────────────────────

def flood_fill(surface, x, y, new_color):
    """BFS flood fill on a pygame.Surface."""
    w, h = surface.get_size()
    if x < 0 or x >= w or y < 0 or y >= h:
        return
    target_color = surface.get_at((x, y))[:3]
    new_color_3  = new_color[:3] if len(new_color) == 4 else new_color
    if target_color == new_color_3:
        return

    queue = deque()
    queue.append((x, y))
    visited = set()
    visited.add((x, y))

    while queue:
        cx, cy = queue.popleft()
        if surface.get_at((cx, cy))[:3] != target_color:
            continue
        surface.set_at((cx, cy), new_color_3)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))


# ── Shape helpers ─────────────────────────────────────────────────────────────

def draw_square(surface, color, start, end, size, filled=False):
    side = min(abs(end[0] - start[0]), abs(end[1] - start[1]))
    sx = start[0]
    sy = start[1]
    ex = sx + (side if end[0] >= start[0] else -side)
    ey = sy + (side if end[1] >= start[1] else -side)
    x = min(sx, ex)
    y = min(sy, ey)
    lw = 0 if filled else size
    pygame.draw.rect(surface, color, (x, y, side, side), lw)


def draw_right_triangle(surface, color, start, end, size, filled=False):
    p1 = start
    p2 = (start[0], end[1])
    p3 = end
    lw = 0 if filled else size
    pygame.draw.polygon(surface, color, [p1, p2, p3], lw)


def draw_equilateral_triangle(surface, color, start, end, size, filled=False):
    import math
    base = abs(end[0] - start[0]) or 1
    direction = 1 if end[0] >= start[0] else -1
    x1 = min(start[0], end[0])
    x2 = max(start[0], end[0])
    y_base = end[1]
    height = int(base * math.sqrt(3) / 2)
    p1 = (x1, y_base)
    p2 = (x2, y_base)
    p3 = ((x1 + x2) // 2, y_base - height)
    lw = 0 if filled else size
    pygame.draw.polygon(surface, color, [p1, p2, p3], lw)


def draw_rhombus(surface, color, start, end, size, filled=False):
    cx = (start[0] + end[0]) // 2
    cy = (start[1] + end[1]) // 2
    hw = abs(end[0] - start[0]) // 2
    hh = abs(end[1] - start[1]) // 2
    points = [(cx, cy - hh), (cx + hw, cy), (cx, cy + hh), (cx - hw, cy)]
    lw = 0 if filled else size
    pygame.draw.polygon(surface, color, points, lw)


# ── Panel rendering ───────────────────────────────────────────────────────────

def draw_panel(tool, color, brush_idx):
    panel = pygame.Rect(0, 0, SCREEN_W, PANEL_H)
    pygame.draw.rect(screen, LGRAY, panel)
    pygame.draw.line(screen, DGRAY, (0, PANEL_H), (SCREEN_W, PANEL_H), 1)

    # Color swatches (row 1 at y=6, row 2 at y=30)
    for i, c in enumerate(COLORS):
        rect1 = pygame.Rect(8 + i * 28, 6, 24, 22)
        pygame.draw.rect(screen, c, rect1)
        pygame.draw.rect(screen, DGRAY, rect1, 1)
        if c == color:
            pygame.draw.rect(screen, BLACK, rect1, 3)
        rect2 = pygame.Rect(8 + i * 28, 30, 24, 14)
        pygame.draw.rect(screen, c, rect2)
        pygame.draw.rect(screen, DGRAY, rect2, 1)
        if c == color:
            pygame.draw.rect(screen, BLACK, rect2.inflate(2, 2), 2)

    # Brush size buttons (1 / 2 / 3) on the right side of colors
    bx = 8 + len(COLORS) * 28 + 8
    size_labels = ["S(1)", "M(2)", "L(3)"]
    for i, lbl in enumerate(size_labels):
        brect = pygame.Rect(bx + i * 52, 6, 48, 38)
        bg = (180, 210, 255) if i == brush_idx else GRAY
        pygame.draw.rect(screen, bg, brect, border_radius=5)
        pygame.draw.rect(screen, DGRAY, brect, 1, border_radius=5)
        dot_r = BRUSH_SIZES[i] // 2 + 2
        pygame.draw.circle(screen, BLACK, (brect.centerx, brect.centery - 6), dot_r)
        lbl_surf = font.render(lbl, True, BLACK)
        screen.blit(lbl_surf, (brect.centerx - lbl_surf.get_width() // 2, brect.bottom - 14))

    # Tools – two rows
    tools_row1 = ["Pen", "Line", "Rect", "Circle", "Eraser", "Fill", "Text"]
    tools_row2 = ["Square", "RTriangle", "EqTriangle", "Rhombus"]
    tx = 8
    btn_w = 60
    btn_gap = 4
    for i, t in enumerate(tools_row1):
        rect = pygame.Rect(tx + i * (btn_w + btn_gap), 6, btn_w, 20)
        # Recalculate x to start after color + brush area
        rect.x = 560 + i * (btn_w + btn_gap)
        bg = (180, 210, 255) if t == tool else GRAY
        pygame.draw.rect(screen, bg, rect, border_radius=3)
        pygame.draw.rect(screen, DGRAY, rect, 1, border_radius=3)
        lbl = font.render(TOOL_LABELS[t], True, BLACK)
        screen.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                          rect.centery - lbl.get_height() // 2))
    for i, t in enumerate(tools_row2):
        rect = pygame.Rect(560 + i * (btn_w + btn_gap), 30, btn_w, 20)
        bg = (180, 210, 255) if t == tool else GRAY
        pygame.draw.rect(screen, bg, rect, border_radius=3)
        pygame.draw.rect(screen, DGRAY, rect, 1, border_radius=3)
        lbl = font.render(TOOL_LABELS[t], True, BLACK)
        screen.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                          rect.centery - lbl.get_height() // 2))

    # Hint bar
    hint = font.render("C=clear | Ctrl+S=save | 1/2/3=size | Esc=cancel text", True, DGRAY)
    screen.blit(hint, (560, 52))


def get_tool_rect(t):
    """Return screen rect for a tool button."""
    tools_row1 = ["Pen", "Line", "Rect", "Circle", "Eraser", "Fill", "Text"]
    tools_row2 = ["Square", "RTriangle", "EqTriangle", "Rhombus"]
    btn_w = 60
    btn_gap = 4
    if t in tools_row1:
        i = tools_row1.index(t)
        return pygame.Rect(560 + i * (btn_w + btn_gap), 6, btn_w, 20)
    elif t in tools_row2:
        i = tools_row2.index(t)
        return pygame.Rect(560 + i * (btn_w + btn_gap), 30, btn_w, 20)
    return None


# ── Preview & canvas drawing ──────────────────────────────────────────────────

def draw_preview(tool, start, end, color, size):
    """Draw a live preview on screen (not committed to canvas)."""
    s = start
    e = end
    if tool == "Line":
        pygame.draw.line(screen, color, s, e, size)
    elif tool == "Rect":
        x = min(s[0], e[0]); y = min(s[1], e[1])
        pygame.draw.rect(screen, color, (x, y, abs(e[0]-s[0]), abs(e[1]-s[1])), size)
    elif tool == "Circle":
        cx = (s[0]+e[0])//2; cy = (s[1]+e[1])//2
        r  = max(abs(e[0]-s[0]), abs(e[1]-s[1])) // 2
        if r > 0:
            pygame.draw.circle(screen, color, (cx, cy), r, size)
    elif tool == "Square":
        draw_square(screen, color, s, e, size)
    elif tool == "RTriangle":
        draw_right_triangle(screen, color, s, e, size)
    elif tool == "EqTriangle":
        draw_equilateral_triangle(screen, color, s, e, size)
    elif tool == "Rhombus":
        draw_rhombus(screen, color, s, e, size)


def apply_to_canvas(tool, start, end, color, size):
    """Commit shape to canvas, adjusting for panel offset."""
    def off(p):
        return (p[0], p[1] - PANEL_H)
    s = off(start)
    e = off(end)
    if tool == "Line":
        pygame.draw.line(canvas, color, s, e, size)
    elif tool == "Rect":
        x = min(s[0], e[0]); y = min(s[1], e[1])
        pygame.draw.rect(canvas, color, (x, y, abs(e[0]-s[0]), abs(e[1]-s[1])), size)
    elif tool == "Circle":
        cx = (s[0]+e[0])//2; cy = (s[1]+e[1])//2
        r  = max(abs(e[0]-s[0]), abs(e[1]-s[1])) // 2
        if r > 0:
            pygame.draw.circle(canvas, color, (cx, cy), r, size)
    elif tool == "Square":
        draw_square(canvas, color, s, e, size)
    elif tool == "RTriangle":
        draw_right_triangle(canvas, color, s, e, size)
    elif tool == "EqTriangle":
        draw_equilateral_triangle(canvas, color, s, e, size)
    elif tool == "Rhombus":
        draw_rhombus(canvas, color, s, e, size)


def in_canvas(pos):
    return pos[1] > PANEL_H


def canvas_pos(pos):
    return (pos[0], pos[1] - PANEL_H)


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    tool       = "Pen"
    color      = COLORS[0]
    brush_idx  = 1          # default medium
    size       = BRUSH_SIZES[brush_idx]
    drawing    = False
    start_pos  = None
    last_pos   = None

    # Text tool state
    text_mode    = False
    text_pos     = None     # canvas coordinates
    text_buffer  = ""

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()
        size = BRUSH_SIZES[brush_idx]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ── Keyboard ──────────────────────────────────────────────────
            if event.type == pygame.KEYDOWN:

                # Text tool: capture typing
                if text_mode:
                    if event.key == pygame.K_RETURN:
                        # Commit text to canvas
                        if text_buffer:
                            txt_surf = font_large.render(text_buffer, True, color)
                            canvas.blit(txt_surf, text_pos)
                        text_mode   = False
                        text_pos    = None
                        text_buffer = ""
                    elif event.key == pygame.K_ESCAPE:
                        text_mode   = False
                        text_pos    = None
                        text_buffer = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            text_buffer += event.unicode
                    continue  # don't process other shortcuts while typing

                # Global shortcuts
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_c:
                    canvas.fill(WHITE)
                if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    fname = f"canvas_{ts}.png"
                    pygame.image.save(canvas, fname)
                    pygame.display.set_caption(f"Paint Extended — saved {fname}")
                # Brush size shortcuts
                if event.key == pygame.K_1:
                    brush_idx = 0
                if event.key == pygame.K_2:
                    brush_idx = 1
                if event.key == pygame.K_3:
                    brush_idx = 2

            # ── Mouse button down ──────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if text_mode:
                    # Clicking elsewhere while in text mode commits text
                    if text_buffer:
                        txt_surf = font_large.render(text_buffer, True, color)
                        canvas.blit(txt_surf, text_pos)
                    text_mode   = False
                    text_pos    = None
                    text_buffer = ""

                # Color swatches
                clicked_color = False
                for i, c in enumerate(COLORS):
                    rx = 8 + i * 28
                    if rx <= mx <= rx + 24 and (6 <= my <= 28 or 30 <= my <= 44):
                        color = c
                        clicked_color = True
                        break
                if clicked_color:
                    continue

                # Brush size buttons
                bx = 8 + len(COLORS) * 28 + 8
                clicked_brush = False
                for i in range(3):
                    brect = pygame.Rect(bx + i * 52, 6, 48, 38)
                    if brect.collidepoint(mx, my):
                        brush_idx = i
                        clicked_brush = True
                        break
                if clicked_brush:
                    continue

                # Tool buttons
                clicked_tool = False
                for t in TOOLS:
                    r = get_tool_rect(t)
                    if r and r.collidepoint(mx, my):
                        tool = t
                        clicked_tool = True
                        break
                if clicked_tool:
                    continue

                # Canvas interaction
                if in_canvas((mx, my)):
                    if tool == "Fill":
                        cx, cy = canvas_pos((mx, my))
                        flood_fill(canvas, cx, cy, color)
                    elif tool == "Text":
                        text_mode   = True
                        text_pos    = canvas_pos((mx, my))
                        text_buffer = ""
                    else:
                        drawing   = True
                        start_pos = (mx, my)
                        last_pos  = (mx, my)

            # ── Mouse button up ────────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and start_pos:
                    shape_tools = ("Line", "Rect", "Circle",
                                   "Square", "RTriangle", "EqTriangle", "Rhombus")
                    if tool in shape_tools:
                        apply_to_canvas(tool, start_pos, (mx, my), color, size)
                drawing   = False
                start_pos = None
                last_pos  = None

            # ── Mouse motion ───────────────────────────────────────────────
            if event.type == pygame.MOUSEMOTION:
                if drawing and in_canvas((mx, my)):
                    if tool == "Pen":
                        if last_pos:
                            lp = canvas_pos(last_pos)
                            cp = canvas_pos((mx, my))
                            pygame.draw.line(canvas, color, lp, cp, size)
                        last_pos = (mx, my)
                    elif tool == "Eraser":
                        pygame.draw.circle(canvas, WHITE, canvas_pos((mx, my)), size * 2)
                        last_pos = (mx, my)

        # ── Continuous pen/eraser while held ──────────────────────────────
        if drawing and in_canvas((mx, my)):
            if tool == "Pen":
                pass  # handled in MOUSEMOTION
            elif tool == "Eraser":
                pass  # handled in MOUSEMOTION

        # ── Render ────────────────────────────────────────────────────────
        screen.fill(LGRAY)
        screen.blit(canvas, (0, PANEL_H))
        draw_panel(tool, color, brush_idx)

        # Shape preview while dragging
        if drawing and start_pos:
            shape_tools = ("Line", "Rect", "Circle",
                           "Square", "RTriangle", "EqTriangle", "Rhombus")
            if tool in shape_tools:
                draw_preview(tool, start_pos, (mx, my), color, size)

        # Text preview
        if text_mode and text_pos:
            preview_txt = text_buffer + "|"
            txt_surf = font_large.render(preview_txt, True, color)
            sx = text_pos[0]
            sy = text_pos[1] + PANEL_H
            # semi-transparent bg
            bg = pygame.Surface((txt_surf.get_width() + 4, txt_surf.get_height() + 2))
            bg.set_alpha(160)
            bg.fill(WHITE)
            screen.blit(bg, (sx - 2, sy - 1))
            screen.blit(txt_surf, (sx, sy))

        # Cursor
        if tool == "Eraser":
            pygame.draw.circle(screen, DGRAY, (mx, my), size * 2, 1)
        elif tool == "Fill":
            pygame.draw.circle(screen, color,  (mx, my), 8)
            pygame.draw.circle(screen, BLACK,  (mx, my), 8, 1)
        elif tool != "Text":
            r = max(size // 2, 2)
            pygame.draw.circle(screen, color, (mx, my), r)
            pygame.draw.circle(screen, BLACK, (mx, my), r, 1)

        pygame.display.flip()


if __name__ == "__main__":
    main()