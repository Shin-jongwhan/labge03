#!/usr/bin/env python

import os, sys, glob, subprocess, shutil, argparse, requests, json, urllib, pprint, time
from datetime import datetime as Datetime

#########################################################################
#									#
# ReDemulti manual script						#
# 1. python [this_file] ReDemulti [Run_ID] [SampleSheet.csv]		#
# 2. Put [SampleSheet.csv] in /data/Instrument/$Device/$Run_ID/		#
#									#
#########################################################################
sFile_itself = os.path.abspath( __file__ ).split("/")[-1]
print("Usage : python {0} ReDemulti [Run_ID] [SampleSheet.csv]".format(sFile_itself))

parser = argparse.ArgumentParser()

subparser = parser.add_subparsers(help='Desired action to perform', dest='action')

parent_parser = argparse.ArgumentParser(add_help=False)

parser_ReDemulti = subparser.add_parser("ReDemulti", parents=[parent_parser], help='Re Demultiplexing')
parser_ReDemulti.add_argument("RunID", help='Only require one runID which have [Samplesheet.csv]')
parser_ReDemulti.add_argument("SampleSheet", help='which has new demulti sample list')

args = parser.parse_args()

LIMS_TASK_key="2C2CB8ED-6D69-457C-981C-8C7CFC24A3E7"

Machinelist = {'NS500759':'NextSeq01','NS500435':'NextSeq02','NB501509':'NextSeq03','NDX550181':'NextSeqDx','M01849':'MiSeq01','M03183':'MiSeq02','M70503':'MiSeqDx01',}


def SampleInfo(SampleID):
        SampleID = SampleID.replace('-Merged','')

        try :
                RunDir = glob.glob('/Demultiplexing/*/*/'+SampleID+'_*')[-1]
                RunID = RunDir.split('/')[-2]           # find RunID if there is SampleID in the RunID

        except :
                try :
                        RunDir = glob.glob('/Demultiplexing/Analysis/Project/EnfantGuard/*/'+SampleID)[-1]
                        RunID = RunDir.split('/')[-2]

                except :
                        print('can\'t find '+SampleID+' file in Demultiplexing Directory')
                        exit()

        MachineID = RunID.split("_")[1]
        SequencingMachine = Machinelist[MachineID]
        print(SequencingMachine+"\t"+RunID+"\t"+SampleID)
        return SequencingMachine, RunID


def RunFastQC(SampleID):
	SequencingMachine, RunID = SampleInfo(SampleID)

	s = requests.Session()
        headers = {"content-type" : "application/json"}
        data = [{"name":"FastQC","serial":SampleID,"argument":[SequencingMachine,RunID,SampleID,'pe'],"priority":"Immediate"}]
        TaskUrl = "http://lims.labgenomics.com:8080/lims/api/task/?key=%s" % LIMS_TASK_key
        js_data = json.dumps(data)
        s.put(TaskUrl, headers=headers, data=js_data)

        time.sleep(0.5)
        return 0


def SampleList(RunDir, SampleSheet) : 
	# find which SampleID have to be re-analyzed.
	SampleIDList = []
	
	try :
		NewSampleSheet = open(RunDir+'/{0}'.format(SampleSheet))
	except OSError :
		print('can\'t find '+RunDir+'/{0} file'.format(SampleSheet))
		exit()
	else :
		SampleSheetFlag = 0
		SampleIDList = []

		with NewSampleSheet :
			for line in NewSampleSheet :
				if SampleSheetFlag == 1:
					linesp = line.strip().split(',')
					SampleIDList.append(linesp[0])
				if line.startswith('Sample_ID'):
					SampleSheetFlag = 1
	return SampleIDList


