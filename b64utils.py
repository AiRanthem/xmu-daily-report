import base64
import sys

s = sys.stdin.read()
e = base64.b64encode(s.encode("utf8"))
print(e.decode("utf8"))
