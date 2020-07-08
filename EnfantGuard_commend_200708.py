import os

# ex)
# python	/data/Tools/bin/EnfantGuard	200214_NDX550181_0098_AH7KVCBGXF	2020021200455-EF3-LT-LR	10	50	1	1	1	1	0	NextSeqDx

def main() : 
	# input commend_line txt file
	f = open("/home/shinejh0528/EnfantGuard_commend_line_manual.txt", 'r')
	while True : 
		i = f.readline().strip()
		if i != "" : 
			i = " ".join(i.split("\t"))
			os.system(i)
		else : break


main()
