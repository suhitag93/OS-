# --------------------CONSTANTS----------------------------------
MAX_BLOCKS      = 10000     # blocks on the file system
MAX_FILE_SIZE   = 1638400   # max file size
BLOCK_SIZE      = 4096      # bytes that a block can hold
DevId           = 20        # file system ID
FREE_STRT       = 1         # starting block of the free list
FREE_END        = 25        # ending block
ROOT            = 26
BLOCKS_IN_FREE  = 400       # max number of pointers possible in a block
#______________________________________________________________

FILES_DIR = "FS"
#______________________________________________________________
import os
import os.path
import time

#system time stored in variable
t   = int(time.time())

#_________________Free Block Functions_________________________
# possible free blocks in file system:

def get_freeblock_list():
    freeBlocks =[]
    for i in range(FREE_STRT,FREE_END+1):
        #open each file
        fuse_file = open(FILES_DIR+'/fusedata.'+str(i),'r+')
        #store contents into variable and remove whitespaces
        data = fuse_file.read().strip()
        data_list = data.split(',')
        print "Block %d entries: %d" %(i,len(data_list))
        for j in data_list:
            freeBlocks.append(int(j))
    return freeBlocks
    #print freeBlocks

def check_freeBlockList():
    FB_list = get_freeblock_list()
    print "number of listed free blocks : %d" %len(FB_list)
    #FB_list =FB_list.sort()
    missingFreeBlocks = []
    for i in range(FB_list[0],MAX_BLOCKS):
        if FB_list.count(i) == 0 :
            missingFreeBlocks.append(i)
            FB_list.append(i)
    FB_list.sort()
    print "Missing blocks: "
    print missingFreeBlocks
    print "Number of listed free blocks: %d" %len(FB_list)
    FreeBlockList = FB_list+missingFreeBlocks
    FreeBlockList.sort()
    print "Complete List by concatenating both lists..."
    print "Number of free blocks: %d" %len(FreeBlockList)
    free_flag = True
    for i in FreeBlockList:
        file_path = FILES_DIR+"/fusedata."+str(i)
        if os.path.isfile(file_path):
            if  not os.stat(file_path).st_size == 0:
                free_flag = False
                print file_path
    if free_flag :
        print "Free Blocks do not contain any files or directories."



#_______________SUPERBLOCK FUNCTIONS___________________________
# check if device ID matches stored value
def check_DevId(supr_list):
    # read super block file into variable
    devId_list = supr_list[2].split(':')
    #print devId_list
    test_devId = devId_list[1]
    #print test_devId
    if (DevId != int(test_devId)):
        print "Device ID did not match expected value."
        exit(1)
    else:
        print "Device ID match."

#check and update, if possible, SuperBlock creation time
def chk_sprBlk_time(t,supr_list):
    tst_ctime_list  = supr_list[0].split(':')
    tst_ctime       = tst_ctime_list[1].strip()
    tst_ctime_nm    = int(tst_ctime)
    if(t < tst_ctime_nm):
        print supr_list
        print "Time in ctime is in the future"
        #supr_list[0]    = supr_list[0].replace(tst_ctime,str(t))
        #print "Time has been updated to current time"
    #print supr_list
    else:
        print "Time of superblock is in the past."

