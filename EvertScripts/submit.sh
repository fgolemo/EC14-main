#!/bin/bash

# Usage: submit.sh Paramfile [analysis script]

# Create stopos pool. Removes any earlier pool
module load stopos
stopos create -p monee.pool 
stopos add -p monee.pool $1

NR_LINES=`cat $1 | wc -l`
let NR_NODES=(${NR_LINES}+11)/12

JOB_ID=`qsub -o logs -e logs -t 1-${NR_NODES} scripts/run_monee.sh`

# Submit analysis - the name of that script to be passed as 2nd argument
if [ -e $2 ] 
then
  qsub -o logs -e logs -W depend=afterokarray:${JOB_ID} $2
fi 

#display job queue
showq -u $USER
