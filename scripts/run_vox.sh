#!/bin/sh
module load stopos
poolname=$1

voxdir=~/EC14-voxelyze/voxelyzeMain
cd $voxdir

ncores=`sara-get-num-cores`

for ((i=1; i<=ncores; i++)) ; do
  stopos next -p $poolname
  if [ "$STOPOS_RC" != "OK" ] ; then
      break
    fi
  $STOPOS_VALUE
  stopos remove -p $poolname
done
