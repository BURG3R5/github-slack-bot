class User:
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.link = kwargs.get("link", f"https://github.com/{name}")
