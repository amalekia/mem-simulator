import sys
from collections import OrderedDict

PAGE_AND_FRAME_SIZE = 256

class TLB:
    def __init__(self):
        self.size = 5
        self.entries = OrderedDict()

    def add_entry(self, page_number, frame_number):
        # Check if there is another key with the same frame number
        for key, value in self.entries.items():
            if value == frame_number:
                del self.entries[key]  # Remove the key with the same frame number
                break

        if len(self.entries) == self.size:
            self.entries.popitem(last=False)  # Remove the oldest entry
        self.entries[page_number] = frame_number

    def lookup(self, page_number):
        return self.entries.get(page_number, None)

class PageTable:
    def __init__(self):
        self.size = 256
        self.entries = {i: {'frame_number': None, 'loaded_bit': False} for i in range(self.size)}
    
    def add_entry(self, page_number, frame_number):
        self.entries[page_number]['frame_number'] = frame_number
        self.entries[page_number]['loaded_bit'] = True

class PhysicalMemory:
    def __init__(self, num_frames, page_repl_alg):
        self.page_repl_alg = page_repl_alg
        self.num_frames = num_frames
        self.frames = [None] * num_frames

    def load_page(self, frame_number, data):
        self.frames[frame_number] = data

    def read_frame(self, frame_number):
        return self.frames[frame_number]

    def load_from_backing_store(self, page, frame):
        with open("BACKING_STORE.bin", mode="rb") as f:
            f.seek(page*256)  #move to page in backing store
            data = f.read(PAGE_AND_FRAME_SIZE)  # Read frame size amount of data
            self.frames[frame] = data
        
class MemoryManager:
    def __init__(self):
        self.page_faults = 0
        self.tlb_hits = 0
        self.tlb_misses = 0
        self.pagesAcessed = []
        self.addrList = []

def FIFO(memManager, physMem, page):
    if len(memManager.pagesAcessed) <= physMem.num_frames:
        return len(memManager.pagesAcessed) - 1
    else:
        oldest_page = memManager.pagesAcessed.pop(0)  # pop the oldest page accessed from the list
        frame = pageTable.entries.get(oldest_page)['frame_number']  # get the frame number of the oldest page from the page table
        pageTable.entries[oldest_page]["loaded_bit"] = False  # remove the frame associated and set it to false
        return frame

def LRU(memManager, page):
    # find the least recently used page from the pages accessed list
    least_recent_page = memManager.pagesAcessed[0]
    for p in memManager.pagesAcessed:
        if memManager.pagesAcessed.index(p) < memManager.pagesAcessed.index(least_recent_page):
            least_recent_page = p
    frame = pageTable.entries.get(least_recent_page)['frame_number']  # get the frame number of the least recently used page from the page table
    pageTable.entries[least_recent_page]["loaded_bit"] = False  # remove the frame associated and set it to false
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
                    frame = LRU(memManager, physMem, page)
                elif pageRepAlg == "OPT":
                    frame = OPT(memManager, physMem, page)
                else:
                    frame = FIFO(memManager, physMem, page)

                physMem.load_from_backing_store(page, frame)
                #update the page table
                pageTable.add_entry(page, frame)

            #update the TLB
            tlb.add_entry(page, frame)
        
        # physicalAddress = frame * 256 + offset
        frameContent = physMem.read_frame(frame)

        #get the data from the physical memory
        # data = physMem.frames.get(frame * 256 + offset)
        data= 0
        print(decim_addr, data, frame, frameContent)
    
    print('Page Faults: ' + str(memManager.page_faults))
    print('Page Fault Rate: ' + str(memManager.page_faults/len(memManager.addrList)))
    print('TLB Hits: ' + str(memManager.tlb_hits))
    print('TLB Misses: ' + str(memManager.tlb_misses))
    print('TLB Hit Rate: ' + str(memManager.tlb_hits/len(memManager.addrList)))

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
    physMem = PhysicalMemory(num_frames, pageRepAlg)
    memManager = MemoryManager()

    if num_frames == 0:
        print("Invalid number of frames")
        sys.exit(1)

    with open("addressestest.txt", "r") as f:
        for line in f:
            #parse the address from integer to binary
            memManager.addrList.append(int(line))

    memSim(tlb, pageTable, physMem, memManager)
