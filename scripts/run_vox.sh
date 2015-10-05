#!/bin/sh
module load stopos

voxdir=${PBS_O_HOME}/EC14-voxelyze/voxelyzeMain
cd $voxdir

ncores=`sara-get-num-cores`

mkdir "$TMPDIR"/vox

for ((i=1; i<=ncores; i++)) ; do
(
    stopos next -p ${pool}
    if [ "$STOPOS_RC" != "OK" ]; then # Parameter pool exhausted: were done
        echo 'No next. breaking.'
        break
    fi
    ./voxelyze -f ${population}${STOPOS_VALUE}_vox.vxa -p 100 > "$TMPDIR"/vox/${STOPOS_VALUE}.trace
    mv "$TMPDIR"/vox/${STOPOS_VALUE}.trace ${traces}afterVox/${STOPOS_VALUE}.trace

    echo "trace ${STOPOS_VALUE} done"
    stopos remove -p ${pool}
) &
done

wait
echo "done"
