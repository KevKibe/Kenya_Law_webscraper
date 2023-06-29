import requests

url = "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
response = requests.get(url)
with open("google-chrome-stable_current_amd64.deb", "wb") as file:
    file.write(response.content)
