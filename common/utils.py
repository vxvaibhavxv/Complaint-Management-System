def isValidInput(value):
    if value == None:
        return False

    if value.strip() == "":
        return False

    return True

def cleanInput(value):
    return value.strip()