#check data in superblock is correct
def chk_sprBlk_data(t,supr_list):
    tst_list =[]
    for i in range(3,7):
        tst_list.append(supr_list[i].split(':'))
    #print "tst_list:"
    #print tst_list
    err_flag =False
    for j in range(0,4):
        tst_data =tst_list[j][1]
        tst_data_str = tst_data.strip()
        if(j==3):
            tst_data_str = tst_data_str.rstrip('}')

        tst_data_num = int(tst_data_str)

        if (j==0):  #freeStart
            if(tst_data_num != FREE_STRT):
                print "freeStart in the superblock was incorrect and has been corrected"
                supr_list[3] = supr_list[3].replace(tst_data_str,str(FREE_STRT))
                err_flag =True
        if (j==1):  #freeStart
            if(tst_data_num != FREE_END):
                print "freeEnd in the superblock was incorrect and has been corrected"
                supr_list[4] = supr_list[4].replace(tst_data_str,str(FREE_END))
                err_flag =True
        if (j==2):  #root
            if(tst_data_num != ROOT):
                print "root in the superblock was incorrect and has been corrected"
                supr_list[5] = supr_list[5].replace(tst_data_str,str(ROOT))
                err_flag =True
        if (j==3):  #max blocks
            if(tst_data_num !=MAX_BLOCKS):
                print "maxBlocks in the superblock was incorrect and has been corrected"
                supr_list[6] = supr_list[6].replace(tst_data_str,str(MAX_BLOCKS))
                err_flag =True
    if(not err_flag):
        print "Superblock values match expected values."
    #print supr_list

def chk_suprBlk(t):
    superblock_path = FILES_DIR + "/fusedata.0"
    superblock = open(superblock_path, 'r+')
    sB_data = superblock.read()
    supr_list = sB_data.strip().split(',')

    check_DevId(supr_list)
    chk_sprBlk_time(t,supr_list)
    chk_sprBlk_data(t,supr_list)

    content = ','.join(supr_list)
    superblock.close()

#________________Time Entry function____________________________

def check_acm_time(t, f_type, num):
    block_path = FILES_DIR +"/fusedata."+str(num)
    block = open(block_path,'r+')
    data = block.read()
    blk_list = data.strip().split(',')
    if (f_type == 'f'):
        atime_index = 5
        ctime_index = 6
        mtime_index = 7
    else:
        atime_index = 4
        ctime_index = 5
        mtime_index = 6

    #break time into 2 item lists:
    atime_lst = blk_list[atime_index].split(':')
    ctime_lst = blk_list[ctime_index].split(':')
    mtime_lst = blk_list[mtime_index].split(':')

    #for atime:
    tst_atime = atime_lst[1].strip()
    num_atime = int(tst_atime)

    #for ctime:
    tst_ctime = ctime_lst[1].strip()
    num_ctime = int(tst_ctime)

    #for mtime:
    tst_mtime = mtime_lst[1].strip()
    num_mtime = int(tst_mtime)

    flag_chg = False

    if (t < num_atime):
        print "a time in fusedata.%d is a future value." %num
        #print "a time in fusedata.%d has been updated to current time" %num
        #blk_list[atime_index] = blk_list[atime_index].replace(tst_atime,str(t))
        flag_chg = True
    if (t<  num_ctime):
        print "c time in fusedata.%d is a future value." %num
        #print "c time in fusedata.%d has been updated to current time" %num
        #blk_list[ctime_index] = blk_list[ctime_index].replace(tst_ctime,str(t))
        flag_chg = True
    if (t < num_mtime):
        print "m time in fusedata.%d is a future value." %num
        #print "m time in fusedata.%d has been updated to current time" %num
        #blk_list[mtime_index] = blk_list[mtime_index].replace(tst_mtime,str(t))
        flag_chg = True
    #update file contens if any change was made:
    #block.seek(0)
    #block.truncate()
    #block.write(data)
    block.close()


#___________FILE AND DIRECTORY FUNCTIONS________________________

