import sys
import base64
import json
import os.path


if len(sys.argv) < 3:
    print("USAGE: pdfp-extract.py [pdfp_path] [output_path]")
    sys.exit()


f = open(sys.argv[1])
pdfp = f.read()
f.close()

pdfp = pdfp.replace("local_pdf(", "").replace(")", "")
pdfp = json.loads(pdfp)

pdf = base64.b64decode(pdfp['pdf'])

f = open(os.path.join(sys.argv[2], pdfp['slide'] + ".pdf"), 'wb')
f.write(pdf)
f.close()