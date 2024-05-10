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

class PhysicalMemory:
    def __init__(self, num_frames):
        self.num_frames = num_frames
        self.frames = [None] * num_frames

    def load_page(self, frame_number, data):
        self.frames[frame_number] = data

    def read_frame(self, frame_number):
        return self.frames[frame_number]

class MemoryManager:
    def __init__(self, page_replacement_algorithm):
        self.page_faults = 0
        self.tlb_hits = 0
        self.tlb_misses = 0
        self.pageRepAlg = page_replacement_algorithm
        self.pagesAcessed = []
        self.addrList = []

def FIFO(memManager, page):
    # implement FIFO page replacement algorithm
    oldest_page = memManager.pagesAcessed[0]  # get the oldest page accessed
    frame = pageTable.entries.get(oldest_page)['frame_number']  # get the frame number of the oldest page from the page table
    del pageTable.entries[oldest_page]  # remove the oldest page from the page table
    return frame

def LRU(memManager, page):
    # implement LRU page replacement algorithm
    
    oldest_page = memManager.pagesAcessed.pop(0)  # get the least recently used page accessed
    frame = pageTable.entries.get(oldest_page)  # get the frame number of the oldest page from the page table
    del pageTable.entries[oldest_page]  # remove the oldest page from the page table
    return frame

def OPT(memManager, page):
    #implement LFU page replacement algorithm
    pass

#function to simulate memory
def memSim(tlb, pageTable, physMem, memManager):
    #for each address
    for decim_addr in memManager.addrList:
        #parse the address from integer to binary
        addr = format(decim_addr, '016b')
        page = int(addr[0:8], 2)
        offset = int(addr[8:], 2)
        frame = -1

        print(page)

        #appends page to the list of pages accessed
        memManager.pagesAcessed.append(page)

        #check the TLB
        if tlb.lookup(page) != None:
            memManager.tlb_hits += 1
            frame = tlb.entries.get(page)
        else:
            memManager.tlb_misses += 1
            #check the page table
            if pageTable.entries[page]["loaded_bit"] != False:
                frame = pageTable.entries[page]["frame_number"]
            else:
                #page fault
                memManager.page_faults += 1
                #implement page replacement algorithm
                if pageRepAlg == "LRU":
                    frame = LRU(memManager, page)
                elif pageRepAlg == "OPT":
                    frame = OPT(memManager, page)
                else:
                    frame = FIFO(memManager, page)

                #update the page table
                pageTable.add_entry(page, frame)

            #update the TLB
            tlb.entries.add_entry(page, frame)
        
        physicalAddress = frame * 256 + offset
        frameContent = physMem.read_frame(frame)

        #get the data from the physical memory
        data = physMem.frames.get(frame * 256 + offset)
        print(decim_addr, ", ", data, ", ", frame, ", " , frameContent, "\n")

if __name__ == '__main__':
    num_frames = 0
    #default page replacement algorithm is FIFO
    pageRepAlg = "FIFO"

    for i in range(len(sys.argv)):
        arg = sys.argv[i]
        if i == 1:
            num_frames = int(arg)
        if i == 2:
            arg = sys.argv[i]
            if arg == "FIFO" or arg == "LRU" or arg == "OPT":
                pageRepAlg = arg
            else:
                print("Invalid page replacement algorithm")
                sys.exit(1)
    
    #instance of the classes
    tlb = TLB()
    pageTable = PageTable()
    physMem = PhysicalMemory(num_frames)
    memManager = MemoryManager(pageRepAlg)

    if num_frames == 0:
        print("Invalid number of frames")
        sys.exit(1)

    with open("addresses.txt", "r") as f:
        for line in f:
            #parse the address from integer to binary
            memManager.addrList.append(int(line))

    memSim(tlb, pageTable, physMem, memManager)
