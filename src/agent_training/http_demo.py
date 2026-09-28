import urllib.request


def fetch_example():
    response = urllib.request.urlopen("https://example.com")
    return response.status


if __name__ == "__main__":
    print(fetch_example())
