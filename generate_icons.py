import struct, zlib, os, math

def make_png(w, h, pixels):
    def chunk(tag, d):
        crc = zlib.crc32(tag + d) & 0xffffffff
        return struct.pack('>I', len(d)) + tag + d + struct.pack('>I', crc)
    rows = []
    for row in pixels:
        rows.append(b'\x00' + bytes([c for px in row for c in px]))
    raw = b''.join(rows)
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', zlib.compress(raw, 9))
            + chunk(b'IEND', b''))

BK = (8, 8, 8)
PK = (255, 110, 180)
PK_DIM = (100, 40, 70)

def star_contains(px, py, cx, cy, outer_r, inner_r, points=5):
    """Returns distance-based alpha for a star polygon (0=inside, >0=outside)."""
    dx = px - cx
    dy = py - cy
    dist = math.sqrt(dx*dx + dy*dy)
    if dist == 0:
        return 0.0
    angle = math.atan2(dy, dx) + math.pi / 2
    sector_angle = 2 * math.pi / points
    sector = round(angle / sector_angle) * sector_angle
    delta = abs(angle - sector) % (2 * math.pi)
    if delta > math.pi:
        delta = 2 * math.pi - delta
    # interpolate between outer and inner radius
    t = delta / (sector_angle / 2)
    r_boundary = outer_r * (1 - t) + inner_r * t
    return dist - r_boundary

def draw_h(pixels, cx, cy, size, thickness, color):
    """Draw letter H centered at (cx, cy)."""
    half_w = size * 0.28
    half_h = size * 0.38
    bar_h = thickness * 0.5
    for y in range(len(pixels)):
        for x in range(len(pixels[0])):
            dx = x - cx
            dy = y - cy
            # Left vertical bar
            if abs(dx + half_w) < thickness and abs(dy) < half_h:
                pixels[y][x] = color
            # Right vertical bar
            if abs(dx - half_w) < thickness and abs(dy) < half_h:
                pixels[y][x] = color
            # Middle crossbar
            if abs(dx) < half_w + thickness and abs(dy) < bar_h:
                pixels[y][x] = color

def draw_f(pixels, cx, cy, size, thickness, color):
    """Draw letter F centered at (cx, cy)."""
    half_w = size * 0.22
    half_h = size * 0.38
    mid_h = size * 0.05
    top_w = size * 0.25
    for y in range(len(pixels)):
        for x in range(len(pixels[0])):
            dx = x - cx
            dy = y - cy
            # Vertical spine on left
            if abs(dx + half_w) < thickness and abs(dy) < half_h:
                pixels[y][x] = color
            # Top horizontal bar
            if dx > -half_w - thickness and dx < half_w + top_w and abs(dy + half_h) < thickness:
                pixels[y][x] = color
            # Middle horizontal bar (shorter)
            if dx > -half_w - thickness and dx < half_w and abs(dy - mid_h) < thickness:
                pixels[y][x] = color

def make_icon(sz):
    half = sz // 2
    outer_r = sz * 0.42
    inner_r = sz * 0.18
    glow_extra = sz * 0.04

    pixels = [[BK] * sz for _ in range(sz)]

    # Draw star with glow
    for y in range(sz):
        for x in range(sz):
            d = star_contains(x, y, half, half, outer_r, inner_r, 5)
            if d <= 0:
                pixels[y][x] = PK
            elif d < glow_extra:
                t = 1 - (d / glow_extra)
                r = int(PK[0] * t * 0.6 + BK[0])
                g = int(PK[1] * t * 0.6 + BK[1])
                b = int(PK[2] * t * 0.6 + BK[2])
                pixels[y][x] = (min(255,r), min(255,g), min(255,b))

    # Draw HF letters inside star — split left/right
    letter_size = sz * 0.13
    thickness = max(1.5, sz * 0.045)
    # H on the left side of center, F on the right
    offset = sz * 0.12
    draw_h(pixels, int(half - offset), half, letter_size, thickness, BK)
    draw_f(pixels, int(half + offset * 0.85), half, letter_size, thickness, BK)

    return make_png(sz, sz, pixels)

os.makedirs('icons', exist_ok=True)
for sz in [72, 96, 128, 144, 152, 192, 384, 512]:
    data = make_icon(sz)
    path = f'icons/icon-{sz}.png'
    with open(path, 'wb') as f:
        f.write(data)
    print(f'  ✓ {path} ({len(data)//1024}KB)')

print('All icons generated.')
