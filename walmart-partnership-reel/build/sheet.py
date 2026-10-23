import sys, glob
from PIL import Image
d = sys.argv[1]
fs = sorted(glob.glob(d + '/f_*.png')); ims = [Image.open(f).resize((270, 480)) for f in fs]
cols = 8; rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (270 * cols, 480 * rows), 'white')
for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 270, (i // cols) * 480))
sheet.save(d + '/sheet.png')
