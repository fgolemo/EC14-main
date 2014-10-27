module load stopos
poolname=$1

ncores=`sara-get-num-cores`
BASEDIR=`pwd`
cd $BASEDIR

for ((i=1; i<=ncores; i++)) ; do
  stopos next -p $poolname
  if [ "$STOPOS_RC" != "OK" ] ; then
      break
    fi
  $STOPOS_VALUE
  stopos remove -p $poolname
done
