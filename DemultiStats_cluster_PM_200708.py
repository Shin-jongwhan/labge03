#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys, glob
import os

#########################################################################################################
#													#
# This script create txt file which have sample, index, clusters, PFclusters, PerfectBarcode (PM)	#
# 1. create demulti folder in /data/Demultiplexing/NextSeqEX/						#
# $ python [this_file] run_folder									#
# This script will create /data/Tools/bin/[Run_dir] + '_Stats_cluster_PM_data.txt'			#
#													#
#########################################################################################################

sFile_itself = os.path.abspath( __file__ ).split("/")[-1]
sFile_dir = "/".join( os.path.abspath( __file__ ).split("/")[:-1] )
print("Usage : python {0} [run_folder]".format(sFile_itself))

Analysis_dir = "/data/Demultiplexing/NextSeqEX/"
print("Analysis_dir : {0}".format(Analysis_dir))
Run_dir = sys.argv[1]
print("output : {0}/{1}_Stats_cluster_PM_data.txt".format(sFile_dir, Run_dir))

sample_dict = {}
dicSample_cluster = {}
indexs = 0 
fastq_file = file(Analysis_dir + Run_dir + "/Stats/DemultiplexingStats.xml")

boolBarcode = False
for fdata in fastq_file:
	Fdata = fdata.strip()
	if Fdata.split('=')[0] == '<Sample name':
		sample_name = Fdata.split('=')[1][1:-2]
		if sample_name[0:2] == 'Un' : pass
		else:
			sample_dict.setdefault(sample_name, 0)
			dicSample_cluster.setdefault(sample_name, 0)
			indexs = 1
	elif len(Fdata.split('PerfectBarcodeCount')) > 1 : 
		if indexs >= 5 or indexs == 0 : pass
		else:
			sample_dict[sample_name] += int(Fdata.split('PerfectBarcodeCount>')[1].split('</')[0])
			#dicSample_cluster[sample_name] = += int(Fdata.split('BarcodeCount>')[1].split('</')[0])
			indexs += 1
	elif len(Fdata.split("<BarcodeCount>")) > 1 : 
		#print(Fdata)
		if indexs >= 5 or indexs == 0 : pass
		else : 
			#print(Fdata)
			dicSample_cluster[sample_name] += int(Fdata.split('<BarcodeCount>')[1].split('</')[0])
	

def PFclusterCount() :
    Run_dir = sys.argv[1]
    #print(os.listdir(Analysis_dir + Run_dir + "/Reports/html"))
    lsReport_dir_list = os.listdir(Analysis_dir + Run_dir + "/Reports/html")
    sLaneBarcode_dir = ""
    for i in range(0, len(lsReport_dir_list)) :
        if os.path.isdir(Analysis_dir + Run_dir + "/Reports/html/" + lsReport_dir_list[i]) == True :
            if os.path.isdir(Analysis_dir + Run_dir + "/Reports/html/" + lsReport_dir_list[i] + "/default/all/all") == True :
                sLaneBarcode_dir = Analysis_dir + Run_dir + "/Reports/html/" + lsReport_dir_list[i] + "/default/all/all/"

    fLaneBarcode = open(sLaneBarcode_dir + "laneBarcode.html", 'r')
    dicLaneBarcode = {}
    dicSampleIndex = {}
    while True :
        i = fLaneBarcode.readline().strip()
        if "</html>" != i :
            if "<td>1</td>" == i :
                sSample = fLaneBarcode.readline().split("<td>")[1].split("</td")[0]
                sIndex = fLaneBarcode.readline()
		if len(sIndex.split("<td>")) > 1 : 
			sIndex = sIndex.split("<td>")[1].split("</td")[0]
                nPFcluster = int(fLaneBarcode.readline().split("<td>")[1].split("</td")[0].replace(",", ""))
                dicLaneBarcode[sSample] = nPFcluster
		dicSampleIndex[sSample] = sIndex
                continue
            if "<td>2</td>" == i or "<td>3</td>" == i or "<td>4</td>" == i :
                sSample = fLaneBarcode.readline().split("<td>")[1].split("</td")[0]
                fLaneBarcode.readline()     # del index line
                nPFcluster = int(fLaneBarcode.readline().split("<td>")[1].split("</td")[0].replace(",", ""))
                dicLaneBarcode[sSample] += nPFcluster
        else :
            break

    lsKey_laneBarcode = list(dicLaneBarcode.keys())
    #for i in lsKey_laneBarcode :
    #   print(i, dicLaneBarcode[i])

    fLaneBarcode.close()
    return dicLaneBarcode, dicSampleIndex


out_file = file(sFile_dir + "/" + Run_dir + '_Stats_cluster_PM_data.txt', 'w')
out_file.write("sample\tIndex\tBarcodeCount(cluster)\tPFcluster\tPerfectBarcodeCount(PM)\n")
dicPFcluster = {}
dicSampleIndex = {}
dicPFcluster, dicSampleIndex = PFclusterCount()
#lsSample_id = list(dicPFcluster.keys())
#print(lsSample_id)
#print(list(sample_dict.keys()))

print("")
print("sample\tIndex\tBarcodeCount(cluster)\tPFcluster\tPerfectBarcodeCount(PM)")
for sample_key in sample_dict.keys():
    if sample_key == "all" :
        continue
    print(sample_key + '\t' + dicSampleIndex[sample_key] + "\t" + str(int(dicSample_cluster[sample_key])) + "\t" + str(int(dicPFcluster[sample_key])) + "\t" + str(int(sample_dict[sample_key])))
    out_file.write(sample_key + '\t' + dicSampleIndex[sample_key] + "\t" + str(int(dicSample_cluster[sample_key])) + "\t" + str(int(dicPFcluster[sample_key])) + "\t" + str(int(sample_dict[sample_key])) + '\n')

print("")
print("")
