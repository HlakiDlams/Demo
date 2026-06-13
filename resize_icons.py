"""Resize the HF543 icon PNG to all required sizes using pure Python stdlib."""
import struct, zlib, sys

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
            bpp = cdata[9]  # color type: 2=RGB, 6=RGBA
            channels = 4 if bpp == 6 else 3
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
        # Extract RGB only
        if channels == 4:
            pixels.append(bytes(b for j in range(w) for b in (row[j*4], row[j*4+1], row[j*4+2])))
        else:
            pixels.append(bytes(row))
        prev = row
    return w, h, pixels  # pixels: list of bytes, each row is w*3 bytes

def write_png(filename, w, h, pixels_rows):
    def chunk(tag, d):
        crc = zlib.crc32(tag+d) & 0xffffffff
        return struct.pack('>I',len(d)) + tag + d + struct.pack('>I',crc)
    raw = b''.join(b'\x00' + r for r in pixels_rows)
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    out = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', zlib.compress(raw, 6))
           + chunk(b'IEND', b''))
    with open(filename, 'wb') as f:
        f.write(out)

def resize_nearest(src_pixels, src_w, src_h, dst_w, dst_h):
    rows = []
    for dy in range(dst_h):
        sy = min(int(dy * src_h / dst_h), src_h-1)
        src_row = src_pixels[sy]
        row = bytearray(dst_w * 3)
        for dx in range(dst_w):
            sx = min(int(dx * src_w / dst_w), src_w-1)
            sp = sx * 3
            dp = dx * 3
            row[dp] = src_row[sp]
            row[dp+1] = src_row[sp+1]
            row[dp+2] = src_row[sp+2]
        rows.append(bytes(row))
    return rows

import os
src = 'icons/icon-512.png'
print(f'Reading source PNG...')
sw, sh, src_pixels = read_png_rgb(src)
print(f'  Source: {sw}x{sh}')

for sz in [72, 96, 128, 144, 152, 192, 384]:
    print(f'  Resizing to {sz}x{sz}...', end=' ', flush=True)
    rows = resize_nearest(src_pixels, sw, sh, sz, sz)
    out = f'icons/icon-{sz}.png'
    write_png(out, sz, sz, rows)
    print(f'done ({os.path.getsize(out)//1024}KB)')

print('All icons done.')
