import sys
import base64
import json
import os.path


if len(sys.argv) < 3:
    print("USAGE: pdfp-extract.py [pdf_path] [output_path]")
    sys.exit()


f = open(sys.argv[1], 'rb')
pdf = f.read()
f.close()

pdfp = {}
pdfp['slide'] = os.path.split(sys.argv[1])[1][:-4]
pdfp['pdf'] = base64.b64encode(pdf).decode('utf-8')

pdfp = json.dumps(pdfp).replace('/', '\\/')
pdfp = "local_pdf( {} )".format(pdfp)

f = open(os.path.join(sys.argv[2], sys.argv[1][:-4] + ".pdfp"), 'w')
f.write(pdfp)
f.close()