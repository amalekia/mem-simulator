import sys

PAGE_AND_FRAME_SIZE = 256

class TLB:
    def __init__(self):
        self.size = 16
        self.entries = {}

    def add_entry(self, page_number, frame_number):
        if len(self.entries) == self.size:
            self.entries.popitem(last=False)  # Remove the oldest entry
        self.entries[page_number] = frame_number

    def lookup(self, page_number):
        return self.entries.get(page_number, None)

class PageTable:
    def __init__(self):
        self.size = 2**8
        self.entries = {i: {'frame_number': None, 'loaded_bit': False} for i in range(self.size)}
    
    def add_entry(self, page_number, frame_number):
        self.entries[page_number]['frame_number'] = frame_number
        self.entries[page_number]['loaded_bit'] = True
    
    def lookup(self, page_number):
        return self.entries[page_number]['frame_number']

class PhysicalMemory:
    def __init__(self, num_frames):
        self.num_frames = num_frames
        self.frames = [None] * num_frames

    def load_page(self, frame_number, data):
        self.frames[frame_number] = data

    def read_frame(self, frame_number):
        return self.frames[frame_number]

def FIFO():
    # implement FIFO page replacement algorithm
    oldest_page = pagesAcessed[0]  # get the oldest page accessed
    frame = pageTable.pages.get(oldest_page)  # get the frame number of the oldest page from the page table
    del pageTable.pages[oldest_page]  # remove the oldest page from the page table
    return frame

def LRU():
    # implement LRU page replacement algorithm
    oldest_page = pagesAcessed.pop(0)  # get the least recently used page accessed
    frame = pageTable.pages.get(oldest_page)  # get the frame number of the oldest page from the page table
    del pageTable.pages[oldest_page]  # remove the oldest page from the page table
    return frame

def OPT():
    #implement LFU page replacement algorithm
    pass

#list of pages accessed
pagesAcessed = []

#default page replacement alg
pageRepAlg = "FIFO"

#instance of the classes
tlb = TLB()
pageTable = PageTable(2**8)
physMem = PhysicalMemory(256)

#page faults counter and tlb hit/miss counter
pageFaults = 0
tlbHits = 0
tlbMisses = 0

#function to simulate memory
def memSim():
    #read in the file
    with open("addresses.txt", "r") as f:
        for line in f:
            #parse the address from integer to binary
            addr = int(line)
            addr = bin(addr)[2:].zfill(16)
            page = (addr & 0xFF00) >> 8
            offset = addr & 0xFF
            frame = -1

            #appends page to the list of pages accessed
            pagesAcessed.append(page)

            #check the TLB
            if tlb.lookup(page) != None:
                tlbHits += 1
                frame = tlb.entries.get(page)
            else:
                tlbMisses += 1
                #check the page table
                if pageTable.pages[page]["loaded_bit"] != False:
                    frame = pageTable.pages[page]["frame_number"]
                else:
                    #page fault
                    pageFaults += 1
                    #implement page replacement algorithm
                    if pageRepAlg == "LRU":
                        frame = LRU(page)
                    elif pageRepAlg == "OPT":
                        frame = OPT(page)
                    else:
                        frame = FIFO(page)

                    #update the page table
                    pageTable.add_entry(page, frame)

                #update the TLB
                tlb.entries.add_entry(page, frame)
            
            physicalAddress = frame * 256 + offset
            frameContent = physMem.read_frame(frame)

            #get the data from the physical memory
            data = physMem.frames.get(frame * 256 + offset)
            print(addr, ", ", data, ", ", frame, ", " , frameContent, "\n")

if __name__ == '__main__':
    for i in range(len(sys.argv)):
        if i == 0:
            pageTable = PhysicalMemory(int(arg))
        if i == 1:
            arg = sys.argv[i]
            if arg == "FIFO" or arg == "LRU" or arg == "OPT":
                pageRepAlg = arg
            else:
                print("Invalid page replacement algorithm")
                sys.exit(1)
    
    memSim()
