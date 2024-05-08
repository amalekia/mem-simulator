import sys

class TLB:
    def __init__(self):
        #list of entries that hold most recently accesses page numbers with their corresponding frame numbers
        self.entries = {}   #dictionary that holds the page number and the frame number
        self.size = 16

class PageTable:
    def __init__(self):
        #dictionary that holds the page number and the frame number
        self.pages = {}     #dictionary that holds the page number and the frame number
        self.size = 8      
        self.pageSize = 256    # 256 bytes per page

class PhysicalMemory:
    def __init__(self, frames):
        #memory which frames map to
        self.frames = {}    #dictionary that holds the frame number and the data
        self.numframes = frames
    
pagesAcessed = []   #list of pages accessed

def FIFO():
    #implement FIFO page replacement algorithm
    pass

def LRU():
    #implement LRU page replacement algorithm
    pass

def OPT():
    #implement LFU page replacement algorithm
    pass

#default page replacement alg
str pageRepAlg = "FIFO"

#instance of the classes
TLB tlb
PageTable pageTable
PhysicalMemory physMem

#page faults counter and tlb hit/miss counter
int pageFaults = 0
int tlbHits = 0
int tlbMisses = 0

#function to simulate memory
def memSim():
    #read in the file
    with open("addresses.txt", "r") as f:
        for line in f:
            #parse the address
            addr = int(line, 16)
            page = (addr & 0xFF00) >> 8
            offset = addr & 0xFF
            frame = -1

            #appends page to the list of pages accessed
            pagesAcessed.append(page)

            #check the TLB
            if tlb.entries.get(page) != None:
                tlbHits += 1
                frame = tlb.entries.get(page)
            else:
                tlbMisses += 1
                #check the page table
                if pageTable.pages.get(page) != None:
                    frame = pageTable.pages.get(page)
                else:
                    #page fault
                    pageFaults += 1
                    #implement page replacement algorithm
                    if pageRepAlg == "LRU":
                        frame = LRU()
                    elif pageRepAlg == "OPT":
                        frame = OPT()
                    else:
                        frame = FIFO()

                    #update the page table
                    pageTable.pages[page] = frame

                #update the TLB
                tlb.entries[page] = frame

            #get the data from the physical memory
            data = physMem.frames.get(frame * 256 + offset)
            print(data)

if __name__ == '__main__':
    for i in range(len(sys.argv)):
        if i == 0:
            pageTable = PhysicalMemory(int(arg))
        if i == 1:
            if arg == "FIFO" or arg == "LRU" or arg == "OPT":
                pageRepAlg = arg
            else:
                print("Invalid page replacement algorithm")
                sys.exit(1)
    memSim()
