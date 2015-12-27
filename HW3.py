import os
import random
import resource
import sys
import time
import collections

#CONSTANT VALUES
min_alloc = 5                 #minimum number of pages allocated to a process by memory

#variable values:
global page_fault_total
resident_set =[]
use_bits=[]
#Variables needed for functions:
size = min_alloc

#______________________GENERIC FUNCTIONS_______________________#

def file_loader():                                                 #creates the file with random page reference values
    file_name = str(sys.argv[1])
    page_ref_array =[]
    if os.path.isfile(file_name):
        f=open(file_name,'r')
        for l in f:
            page_ref_array.append(int(l))
        page_ref_array.pop(0)
    else:
        f = open(file_name,'w')
        num_pages = 10000
        page_ref_array =[]
        f.write(str(num_pages))
        f.write("\n")
        for i in xrange(0,num_pages):
            j= random.randint(1,500)
            f.write(str(j))
            f.write("\n")
            page_ref_array.append(j)
    f.close()
    return page_ref_array

def ReduceResidentSet():
    for k in use_bits:
                    if k==0:
                        loc = use_bits.index(k)
                        #print "reducing memory allocation..."
                        resident_set.pop(loc)
                        use_bits.pop(loc)

def page_fault_frequency(ref_string,F):
    global size
    resident_set =[]
    use_bits = []
    page_fault_total =0
    prev_t =0
    curr_t =0
    for i in xrange(0,len(ref_string)):                 #runs till completion, length of file
        if ref_string[i] not in resident_set:           #if page ref is not in resident set
            if page_fault_total==0:                 #if it is not in resident set and there are no empty cells in the resident set
                prev_t = i+1
                curr_t = prev_t
            else:
                curr_t = i+1
            page_fault_total+=1
            delta_t = curr_t - prev_t               #time interval value
            #print curr_t
            #print prev_t
            #print delta_t
            if(delta_t>=float(1/F)):
                #print "time interval exceeds critical value!!!"
                ReduceResidentSet()
            else:
                resident_set.append(ref_string[i])
                use_bits.append(0)
                for k in xrange(0,len(use_bits)):
                    use_bits[k]=0
            prev_t = curr_t
        else:
            loc = resident_set.index(ref_string[i])
            use_bits[loc] = 1                                  #page referenced, corresponding use bit set to 1
    #print resident_set
    #print use_bits
    return page_fault_total



def vsws(pages,M,L,Q):
    resident_set =[]                                #empty resident set
    working_set = []
    use_bit =[]
    total_fault_count = 0
    counter =0
    samplingStart =0
    for t in xrange(0,len(pages)):
        counter +=1
        temp_faults = 0
        if pages[t] not in working_set:
            working_set.append(pages[t])
        for i in xrange(len(use_bit)):                  #reset all use bits at beginning of interval
            if use_bit[i] == 1:
                use_bit[i] = 0
        if pages[t] in resident_set:                #if page is in memory,
            loc = resident_set.index(pages[t])
            use_bit[loc] = 1

        elif pages[t] not in resident_set:

                resident_set.append(pages[t])
                use_bit.append(1)
                total_fault_count+=1

        if(t-samplingStart <L):

                temp_faults+=1
                if (temp_faults>=Q):

                    if(counter>=M):

                        for k in use_bit:
                            if k ==0:                       #if pages in resident set are not referenced
                                loc = use_bit.index(k)      #remove those pages from the resident set
                                resident_set.pop(loc)
                                use_bit.pop(loc)
                    temp_faults =0
                    working_set=[]
                    samplingStart=t+1
        else:
                for k in use_bit:
                    if k ==0:                       #if pages in resident set are not referenced
                        loc = use_bit.index(0)      #remove those pages from the resident set
                        resident_set.pop(loc)
                        use_bit.pop(loc)
                temp_faults=0
                working_set=[]
                samplingStart =t+1
    print "page faults: ",total_fault_count
    return 0


##__________________MAIN()____________________________##

print "10000 page accesses to "
pages = file_loader()
##_________________ PAGE FAULT FREQUENCY_______________________##
#print "PAGE FAULT FREQUENCY:\n"
F_Values= [1,0.95,0.8,0.75,0.65,0.50,0.4,0.30,0.25,0.1,0.025,0.01]
#for i in xrange(0,len(F_Values)):
    #print ("F = ",F_Values[i])
    #print page_fault_frequency(pages,F_Values[i])

#It is seen that the number of page faults is highest at 1 and
# dips down as the value of F decreases until it stabilizes at a value, indicating that increasing the memory allocation
# beyond this point has little effect on performance.

##__________________VSWS ALGORITHM_____________________________##
print "Variable interval Sample Working Set "
#pages =[2,3,2,1,5,4,5,2,3,2,2,5,4,2,3,2]
M=10
L=50
Q=3
Values =[1,20,50,100,150,200,1000]
for i in Values:
    print "Analyzing M:"
    print "M = ",i
    vsws(pages,i,i*2,Q)
for i in Values:
    print "Analyzing L:"
    print "L = ",i
    vsws(pages,i/2,i,Q)

for i in Values:

    print "Analyzing Q:"
    print "Q = ",i
    vsws(pages,M,L,i)


#We see that as th value of M and L is increased, the number of page faults decreases.
#The change is not pronounced in case of variations to Q