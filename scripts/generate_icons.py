import os
from PIL import Image, ImageDraw

os.makedirs('public/icons', exist_ok=True)

# 1. SVG
svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2563eb" />
      <stop offset="100%" stop-color="#1d4ed8" />
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8" />
      <stop offset="100%" stop-color="#6366f1" />
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="110" fill="url(#bg)" />
  <rect x="96" y="110" width="320" height="292" rx="24" fill="#ffffff" opacity="0.95" />
  <rect x="136" y="150" width="140" height="36" rx="8" fill="url(#accent)" />
  <rect x="136" y="210" width="240" height="16" rx="8" fill="#64748b" />
  <rect x="136" y="240" width="200" height="16" rx="8" fill="#94a3b8" />
  <rect x="136" y="270" width="240" height="16" rx="8" fill="#cbd5e1" />
  <rect x="136" y="310" width="100" height="56" rx="10" fill="#e2e8f0" />
  <rect x="252" y="316" width="124" height="14" rx="7" fill="#64748b" />
  <rect x="252" y="340" width="100" height="14" rx="7" fill="#94a3b8" />
  <circle cx="370" cy="150" r="28" fill="#f59e0b" />
  <polygon points="370,132 374,146 388,150 374,154 370,168 366,154 352,150 366,146" fill="#ffffff" />
</svg>"""

with open('public/icons/icon.svg', 'w', encoding='utf-8') as f:
    f.write(svg_content)

# 2. PNG
def generate_png(size, filename):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    margin = int(size * 0.05)
    radius = int(size * 0.22)
    draw.rounded_rectangle([margin, margin, size - margin, size - margin], radius=radius, fill=(37, 99, 235, 255))
    
    p_x1 = int(size * 0.20)
    p_y1 = int(size * 0.22)
    p_x2 = int(size * 0.80)
    p_y2 = int(size * 0.78)
    draw.rounded_rectangle([p_x1, p_y1, p_x2, p_y2], radius=int(size * 0.05), fill=(255, 255, 255, 245))
    
    b_x1 = int(size * 0.26)
    b_y1 = int(size * 0.29)
    b_x2 = int(size * 0.52)
    b_y2 = int(size * 0.36)
    draw.rounded_rectangle([b_x1, b_y1, b_x2, b_y2], radius=int(size * 0.02), fill=(56, 189, 248, 255))
    
    line_x1 = int(size * 0.26)
    draw.rounded_rectangle([line_x1, int(size * 0.42), int(size * 0.74), int(size * 0.45)], radius=3, fill=(100, 116, 139, 255))
    draw.rounded_rectangle([line_x1, int(size * 0.48), int(size * 0.68), int(size * 0.51)], radius=3, fill=(148, 163, 184, 255))
    draw.rounded_rectangle([line_x1, int(size * 0.54), int(size * 0.74), int(size * 0.57)], radius=3, fill=(203, 213, 225, 255))
    
    draw.rounded_rectangle([line_x1, int(size * 0.62), int(size * 0.44), int(size * 0.73)], radius=4, fill=(226, 232, 240, 255))
    draw.rounded_rectangle([int(size * 0.48), int(size * 0.63), int(size * 0.74), int(size * 0.66)], radius=3, fill=(100, 116, 139, 255))
    draw.rounded_rectangle([int(size * 0.48), int(size * 0.69), int(size * 0.68), int(size * 0.72)], radius=3, fill=(148, 163, 184, 255))
    
    star_cx = int(size * 0.72)
    star_cy = int(size * 0.29)
    star_r = int(size * 0.07)
    draw.ellipse([star_cx - star_r, star_cy - star_r, star_cx + star_r, star_cy + star_r], fill=(245, 158, 11, 255))
    
    img.save(filename, 'PNG')

generate_png(192, 'public/icons/icon-192.png')
generate_png(512, 'public/icons/icon-512.png')
print('Icons generated successfully!')
