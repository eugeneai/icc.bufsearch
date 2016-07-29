
#!/usr/bin/env python3
import os
import binascii as ba
import icc.bufsearch as bs
import logging
logging.basicConfig(filename='recovery.log',level=logging.INFO)
logging.info('Start logging the result!')

EXCEPT=(
        ".vault",
        ".exe",
        ".doc",
        ".xls",
        ".dll",
        # ".vault",
        # ".vault",
        # ".vault",
        )

DEV="/dev/sda2"
TIMES=10

PATTERNS=["d0cf11e0a1b11ae1",]



PREFIXES=[ba.unhexlify(pt) for pt in PATTERNS]

HEADER=b"Multielemental analysis of rocks with high calcium content by X-ray fluorescence spectrometry for environmental"

def ucslike(b):
    nb=[]
    for i in b:
        nb.append(i)
        nb.append(0)
    return bytes(nb)

HEADER2=ucslike(HEADER)
PATTERN=[b"magnetite",b"enriched"]
PATTERN2=[ucslike(p) for p in PATTERN]

PREFIXES.append(HEADER)
PREFIXES.append(HEADER2)

HEADERS=[HEADER,HEADER2]


headers=[bs.Raita(p) for p in HEADERS]

PATTERNS = [PREFIXES[0]]+PATTERN+PATTERN2
prefs=[bs.Raita(p) for p in PATTERNS]

def scan_reader(file, start_blk, blk_size, blocks, count=None):
    file.seek(start_blk*blk_size)
    queue=[]
    num=start_blk
    while True:
        if count == 0:
            break
        if len(queue)==0:
            buffer=file.read(blk_size*blocks)
            cnt=len(buffer)
            if cnt==0:
                break
            cblk=int(cnt//blk_size)
            for c in range(cblk):
                queue.append(buffer[c*blk_size:(c+1)*blk_size])
        else:
            yield num, queue.pop(0)
            num+=1
            if count !=None:
                count-=1

def scan_hdd(dev):
    # blk_size=16384 # default block size
    blk_size=512*64 # 4096 # default block size
    input = open(dev, "rb")
    input.seek(0, os.SEEK_END)
    size=input.tell()
    print (size)
    blocks = size / blk_size
    print ("Total blocks: ", size)
    blocks = int(blocks)
    print ("Total blocks: ", blocks)
    msteps=1
    step=0

    start_blk=700000

    for num, block in scan_reader(input, start_blk=start_blk, blk_size=blk_size, blocks=10, count=None):
        if step % msteps == 0:
            print ("Block {} of {} = {:.5%}.".format(num, blocks, num/blocks),
                   end="\r")
            step = msteps-1

        for e in headers:
            rc, reason=e.search(block, count=1)
            if rc:
                # print ("\n>> Found HEADER at {} block {}".format(num*blk_size, num))
                # print ("Header at: {}", rc[0])
                prrcs=[p.search(block, count=1)[0] for p in prefs]
                # if not None in prrcs:
                if 1:
                    print ("\n>> Found at {} block {}".format(num*blk_size, num))
                    #print ("#"+':'.join(hex(x) for x in block[:10]).replace("0x",""))
                    print ("Header at: {}", rc[0])
                    print ("Prefixes at: {}", prrcs)
                    logging.info("# {}:{};".format(num*blk_size, num) + str([rc]+[":"]+prrcs))

        step-=1
    print("End")
    logging.info("End recovery scan.")


def undel_ntfs():
    START_FROM="f_003e50" # inode 158054

    i=open("undelete-sda2.list")
    i.readline()
    i.readline()

    proceed=True

    for l in i:
        l=l.strip()
        if not proceed:
            if not l.endswith(START_FROM):
                continue
            else:
                proceed=True
        stop=False
        for E in EXCEPT:
            if l.endswith(E):
                stop=True
                break
        if stop:
            continue
        try:
            inode,flags,percent,date,time,size,name=l.split(maxsplit=6)
        except ValueError:
            print ("Unpack:",l)
            continue
        print (l)
        ind=False
        if name=="<none>":
            name="inode_"+inode
            ind=True
        if flags.startswith('F'):
            if ind:
                rc=os.system("ntfsundelete -u -i %s-%s -o '%s' %s" % (inode,inode,name,DEV))
            else:
                rc=os.system("ntfsundelete -u -m '%s' -o '%s' %s" % (name,name,DEV))
        else:
            print ('skip dir %s' % name)
            continue
        if rc!=0:
            continue
        f=open(name,'rb')
        cb=f.read(1024)
        for pri, pr in enumerate(PREFIXES):
            if cb.startswith(pr):
                os.system("mv '%s' '%s-%s'" % (name,PATTERNS[pri],name))
                print ("!!!")
                break
        else:
            os.system("rm -f '%s'" % name)

        # TIMES-=1
        # if TIMES==0:
        #   break

if __name__=="__main__":
    scan_hdd("/dev/sdd")
    quit()
