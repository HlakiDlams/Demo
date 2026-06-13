import struct, zlib, os

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
WH = (240, 236, 228)

def make_icon(sz):
    half = sz // 2
    border = max(3, sz // 16)
    diamond_r = sz // 4      # diamond radius
    inner_r = sz // 10       # inner circle radius

    pixels = []
    for y in range(sz):
        row = []
        for x in range(sz):
            nx = x - half
            ny = y - half
            # Border ring
            if x < border or x >= sz - border or y < border or y >= sz - border:
                row.append(PK)
            # Diamond (rotated square)
            elif abs(nx) + abs(ny) < diamond_r:
                dist_inner = abs(nx) + abs(ny)
                if dist_inner < inner_r:
                    row.append(BK)
                else:
                    # Pink fill with subtle gradient feel
                    t = (dist_inner - inner_r) / (diamond_r - inner_r)
                    r = int(PK[0] * t + BK[0] * (1-t))
                    g = int(PK[1] * t + BK[1] * (1-t))
                    b = int(PK[2] * t + BK[2] * (1-t))
                    row.append((r, g, b))
            else:
                row.append(BK)
        pixels.append(row)
    return make_png(sz, sz, pixels)

os.makedirs('icons', exist_ok=True)
for sz in [72, 96, 128, 144, 152, 192, 384, 512]:
    data = make_icon(sz)
    path = f'icons/icon-{sz}.png'
    with open(path, 'wb') as f:
        f.write(data)
    print(f'  ✓ {path} ({len(data)//1024}KB)')

print('All icons generated.')
