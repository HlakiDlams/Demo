"""Replace Capacitor's default placeholder launcher icons and splash screens
with the real HF543 star branding, generated from icons/icon-512.png using
pure Python stdlib (no Pillow/ImageMagick available in this environment)."""
import struct, zlib, os

def read_png_rgb(filename):
    with open(filename, 'rb') as f:
        raw_file = f.read()
    assert raw_file[:8] == b'\x89PNG\r\n\x1a\n', "Not a PNG"
    pos = 8
    idat = bytearray()
    w = h = bpp = 0
    while pos < len(raw_file):
        length = struct.unpack('>I', raw_file[pos:pos+4])[0]
        tag = raw_file[pos+4:pos+8]
        cdata = raw_file[pos+8:pos+8+length]
        pos += 12 + length
        if tag == b'IHDR':
            w, h = struct.unpack('>II', cdata[:8])
            bpp = cdata[9]
        elif tag == b'IDAT':
            idat += cdata
        elif tag == b'IEND':
            break
    raw = zlib.decompress(bytes(idat))
    channels = 4 if bpp == 6 else 3
    stride = w * channels
    prev = bytearray(stride)
    pixels = []
    i = 0
    for _ in range(h):
        ft = raw[i]; i += 1
        row = bytearray(raw[i:i+stride]); i += stride
        if ft == 1:
            for x in range(channels, stride):
                row[x] = (row[x] + row[x-channels]) & 0xff
        elif ft == 2:
            for x in range(stride):
                row[x] = (row[x] + prev[x]) & 0xff
        elif ft == 3:
            for x in range(stride):
                a = row[x-channels] if x >= channels else 0
                row[x] = (row[x] + ((a + prev[x]) >> 1)) & 0xff
        elif ft == 4:
            for x in range(stride):
                a = row[x-channels] if x >= channels else 0
                b = prev[x]
                c = prev[x-channels] if x >= channels else 0
                pa,pb,pc = abs(b-c),abs(a-c),abs(a+b-2*c)
                pr = a if pa<=pb and pa<=pc else (b if pb<=pc else c)
                row[x] = (row[x] + pr) & 0xff
        if channels == 4:
            pixels.append(bytes(b for j in range(w) for b in (row[j*4], row[j*4+1], row[j*4+2])))
        else:
            pixels.append(bytes(row))
        prev = row
    return w, h, pixels

def write_png_rgb(filename, w, h, rows):
    def chunk(tag, d):
        crc = zlib.crc32(tag+d) & 0xffffffff
        return struct.pack('>I', len(d)) + tag + d + struct.pack('>I', crc)
    raw = b''.join(b'\x00' + r for r in rows)
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    out = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', zlib.compress(raw, 9))
           + chunk(b'IEND', b''))
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
        f.write(out)

def write_png_rgba(filename, w, h, rows_rgba):
    def chunk(tag, d):
        crc = zlib.crc32(tag+d) & 0xffffffff
        return struct.pack('>I', len(d)) + tag + d + struct.pack('>I', crc)
    raw = b''.join(b'\x00' + r for r in rows_rgba)
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
    out = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', zlib.compress(raw, 9))
           + chunk(b'IEND', b''))
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
        f.write(out)

def resize_nearest_rgb(src_pixels, src_w, src_h, dst_w, dst_h):
    rows = []
    for dy in range(dst_h):
        sy = min(int(dy * src_h / dst_h), src_h-1)
        src_row = src_pixels[sy]
        row = bytearray(dst_w * 3)
        for dx in range(dst_w):
            sx = min(int(dx * src_w / dst_w), src_w-1)
            sp, dp = sx*3, dx*3
            row[dp:dp+3] = src_row[sp:sp+3]
        rows.append(bytes(row))
    return rows

BRAND_BG = (8, 8, 8)  # matches site's --bg

def make_canvas_rgb(w, h, color=BRAND_BG):
    row = bytes(color) * w
    return [row for _ in range(h)]

def paste_rgb(canvas_rows, w, h, patch_rows, pw, ph, x0, y0):
    rows = [bytearray(r) for r in canvas_rows]
    for py in range(ph):
        cy = y0 + py
        if cy < 0 or cy >= h:
            continue
        src = patch_rows[py]
        dst = rows[cy]
        for px in range(pw):
            cx = x0 + px
            if cx < 0 or cx >= w:
                continue
            dst[cx*3:cx*3+3] = src[px*3:px*3+3]
    return [bytes(r) for r in rows]

print('Reading source icon...')
sw, sh, src = read_png_rgb('icons/icon-512.png')
print(f'  Source: {sw}x{sh}')

# --- Launcher icons (legacy square, round, and adaptive foreground) ---
LAUNCHER_SIZES = {
    'mdpi': (48, 108),
    'hdpi': (72, 162),
    'xhdpi': (96, 216),
    'xxhdpi': (144, 324),
    'xxxhdpi': (192, 432),
}
res_dir = 'android/app/src/main/res'
for density, (legacy_sz, fg_sz) in LAUNCHER_SIZES.items():
    legacy = resize_nearest_rgb(src, sw, sh, legacy_sz, legacy_sz)
    write_png_rgb(f'{res_dir}/mipmap-{density}/ic_launcher.png', legacy_sz, legacy_sz, legacy)
    write_png_rgb(f'{res_dir}/mipmap-{density}/ic_launcher_round.png', legacy_sz, legacy_sz, legacy)
    fg = resize_nearest_rgb(src, sw, sh, fg_sz, fg_sz)
    write_png_rgb(f'{res_dir}/mipmap-{density}/ic_launcher_foreground.png', fg_sz, fg_sz, fg)
    print(f'  ✓ {density}: ic_launcher {legacy_sz}px, foreground {fg_sz}px')

# --- Splash screens: branded dark background with centered star logo ---
SPLASH_SIZES = {
    'drawable': (480, 320),
    'drawable-land-mdpi': (480, 320),
    'drawable-land-hdpi': (800, 480),
    'drawable-land-xhdpi': (1280, 720),
    'drawable-land-xxhdpi': (1600, 960),
    'drawable-land-xxxhdpi': (1920, 1280),
    'drawable-port-mdpi': (320, 480),
    'drawable-port-hdpi': (480, 800),
    'drawable-port-xhdpi': (720, 1280),
    'drawable-port-xxhdpi': (960, 1600),
    'drawable-port-xxxhdpi': (1280, 1920),
}
for folder, (w, h) in SPLASH_SIZES.items():
    logo_sz = int(min(w, h) * 0.42)
    logo = resize_nearest_rgb(src, sw, sh, logo_sz, logo_sz)
    canvas = make_canvas_rgb(w, h)
    canvas = paste_rgb(canvas, w, h, logo, logo_sz, logo_sz, (w-logo_sz)//2, (h-logo_sz)//2)
    write_png_rgb(f'{res_dir}/{folder}/splash.png', w, h, canvas)
    print(f'  ✓ {folder}: {w}x{h} splash')

print('Android launcher icons and splash screens rebranded.')
