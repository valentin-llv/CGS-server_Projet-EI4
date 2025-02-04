import base64
from PIL import Image
from io import BytesIO
colorNames = ['None', 'Purple', 'White', 'Blue', 'Yellow', 'Orange', 'Black', 'Red', 'Green', 'Multicolor']

width = 100
src = []

# convert maps images to base64 data and write it in maps_images.js
for i, file in enumerate(colorNames[1:]):
	# open the file
	img = Image.open(file + '.jpg')
	# resize it, with rotation
	img = img.resize((width, int(width*img.size[1]/img.size[0]))).rotate(90, expand=True)
	print("Size= %d,%d" % img.size)
	# get its base64 data
	buffered = BytesIO()
	img.save(buffered, format="JPEG", quality=80, optimize=True)
	img.close()
	# get its base64 data and generate JS code
	img64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
	res = ("cards[%d] = \"url('data:image/jpg;base64," % (i+1)) + img64 + "')\";\n"
	src.append(res)

# write the JS code
with open('cards.js', 'w') as f:
	f.write("var cards = [];\n")
	f.write("\n".join(src))
