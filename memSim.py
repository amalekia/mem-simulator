import sys
from collections import OrderedDict
import binascii

PAGE_AND_FRAME_SIZE = 256

class TLB:
    def __init__(self):
        self.size = 16
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
            self.frames[frame] = binascii.hexlify(f.read(PAGE_AND_FRAME_SIZE)).upper()
    
    def get_value(self, page, offset):
        with open("BACKING_STORE.bin", mode="rb") as f:
            f.seek(page * PAGE_AND_FRAME_SIZE + offset)  # move to the specific offset in the page
            data = binascii.hexlify(f.read(1))  # Read a single byte of data
            return data
        
class MemoryManager:
    def __init__(self):
        self.page_faults = 0.0
        self.tlb_hits = 0.0
        self.tlb_misses = 0.0
        self.pagesAcessed = []
        self.addrList = []

def FIFO(memManager, physMem):
    if len(memManager.pagesAcessed) <= physMem.num_frames:
        return len(memManager.pagesAcessed) - 1
    else:
        oldest_page = memManager.pagesAcessed.pop(0)  # pop the oldest page accessed from the list
        frame = pageTable.entries.get(oldest_page)['frame_number']  # get the frame number of the oldest page from the page table
        pageTable.entries[oldest_page]["loaded_bit"] = False  # remove the frame associated and set it to false
        return frame

def LRU(memManager):
    # find the least recently used page from the pages accessed list
    if len(memManager.pagesAcessed) <= physMem.num_frames:
        return len(memManager.pagesAcessed) - 1
    else:
        queue = []
        least_recent_page = memManager.pagesAcessed[0]
        i = len(memManager.pagesAcessed) - 2
        while len(queue) < len(memManager.pagesAcessed) - 1 and i > 0:
            print("Queue: " + str(queue))
            print("Page " + str(memManager.pagesAcessed[i]))
            if memManager.pagesAcessed[i] in queue:
                queue.remove(memManager.pagesAcessed[i])
            queue.append(memManager.pagesAcessed[i])
            i -= 1
        for page in queue:
            if page not in memManager.pagesAcessed:
                least_recent_page = page
                break
        print(least_recent_page)
        frame = pageTable.entries.get(least_recent_page)['frame_number']  # get the frame number of the least recently used page from the page table
        pageTable.entries[least_recent_page]["loaded_bit"] = False  # remove the frame associated and set it to false
        return frame

def OPT(memManager):
    #find the predicted least used page from the pages to be accessed list
    if len(memManager.pagesAcessed) <= physMem.num_frames:
        return len(memManager.pagesAcessed) - 1
    else:
        queue = []
        least_recent_page = memManager.pagesAcessed[0]
        i = len(memManager.pagesAcessed)
        while len(queue) < len(memManager.pagesAcessed) - len(memManager.addrList) - 1 and i < len(memManager.addrList) - 1:
            if memManager.pagesAcessed[i] in queue:
                queue.remove(memManager.pagesAcessed[i])
            queue.append(memManager.pagesAcessed[i])
            i += 1
        for page in queue:
            if page not in memManager.pagesAcessed:
                least_recent_page = page
                break
        frame = pageTable.entries.get(least_recent_page)['frame_number']  # get the frame number of the least recently used page from the page table
        pageTable.entries[least_recent_page]["loaded_bit"] = False  # remove the frame associated and set it to false
        return frame

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
                    frame = LRU(memManager)
                elif pageRepAlg == "OPT":
                    frame = OPT(memManager)
                else:
                    frame = FIFO(memManager, physMem)

                physMem.load_from_backing_store(page, frame)
                #update the page table
                pageTable.add_entry(page, frame)

            #update the TLB
            tlb.add_entry(page, frame)
        
        frameContent = physMem.read_frame(frame)

        #get the data from the physical memory
        value = physMem.get_value(page, offset)
        print(int(value, 16))
        print('' + str(decim_addr) + ', ' 
              + str(int(value, 16)) + ', '
              + str(frame) + ', '
              + str(frameContent))
    
    #print the statistics
    print('Number of Translated Addresses: ' + str(len(memManager.addrList)))
    print('Page Faults: ' + str(memManager.page_faults))
    print('Page Fault Rate: ' + str(memManager.page_faults/len(memManager.addrList)))
    print('TLB Hits: ' + str(memManager.tlb_hits))
    print('TLB Misses: ' + str(memManager.tlb_misses))
    print('TLB Hit Rate: ' + str((round(memManager.tlb_hits/len(memManager.addrList), 8))))

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

    with open("addresses.txt", "r") as f:
        for line in f:
            #parse the address from integer to binary
            memManager.addrList.append(int(line))

    memSim(tlb, pageTable, physMem, memManager)
