import cv2
import numpy as np
import base64
import io
from PIL import Image

# 1. Read original portrait
img = cv2.imread(r'e:\PORTFOLIO\current_portrait.png', cv2.IMREAD_UNCHANGED)
b, g, r, a = cv2.split(img)

# Morphological cleaning of alpha channel
# Close tiny dark notches and holes inside the hair edge:
k_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
a_closed = cv2.morphologyEx(a, cv2.MORPH_CLOSE, k_close)

# Remove tiny isolated noise islands:
k_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
a_opened = cv2.morphologyEx(a_closed, cv2.MORPH_OPEN, k_open)

# Erode by 1 pixel to trim jagged stair-steps and edge fringes:
k_erode = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
a_eroded = cv2.erode(a_opened, k_erode, iterations=1)

# Gaussian smoothing for smooth antialiased matte transition:
a_smooth = cv2.GaussianBlur(a_eroded, (3, 3), 0.75)

# Re-composite image with cleaned matte
cleaned_img = cv2.merge([b, g, r, a_smooth])

# Convert to WebP Base64 using PIL for maximum quality and compression
pil_img = Image.fromarray(cv2.cvtColor(cleaned_img, cv2.COLOR_BGRA2RGBA))
buf = io.BytesIO()
pil_img.save(buf, format='WEBP', quality=95, method=6)
b64_new = "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode('ascii')

# 2. Update index.html:
with open(r'e:\PORTFOLIO\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace portrait base64 in HTML
p_idx = text.rfind('class="portrait"')
src_start = text.find('src="data:image/webp;base64,', p_idx)
src_end = text.find('"', src_start + 5)
old_src = text[src_start:src_end]
text = text[:src_start] + 'src="' + b64_new + text[src_end:]

# Revert CSS for .portrait to clean original rounded rectangle
old_portrait_css = '''.portrait {
  float: right;
  width: 240px;
  height: 240px;
  aspect-ratio: 1;
  object-fit: cover;
  object-position: center 15%;
  border-radius: 50%;
  margin: 0 0 24px 32px;
  background: linear-gradient(135deg, var(--surface), var(--card-bg));
  border: 3px solid var(--accent);
  box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.15), 0 0 0 6px var(--surface), 0 0 0 7px var(--rule);
  transition: transform .35s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow .35s ease, border-color .35s ease;
}
.portrait:hover {
  transform: scale(1.04);
  box-shadow: 0 16px 36px -4px rgba(0, 0, 0, 0.22), 0 0 0 6px var(--surface), 0 0 0 8px var(--accent);
}
@media (max-width: 768px) {
  .portrait {
    float: none;
    display: block;
    margin: 0 auto 28px auto;
    width: 200px;
    height: 200px;
  }
}'''

clean_portrait_css = '''.portrait {
  float: right;
  width: 220px;
  height: 220px;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 20px;
  margin: 0 0 20px 28px;
  border: 2px solid var(--rule);
  box-shadow: var(--shadow-md);
  transition: transform .3s ease, border-color .3s;
}
.portrait:hover {
  transform: scale(1.02);
  border-color: var(--accent);
}
@media (max-width: 600px) {
  .portrait {
    float: none;
    display: block;
    margin: 0 0 24px 0;
    width: 160px;
    height: 160px;
  }
}'''

assert old_portrait_css in text, "old_portrait_css not found"
text = text.replace(old_portrait_css, clean_portrait_css)

with open(r'e:\PORTFOLIO\index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Matte cleaned & CSS reset to clean original style successfully!")

