#!/bin/sh

pool=dead${2}.pool

module load stopos
stopos create -p ${pool}
stopos add -p ${pool} $1

scriptdir=${HOME}/EC14-main/scripts

JOB_ID=`qsub -o logs -e logs -v pool=${pool} ${scriptdir}/run_vox.sh`

#display job queue
showq -u $USER
