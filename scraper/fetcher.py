import requests

def fetch_html(url):
    res = requests.get(url, timeout=10)
    return res.text