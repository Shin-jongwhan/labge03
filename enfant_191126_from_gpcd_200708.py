#!/usr/bin/env python

import os, sys, glob, subprocess, shutil, argparse, requests, json, urllib, pprint, time

#########################################################################
# Use only ReDemulti for enfantguard					#
# 1. Put 'SampleSheet_enfant.csv' in /data/Instrument/$Device/$Run_ID/	#
# 2. python [this_file] ReDemulti [Run_ID]				#
#########################################################################

parser = argparse.ArgumentParser()

subparser = parser.add_subparsers(help='Desired action to perform', dest='action')

parent_parser = argparse.ArgumentParser(add_help=False)

parser_ReDemulti = subparser.add_parser("ReDemulti", parents=[parent_parser], help='Re Demultiplexing')
parser_ReDemulti.add_argument("RunID", help='Only require one runID which have Samplesheet_gpcd.csv')

parser_MultiAnal = subparser.add_parser("MultiAnal", parents=[parent_parser], help='Multiple Analysis from One Customer')
parser_MultiAnal.add_argument("Input", help='A file with one sample ID per line or simply two Sample ID within \'')

parser_ParsingError = subparser.add_parser("ParsingError", parents=[parent_parser], help='Revise Output File of Sample')
parser_ParsingError.add_argument("Input", help='Just one Sample ID or a file which have one sample ID per line ')

parser_RunFastQC = subparser.add_parser("RunFastQC", parents=[parent_parser], help='Run from FastQC Step')
parser_RunFastQC.add_argument("Input", help='Just one Sample ID or a file which have one sample ID per line ')

parser_RunGPCD = subparser.add_parser("RunGPCD", parents=[parent_parser], help='Run from GPCD Step')
parser_RunGPCD.add_argument("Input", help='Just one Sample ID or a file which have one sample ID per line ')

parser_RmGPCD = subparser.add_parser("RmDenovoFiles", parents=[parent_parser], help='Remove Database Files in gpcd01')
parser_RmGPCD.add_argument("Input", help='Just one Sample ID or a file which have one sample ID per line ')

parser_RmGPCD = subparser.add_parser("ConcatSamples", parents=[parent_parser], help='Remove Database Files in gpcd01')
parser_RmGPCD.add_argument("OldSampleID", help='Only require one sample ID')
parser_RmGPCD.add_argument("NewSampleID", help='Only require one sample ID')

args = parser.parse_args()

LIMS_TASK_key="2C2CB8ED-6D69-457C-981C-8C7CFC24A3E7"

Machinelist = {'NS500759':'NextSeq01','NS500435':'NextSeq02','NB501509':'NextSeq03','NDX550181':'NextSeqDx','M01849':'MiSeq01','M03183':'MiSeq02','M70503':'MiSeqDx01',}


def SampleInfo(SampleID):
	SampleID = SampleID.replace('-Merged','')

	try :
		RunDir = glob.glob('/Demultiplexing/*/*/'+SampleID+'_*')[-1]
		RunID = RunDir.split('/')[-2]		# find RunID if there is SampleID in the RunID

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

def RunGPCD(RunID, SampleID):
	
	SequencingMachine, RunID = SampleInfo(SampleID)

        s = requests.Session()
        headers = {"content-type" : "application/json"}
        data = [{"name":"GPCD","serial":SampleID,"argument":[RunID,SampleID,SequencingMachine],"priority":"Immediate"}]
        TaskUrl = "http://lims.labgenomics.com:8080/lims/api/task/?key=%s" % LIMS_TASK_key
        js_data = json.dumps(data)
        s.put(TaskUrl, headers=headers, data=js_data)
	
	print('Put Run GPCD Task to LIMS '+SequencingMachine+' '+RunID+' '+SampleID)
	time.sleep(0.5)
	return 0
	
