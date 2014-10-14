#!/bin/bash

#
# Created by B.P.M. Weel on 3/20/12.
# Copyright 2012 VU. All rights reserved.

#PBS -lnodes=1 -lwalltime=00:09:59

### Set the simulation-specific parameters
#--------------------------------------------------------------------------------------------------#
workdir=${HOME}/monee/
roborobodir=${HOME}/monee/RoboRobo
mytmpdir=monee #Subdirectory used in nodes' scratch space
#--------------------------------------------------------------------------------------------------#

#echo "$(date)"
#echo "Script running on `hostname`"

#echo "Nodes reserved:"
NODES="$(sort $PBS_NODEFILE | uniq)"
#echo "$NODES"

#Start master process on this host
#echo "Re-creating tempdir..."
cd $TMPDIR;
rm -rf $mytmpdir
mkdir $mytmpdir

#TODO: only copy necessary files...
#echo "Copying roborobo to scratch dir..."
cp -rf ${roborobodir} $mytmpdir/

#echo "Starting runs..."
cd ${mytmpdir}/RoboRobo

BASEDIR=`pwd`
SCRIPTDIR=scripts
TEMPLATEDIR=${BASEDIR}/template/

module load stopos

ncores=`sara-get-num-cores`
cd $BASEDIR

for ((i=1; i<=ncores; i++)) ; do
(
    # read job parameters from disparm string pool
    # Obsolete, switched to stopos disparm -n -p ${HOME}/monee/RoboRobo/monee.pool
    stopos next -p monee.pool

    if [ "$STOPOS_RC" != "OK" ]; then # Parameter pool exhausted: we're done
        break
    fi

    ### Run the simulation
    SEED=$RANDOM
    #echo "Running experiment with parameters: --seed ${SEED} --basedir ${BASEDIR}/ --templatedir ${TEMPLATEDIR} ${STOPOS_VALUE}"
    ${BASEDIR}/scripts/monee.sh --seed ${SEED} --basedir ${BASEDIR} --templatedir ${TEMPLATEDIR} ${STOPOS_VALUE}

    stopos remove -p monee.pool
) &
done

wait