#validate size and location values in inode
def check_file_inode(num):
    block_path = FILES_DIR + "/fusedata." +str(num)
    block = open(block_path,'r+')
    data = block.read().strip()
    file_list = data.split(',')
    print "Block: fusedata.%d"%num
    #print file_list
    #get size
    size_field = file_list[0]
    #print size_field
    size_lst =size_field.split(':')
    #print size_lst
    size = int(size_lst[1].strip()) #convert to str if needed

    #get linkcount
    lc_list = file_list[4].split(':')
    linkcount = int(lc_list[1].strip()) #typecast with str if needed
    #print linkcount

    #get indirect value:
    indirect_loc_list = file_list[8].split(' ')
    indirect_list = indirect_loc_list[1].strip().split(':')
    indirect = (indirect_list[1].strip())
    #print indirect_list
    #print indirect

    #get the location:
    location_data = indirect_loc_list[2]
    location_data = location_data.rstrip('}')
    location_list = location_data.split(':')
    location_block = location_list[1].strip()  #not converted to int
    #print location

    #read contents in fusedata block at location:
    loc_path = FILES_DIR +'/fusedata.' +location_block
    loc_file = open(loc_path,'r+')
    loc_data = loc_file.read()

    test_data = loc_data.strip().split(',')
    test_array = []
    #create array flag:
    arr_flag = True
    for i in test_data:
        i=i.strip()
        #check if location is not an array and indirect value is correct
        if (not i.isdigit()):
            arr_flag =False
            break
        test_array.append(int(i))
        #open block corresponding to location array:
        fobj = open(FILES_DIR+'/fusedata.'+i,'r+')
        print "Contents of file %s pointed to by location value in location block %s:" %(i,location_block)
        print fobj.read()
    err_flag = False

    if (not arr_flag):
        if(indirect ==0):
            if(not (size<BLOCK_SIZE and size >0)):
                print "Error: size of data in file inode in fusedata. %d." %num
                err_flag = True
                file_list[8] = file_list[8].replace(indirect,'0')
                print "File list"
                print file_list
    elif(indirect !=0):
        #set indirect to 1:
        if(not (size <(BLOCK_SIZE*len(test_array)))):
                print "Error: Size of data at fusedata.%d fails conditions." %num
                err_flag =True
        if (not (size > (BLOCK_SIZE*(len(test_array)-1)))):
                print "Error: Size at fusedata.%d is too large." %num
                err_flag = True
        if not err_flag:
            print "The size at fusedata.%d is %d bytes. " %(num, size)

#_____________________DIRECTORY FUNCTIONS_____________________________#


def check_dir(num, parent):
    #read data of fusedata blocks
    block_path = FILES_DIR +"/fusedata."+str(num)
    block = open(block_path,'r+')
    data = block.read()
    if(data.count('{') != 2 and data.count('}') != 2):
        print "Format does not match expected format in fusedata.%d" % num
        return -1
    file_lst = data.strip().split('{')
    count_data = file_lst[2].rsplit('}}')
    count_data = count_data[0].split(',')
    file_lst = file_lst[1].split(',')
    #print file_lst
    #get linkcount
    lc_list = file_lst[7].split(':')
    #print lc_list
    lnk_count = lc_list[1]
    #if data in directory does not match format:
    err_flag =False
    #print data
    #print data
    if (int(lnk_count) != len(count_data)):
        err_flag = True
        print "The link count is incorrect in fusedata.%d"%num
    flag_d = True
    flag_dd = True
    #print count_data
    if (not err_flag):
        for i in range(0,(len(count_data))):
            d = count_data[i].strip().split(':')
            if (d[1]=='.'):

                if(int(d[2]) != num):

                    flag_d =False
                    print "ERROR: block number %d: block number of . directory is incorrect/ missing "%num
            if (d[1]=='..'):
                if(int(d[2])!=parent):
                    flag_d = False
                    print "ERROR: Block number %d block number of .. directory is incorrect/ missing "%num
    if (flag_d and flag_dd) :
        print "There are no errors in . directory or .. directory of block number %d" %num


#____________________________MAIN___________________________

chk_suprBlk(t)          #checks for devID, creation time of superblock and data of superblock.
check_acm_time(t,'d',ROOT)
check_acm_time(t,'d',30)
check_file_inode(27)

check_dir(30, ROOT)
check_dir(ROOT,ROOT)
check_freeBlockList()
