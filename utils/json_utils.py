class JSON:
    """Wrapper for a `dict`.
    Safely extracts values using multiple keys."""

    def __contains__(self, key) -> bool:
        return key in self.data

    def __init__(self, json) -> None:
        self.data = json

    def __getitem__(self, keys):
        def get(k):
            if isinstance(self.data[k], dict):
                return JSON(self.data[k])
            return self.data[k]

        # Single key
        if isinstance(keys, str):
            key = keys
            if key in self.data:
                return get(key)
            return key.upper()
        # Multiple keys
        for key in keys:
            if key in self.data:
                return get(key)
        else:
            return keys[0].upper()
