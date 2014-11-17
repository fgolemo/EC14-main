#!/bin/sh
module load stopos

voxdir=${PBS_O_HOME}/EC14-voxelyze/voxelyzeMain
cd $voxdir

ncores=`sara-get-num-cores`

for ((i=1; i<=ncores; i++)) ; do
(
    stopos next -p ${pool}
    if [ "$STOPOS_RC" != "OK" ]; then # Parameter pool exhausted: we're done
        break
    fi
    ./voxelyze -f ${population}${STOPOS_VALUE}_vox.vxa -p 100 > ${traces}duringVox/${STOPOS_VALUE}.trace
    stopos remove -p ${pool}
) &
done

wait

mv ${traces}duringVox/* ${traces}afterVox/