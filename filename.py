import random
import string
import os

def createFilename(ogFilename, hex): 
    filename, ext = os.path.splitext(ogFilename) # Separate filename and its extension 

    if filename == "": # We know that if filename is a empty string it means no file was sent so we return a error
        return Exception()
    
    random.seed(hex) # Use hex as seed to generate filename. This prevents creation of more files with the same contents saving storage space. Collisions are possible although not likely.
    filename = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6)) + (ext or filename) # randomizes filename to 6 characters long and adding its file extention
    return filename