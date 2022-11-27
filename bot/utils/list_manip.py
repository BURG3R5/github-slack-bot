def intersperse(array: list, padding) -> list:
    result = [padding] * (len(array) * 2 - 1)
    result[0::2] = array
    return result