def ReDemulti(RunID, SampleSheet):

	# find run path and sequencing machine which were used.
	RunDir = glob.glob('/data/Instrument/*/'+RunID)[0]
        SequencingMachine = glob.glob('/Demultiplexing/*/'+RunID)[0].split('/')[-2]		# find device automatically if there is runid in the device
	TestRunID = "_".join(RunID.split("_")[:2]) + "_redemulti"
	Demulti_run_dir = "/data/Demultiplexing/{0}/{1}".format(SequencingMachine, RunID)
	SampleIDLIst = []
	if os.path.isdir(RunDir) != True :
		print("Please check run directory : {0}".format(RunDir))
		sys.exit()
	else : 
		print("Run directory : {0}".format(RunDir))
	if os.path.isdir(Demulti_run_dir) != True :
		print("Please check demulti directory : {0}".format(Demulti_run_dir))
		sys.exit()
	else : 
		print("Demultiplexing directory : {0}".format(Demulti_run_dir))
		
	if SampleSheet == "SampleSheet.csv" : 
		print("SampleSheet.csv : default")
		
		sRM_RTAComplete_CMD = "rm {0}/RTAComplete.txt".format(RunDir)
		sRename_sampleSheet_CMD = "rename SampleSheet.csv SampleSheet_old.csv {0}/SampleSheet.csv".format(RunDir)
		print(sRM_RTAComplete_CMD)
		os.system(sRM_RTAComplete_CMD)
		time.sleep(1)
		print(sRename_sampleSheet_CMD)
		os.system(sRename_sampleSheet_CMD)
		time.sleep(1)
		
		sMV_Run_dir_CMD_1 = "mv {0} /data/Instrument/".format(RunDir)
		sMV_Run_dir_CMD_2 = "mv /data/Instrument/{0} {1}/".format(RunID, "/".join(RunDir.split("/")[:-1]))
		print("move {0} to /data/Instrument/".format(RunDir))
		os.system(sMV_Run_dir_CMD_1)
		time.sleep(5)
		print("move /data/Instrument/{0} to {1}/".format(RunID, "/".join(RunDir.split("/")[:-1])))
		os.system(sMV_Run_dir_CMD_2)
		time.sleep(5)
			#################################################
		while True :
			if os.path.isfile(RunDir + "/SampleSheet.csv") :
				print("SampleSheet.csv is created")
				break
			else :
				print("Please upload and save {0}/SampleSheet.csv. You can upload SampleSheet.csv on corelims".format(RunDir))
				print("If you upload and save SampleSheet.csv on corelims, then create SampleSheet.csv in {0}".format(RunDir))
				time.sleep(30)		

		SampleIDList = SampleList(RunDir, SampleSheet)
		print("Remove original fastq file in /data/Demultiplexing/{0}/{1}".format(SequencingMachine, RunID))
		for SampleID in SampleIDList :          # remove sample fastq which wrote in SampleSheet.csv
                        for SampleID_fastq in glob.glob('/Demultiplexing/'+SequencingMachine+'/'+RunID+'/'+SampleID+'*') :
                                print("remove fastq {0}".format(SampleID_fastq))
                                os.remove(SampleID_fastq)
		

		#print(Datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
		sDate_time = str(Datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
		print(sDate_time)
		print("create RTAComplete.txt")
		sMake_RTAComplete = "echo {0} > {1}/RTAComplete.txt".format(sDate_time, RunDir)
		os.system(sMake_RTAComplete)
			
	else : 
		print("SampleSheet.csv : {0}".format(SampleSheet))
		os.system("mkdir /Demultiplexing/NextSeqEX/{0}".format(TestRunID))
		input_fastqc = str(raw_input("Do you want to run Fastqc? (type yes or else) : "))
		print(input_fastqc)
		
		while True :
			if os.path.isfile(RunDir + "/" + SampleSheet) :
				print("{0} is created".format(SampleSheet))
				break
			else :
				print("Please create {0} in {1}.".format(SampleSheet, RunDir))
				time.sleep(30)

		SampleIDList = SampleList(RunDir, SampleSheet)
		for SampleID in SampleIDList :
			for SampleID_fastq in glob.glob('/Demultiplexing/'+SequencingMachine+'/'+RunID+'/'+SampleID+'*') :
				print("remove original fastq {0}".format(SampleID_fastq))
				os.remove(SampleID_fastq)
		
		# run demultiplexing script
		BCLtoFastqCMD = '/data/Pipeline/Illumina/bcl2fastq_v2.17-custom/bin/bcl2fastq -R '+RunDir+' -o /Demultiplexing/NextSeqEX/'+TestRunID+ ' -r 12 -d 12 -p 12 -w 1 --minimum-trimmed-read-length 0 --mask-short-adapter-reads 10 --barcode-mismatches 1 --sample-sheet '+RunDir+'/{0}'.format(SampleSheet)
		print(BCLtoFastqCMD)
		a = subprocess.Popen(BCLtoFastqCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

		os.system("python /data/Tools/bin/DemultiStats_cluster_PM.py {0}".format(TestRunID))		# create DemultiStats.txt which has counted cluster, PFcluser, PerfectBarcode for lims DB update in /data/Tools/bin/

		#run fastqc script.
		if input_fastqc == "yes" : 
			for SampleID in SampleIDList :
				for SampleID_fastq in glob.glob('/Demultiplexing/NextSeqEX/'+TestRunID+'/'+SampleID+'*') :
					print("move fastq /Demultiplexing/NextSeqEX/{0}/{1} to {2}".format(TestRunID, SampleID_fastq, Demulti_run_dir))
					sMove_fastq_CMD = "mv {0} {1}/".format(SampleID_fastq, Demulti_run_dir)
					os.system(sMove_fastq_CMD)
			sDate_time_2 = str(Datetime.today().strftime("%Y%m%d_%H%M%S"))
			sRename_Reports_folder_CMD = "rename Reports Reports_{0} /Demultiplexing/NextSeqEX/{1}/Reports".format(sDate_time_2, TestRunID)
			sMove_Reports_folder_CMD = "mv /Demultiplexing/NextSeqEX/{0}/Reports_{1} {2}".format(TestRunID, sDate_time_2, Demulti_run_dir)
			sRename_Stats_folder_CMD = "rename Stats Stats_{0} /Demultiplexing/NextSeqEX/{1}/Stats".format(sDate_time_2, TestRunID)
			sMove_Stats_folder_CMD = "mv /Demultiplexing/NextSeqEX/{0}/Stats_{1} {2}".format(TestRunID, sDate_time_2, Demulti_run_dir)
			print(sRename_Reports_folder_CMD)
			os.system(sRename_Reports_folder_CMD)
			time.sleep(0.5)
			print(sMove_Reports_folder_CMD)
			os.system(sMove_Reports_folder_CMD)
			print(sRename_Stats_folder_CMD)
			os.system(sRename_Stats_folder_CMD)
			time.sleep(0.5)
			print(sMove_Stats_folder_CMD)
			os.system(sMove_Stats_folder_CMD)
			time.sleep(2)
			sRemove_testRunDir_CMD = "rm -rf /Demultiplexing/NextSeqEX/{0}".format(TestRunID)
			print(sRemove_testRunDir_CMD)
			print("Run Fastqc api")
			os.system(sRemove_testRunDir_CMD)
			for SampleID in SampleIDList :
				RunFastQC(SampleID)
	

def main():

	if args.action == 'ReDemulti' :
		RunID = args.RunID
		SampleSheet = args.SampleSheet
		ReDemulti(RunID, SampleSheet)


main()