def RmDenovoFiles(SampleID):

	RmGPCDCMD = 'ssh denovo01 \'rm -r /data/Analysis/ETC/depth_per_base/GenoPac/GenoPac_'+SampleID+'\''
	a = subprocess.Popen(RmGPCDCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	RmGPCDCMD = 'ssh denovo01 \'rm -r /data/Analysis/ETC/depth_per_base/GenoPac/GenoPac_'+SampleID+'-Merged\''
	a = subprocess.Popen(RmGPCDCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	
	RmGPCDCMD = 'ssh denovo01 \'rm -r /data/Analysis/ETC/GENOPAC/*/'+SampleID+'\''
	a = subprocess.Popen(RmGPCDCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	RmGPCDCMD = 'ssh denovo01 \'rm -r /data/Analysis/ETC/GENOPAC/*/'+SampleID+'-Merged\''
	a = subprocess.Popen(RmGPCDCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	print('Remove Database files from Denovo01 '+SampleID+' and '+SampleID+'-Merged files')
	time.sleep(0.5)
	return 0	

def RmGPCDFiles(SampleID):

	RmGPCDCMD = 'ssh gpcd01 \'rm -r /data/Analysis/ETC/depth_per_base/GenoPac/GenoPac_'+SampleID+'\''
	a = subprocess.Popen(RmGPCDCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	RmGPCDCMD = 'ssh gpcd01 \'rm -r /data/Analysis/ETC/depth_per_base/GenoPac/GenoPac_'+SampleID+'-Merged\''
	a = subprocess.Popen(RmGPCDCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	
	RmGPCDCMD = 'ssh gpcd01 \'rm -r /data/Analysis/ETC/GENOPAC/*/'+SampleID+'\''
	a = subprocess.Popen(RmGPCDCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	RmGPCDCMD = 'ssh gpcd01 \'rm -r /data/Analysis/ETC/GENOPAC/*/'+SampleID+'-Merged\''
	a = subprocess.Popen(RmGPCDCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	print('Remove Database files from GPCD01 '+SampleID+' and '+SampleID+'-Merged files')
	time.sleep(0.5)
	return 0	

def ParsingError(SampleID):
	SequencingMachine, RunID = SampleInfo(SampleID)

	CopyCMD = 'ssh denovo01 \'cp /data/Analysis/ETC/GENOPAC/'+RunID+'/'+SampleID+'/GPC_NGS_1sample.txt /data/Analysis/ETC/GENOPAC/'+RunID+'/'+SampleID+'/GPC_NGS_1sample.txt.orig\''
        a = subprocess.Popen(CopyCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

	ParsingErrorCMD = 'ssh denovo01 \'awk -v OFS=\"\\t\" -F \"\\t\" \'\"\'\"\'FNR==NR{a[NR]=$2;next}{$2=a[FNR]}1\'\"\'\"\' /data/Analysis/ETC/GENOPAC/GPC_NGS_1sample.txt /data/Analysis/ETC/GENOPAC/'+RunID+'/'+SampleID+'/GPC_NGS_1sample.txt.orig > /data/Analysis/ETC/GENOPAC/'+RunID+'/'+SampleID+'/GPC_NGS_1sample.txt\''
	a = subprocess.Popen(ParsingErrorCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

	GPCDReportCMD = 'ssh denovo01 \'cd /data/lims/GPCD && /usr/lib/jvm/jdk1.8.0_20/bin/java -cp \"GPCD.jar:gpcd-rmi-1.0.jar:lims-shared-Qbey.jar:/data/lims/Client/lims-client-Kyoko-jar-with-dependencies.jar\" com.labgenomics.gpcd.daemon.GPCD labge02-e 20020 GPCDReportService '+RunID+' '+SampleID+'\''
        a = subprocess.Popen(GPCDReportCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

	return 0

def ConcatSamples(OldSampleID, NewSampleID):

	NewSampleDir = glob.glob('/Demultiplexing/Analysis/Project/GPCD/*/'+NewSampleID)[0]
	CopyCMD = 'cp -r '+NewSampleDir+' '+NewSampleDir+'.original'
        a = subprocess.Popen(CopyCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

	OldSampleFastq_1 = '/Demultiplexing/Analysis/Project/GPCD/*/'+OldSampleID+'/'+OldSampleID+'_1.fastq.gz'
	OldSampleFastq_2 = '/Demultiplexing/Analysis/Project/GPCD/*/'+OldSampleID+'/'+OldSampleID+'_2.fastq.gz'

	NewSampleFastq_1 = '/Demultiplexing/Analysis/Project/GPCD/*/'+NewSampleID+'.original/'+NewSampleID+'_1.fastq.gz'
	NewSampleFastq_2 = '/Demultiplexing/Analysis/Project/GPCD/*/'+NewSampleID+'.original/'+NewSampleID+'_2.fastq.gz'

	ConcatCMD = 'cat '+OldSampleFastq_1+' '+NewSampleFastq_1+' > '+NewSampleDir+'/'+NewSampleID+'_1.fastq.gz'
        a = subprocess.Popen(ConcatCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
	ConcatCMD = 'cat '+OldSampleFastq_2+' '+NewSampleFastq_2+' > '+NewSampleDir+'/'+NewSampleID+'_2.fastq.gz'
        a = subprocess.Popen(ConcatCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

	return 0
	
def MultiAnal(OldSampleID, NewSampleID):

	SequencingMachine, RunID = SampleInfo(OldSampleID)

	# remove new sample dir if exists
	try :
		shutil.rmtree('/Demultiplexing/Analysis/Project/GPCD/'+RunID+'/'+NewSampleID+'/')
				
	except :
		pass

	shutil.copytree('/Demultiplexing/Analysis/Project/GPCD/'+RunID+'/'+OldSampleID+'/','/Demultiplexing/Analysis/Project/GPCD/'+RunID+'/'+NewSampleID+'/')

	# make new sample dir and change files name
	for fname in glob.glob('/Demultiplexing/Analysis/Project/GPCD/'+RunID+'/'+NewSampleID+'/'+OldSampleID+'*'):
		NewName = NewSampleID.join(fname.rsplit(OldSampleID,1))
		os.rename(fname,NewName)

	os.environ['http_proxy'] = 'http://192.168.7.12:3128/'
	os.environ['https_proxy'] = 'http://192.168.7.12:3128/'
	os.environ['ftp_proxy'] = 'http://192.168.7.12:3128/'

	OldSample=OldSampleID.strip().split("-")
	OldSampleName = OldSample[0]
	OldAnalCode = OldSample[1]

	NewSample=NewSampleID.strip().split("-")
	NewSampleName = NewSample[0]
	NewAnalCode = NewSample[1]

	js_url = "http://labge02:8080/gpcd/api/gpcd/%s/%s?key=%s" %(OldSampleName,OldSampleID,LIMS_TASK_key)
	data = urllib.urlopen(js_url).read()
	if data == "":
		print('Get '+OldSampleID+' Information from LIMS is Not Available')
		return 0  

	js_data = json.loads(data)

	labID = "MulAnaId"
	exps = js_data['pre']+';'+js_data['hyb']+';'+js_data['post']
	PutUrl = "http://labge02:8080/gpcd/api/gpcd/%s/%s?runId=%s&labId=%s&exps=%s&yield=%s&read=%s&totalN=%s&totalA=%s&totalT=%s&totalG=%s&totalC=%s&totalQ20=%s&totalQ30=%s&avgReadSize=%s&ratioN=%s&ratioGC=%s&ratioQ20=%s&ratioQ30=%s&i7idx=%s&i7seq=%s&key=%s" %(NewSampleName,NewSampleID,RunID,labID,exps,js_data['rawYield'],js_data['rawRead'],js_data['rawN'],js_data['rawA'],js_data['rawT'],js_data['rawG'],js_data['rawC'],js_data['rawQ20Base'],js_data['rawQ30Base'],js_data['rawAvgReadLength'],js_data['rawNRatio'],js_data['rawGCRatio'],js_data['rawQ20Ratio'],js_data['rawQ30Ratio'],js_data['idx1Id'],js_data['idx1Seq'],LIMS_TASK_key)

	requests.request('PUT', PutUrl)
					
	RunGPCD(RunID,NewSampleID)

	return 0


def ReDemulti(RunID):

	# find run path and sequencing machine which were used.
	RunDir = glob.glob('/data/Instrument/*/'+RunID)[0]
        SequencingMachine = glob.glob('/Demultiplexing/*/'+RunID)[0].split('/')[-2]		# find device automatically if there is runid in the device
		
	# find which SampleID have to be re-analyzed.
	try :
		NewSampleSheet = open(RunDir+'/SampleSheet_enfant.csv')
	except OSError :
		print('can\'t find '+RunDir+'/SampleSheet_enfant.csv file')
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

	
	# writing SampleIDs and transport to gpcd01
	for SampleID in SampleIDList :
		#RmDenovoFiles(SampleID)
		#RmGPCDFiles(SampleID)
		for SampleID_fastq in glob.glob('/Demultiplexing/'+SequencingMachine+'/'+RunID+'/'+SampleID+'*') :
			print("remove fastq {0}".format(SampleID_fastq))
			os.remove(SampleID_fastq)

	# run demultiplexing script
	BCLtoFastqCMD = '/data/Pipeline/Illumina/bcl2fastq_v2.17-custom/bin/bcl2fastq -R '+RunDir+' -o /Demultiplexing/'+SequencingMachine+'/'+RunID+' -r 12 -d 12 -p 12 -w 1 --minimum-trimmed-read-length 0 --mask-short-adapter-reads 10 --barcode-mismatches 1 --sample-sheet '+RunDir+'/SampleSheet_enfant.csv'
	print(BCLtoFastqCMD)
        a = subprocess.Popen(BCLtoFastqCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

	# remove old fastq file and copy new one and run fastqc script.
	for SampleID in SampleIDList :
		RunFastQC(SampleID)

def main():

	if args.action == 'ReDemulti' :
		RunID = args.RunID
		ReDemulti(RunID)
"""
	elif args.action == 'MultiAnal' :
		if os.path.isfile(args.Input) :
	                with open(args.Input) as p :
	                        for line in p :
	                                linesp = line.strip().split("\t")
	                                for i in range(2,len(linesp)):
						if linesp[i] == "" :
							continue
						OldSampleID = linesp[1]
						NewSampleID = linesp[i]
						RmDenovoFiles(NewSampleID)
						MultiAnal(OldSampleID,NewSampleID)
		else :
			SampleID = args.Input
			OldSampleID, NewSampleID = SampleID.split(" ")
			RmDenovoFiles(NewSampleID)
			MultiAnal(OldSampleID,NewSampleID)

	elif args.action == 'ParsingError' :
		if os.path.isfile(args.Input) :
	                with open(args.Input) as p :
	                        for line in p :
	                                linesp = line.strip().split()
	                                SampleID = linesp[0]
	                                ParsingError(SampleID)
		else :
			SampleID = args.Input
			ParsingError(SampleID)

	elif args.action == 'RunFastQC' :
		if os.path.isfile(args.Input) :
	                with open(args.Input) as p :
	                        for line in p :
	                                linesp = line.strip().split()
	                                SampleID = linesp[0]
	                                RmDenovoFiles(SampleID)
	                                RunFastQC(SampleID)
		else :
			SampleID = args.Input
			RmGPCDFiles(SampleID)
			RunFastQC(SampleID)
	
	elif args.action == 'RmDenovoFiles' :
		if os.path.isfile(args.Input) :
	                with open(args.Input) as p :
	                        for line in p :
	                                linesp = line.strip().split()
	                                SampleID = linesp[0]
	                                RmDenovoFiles(SampleID)
		else :
			SampleID = args.Input
			RmDenovoFiles(SampleID)
	
	elif args.action == 'RunGPCD' :
		if os.path.isfile(args.Input) :
	                with open(args.Input) as p :
	                        for line in p :
	                                linesp = line.strip().split()
	                                SampleID = linesp[0]
	                                RmDenovoFiles(SampleID)
	                                RunGPCD('',SampleID)
		else :
			SampleID = args.Input
			RmDenovoFiles(SampleID)
			RunGPCD('',SampleID)
	
	elif args.action == 'ConcatSamples' :
		OldSampleID = args.OldSampleID
		NewSampleID = args.NewSampleID
		RmDenovoFiles(NewSampleID)
		ConcatSamples(OldSampleID, NewSampleID)
		RunGPCD('',NewSampleID)
"""	

#	elif args.action == 'RmGPCDFiles' :
#		if os.path.isfile(args.Input) :
#			with open(args.Input) as p :
#				for line in p :
#					linesp = line.strip().split()
#					SampleID = linesp[0]
#					RmGPCDFiles(SampleID)
#		else :
#			SampleID = args.Input
#			RmGPCDFiles(SampleID)

main()
