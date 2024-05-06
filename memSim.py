
class TLB:
    def __init__(self):
        self.entries = []
        self.size = 16

class PageTable:
    def __init__(self):
        self.entries = []
        self.size = 8
        self.pageSize = 256    # 256 bytes

class PhysicalMemory:
    def __init__(self):
        self.pages = []
        self.size = 32

def memSim(numFrames):
    
    


if __name__ == '__main__':
    numFrames = input("Enter the number of frames: ")
    memSim(numFrames)
