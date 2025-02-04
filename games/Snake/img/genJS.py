# small script to generate the base64 images in JS (from the png)

import base64

def genJS(filename):
	"""Generate the base64 corresponding to the png
	See https://stackoverflow.com/questions/6375942/how-do-you-base-64-encode-a-png-image-for-use-in-a-data-uri-in-a-css-file"""
	return base64.b64encode(open(filename, "rb").read()).decode('utf-8')
	# return filename


src = []

# do it for the head and the tail
for pre in ['head', 'tail']:
	ll = []
	for p in ['red', 'green']:
		l = []
		for d in range(4):
			l.append("\"url('data:image/png;base64,%s')\"" % str(genJS('%s/%s-%d.png' % (p, pre, d))))
		ll.append("[%s]" % ",\n".join(l))
	src.append("let %s = [%s];" % (pre, ",\n".join(ll)))

# and for the body
lll = []
for p in ['red', 'green']:
	ll = []
	for d1 in range(3):
		l = ["\"\""]*(d1+1)
		for d2 in range(d1+1, 4):
			l.append("\"url('data:image/png;base64,%s')\"" % str(genJS('%s/snake-%d-%d.png' % (p, d1, d2))))
			# l.append("'%d-%d'"%(d1,d2))   # test
		ll.append("[%s]" % ",\n".join(l))
	lll.append("[%s]" % ",\n".join(ll))
src.append("let body = [%s];" % (",\n".join(lll)))

with open('../server/templates/game/image-snake.js', 'w') as f:
	f.write("\n".join(src))