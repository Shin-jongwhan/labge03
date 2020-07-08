#!/bin/sh

deviceId=$1
runId=$2
record=$3
type=$4


echo 'progress 0'
mkdir -p /data/Analysis/Project/tmp/$runId
mkdir -p /data/Analysis/Project/tmp/$runId/$record

if [ $type = 'pe' ]; then
	rm -f /data/Analysis/Project/tmp/$runId/$record/$record'_raw_1.fastq.gz'
	rm -f /data/Analysis/Project/tmp/$runId/$record/$record'_raw_2.fastq.gz'
	rm -f /data/Analysis/Project/tmp/$runId/$record/$record'_1.fastq'
	rm -f /data/Analysis/Project/tmp/$runId/$record/$record'_2.fastq'
	rm -f /data/Analysis/Project/tmp/$runId/$record/$record'_1.fastq.gz'
	rm -f /data/Analysis/Project/tmp/$runId/$record/$record'_2.fastq.gz'

	echo 'fastq data copying..'
	echo 'status fastq data copying..'
	cat /Demultiplexing/$deviceId/$runId/$record'_S'*'_L'*'_R1_'*'.fastq.gz' > /data/Analysis/Project/tmp/$runId/$record/$record'_raw_1.fastq.gz' &
	cat /Demultiplexing/$deviceId/$runId/$record'_S'*'_L'*'_R2_'*'.fastq.gz' > /data/Analysis/Project/tmp/$runId/$record/$record'_raw_2.fastq.gz' &
	wait

	echo 'progress 0.3'
	cd /data/Analysis/Project/tmp/$runId/$record
	echo 'drop empty read pairs..'
	echo 'status drop empty read pairs..'
	/usr/local/java/jdk1.8/bin/java -cp /data/lims/FastQC/Toolkit.jar com.labgenomics.toolkit.ReadLengthFilter $record'_raw_1.fastq.gz' $record'_raw_2.fastq.gz' $record'_1.fastq.gz' $record'_2.fastq.gz' &
	wait

#	mv /Demultiplexing/$deviceId/$runId/$record'_1.fastq.gz' /data/Analysis/Project/tmp/$runId/$record/
#	mv /Demultiplexing/$deviceId/$runId/$record'_2.fastq.gz' /data/Analysis/Project/tmp/$runId/$record/

	rm -f /data/Analysis/Project/tmp/$runId/$record/$record'_raw_1.fastq.gz'
	rm -f /data/Analysis/Project/tmp/$runId/$record/$record'_raw_2.fastq.gz'

	echo 'progress 0.7'
	echo 'stat calculating...'
	echo 'status stat calculating...'
	/data/Tools/bin/FastQStatGz pe gz $record $record.sqs &
	/data/Tools/stat/FastQC-v0.11.4/fastqc --nogroup -t 2 -q $record'_1.fastq.gz' $record'_2.fastq.gz' &
	wait
elif [ $type = 'se' ]; then
	rm -f /data/Analysis/Project/tmp/$runId/$record/$record'_raw_1.fastq.gz'
	rm -f /data/Analysis/Project/tmp/$runId/$record/$record'_1.fastq'
	rm -f /data/Analysis/Project/tmp/$runId/$record/$record'_1.fastq.gz'

	echo 'fastq data copying..'
	cat /Demultiplexing/$deviceId/$runId/$record'_S'*'_L'*'_R1_'*'.fastq.gz' > /data/Analysis/Project/tmp/$runId/$record/$record'_raw_1.fastq.gz' &
	wait

	echo 'progress 0.3'
	cd /data/Analysis/Project/tmp/$runId/$record
	echo 'drop empty read pairs..'
	/usr/local/java/jdk1.8/bin/java -cp /data/lims/FastQC/Toolkit.jar com.labgenomics.toolkit.ReadLengthFilterSingleEnd $record'_raw_1.fastq.gz' $record'_1.fastq.gz' &
	wait

	rm -f /data/Analysis/Project/tmp/$runId/$record/$record'_raw_1.fastq.gz'

	echo 'progress 0.7'
	echo 'stat calculating...'
	/data/Tools/bin/FastQStatGz se gz $record $record.sqs &
	/data/Tools/stat/FastQC-v0.11.4/fastqc --nogroup -t 2 -q $record'_1.fastq.gz' &
	wait
fi
echo 'progress 1.0'
