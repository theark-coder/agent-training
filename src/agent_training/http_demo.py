import urllib.request
response = urllib.request.urlopen("https://example.com")
print(response.status)
body = response.read().decode()
print(body[:100])