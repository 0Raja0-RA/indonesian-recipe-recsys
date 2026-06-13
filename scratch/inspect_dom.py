import urllib.request
import re

try:
    html = urllib.request.urlopen("http://localhost:8501").read().decode("utf-8")
    testids = set(re.findall(r'data-testid="([^"]+)"', html))
    print("Found testids:", sorted(list(testids)))
except Exception as e:
    print("Error:", e)
