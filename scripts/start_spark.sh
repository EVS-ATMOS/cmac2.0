export SPARK_SSH_FOREGROUND="y"
source activate cmac_env
cat $PBS_NODEFILE | uniq > temp
tail -n +2 temp > $SPARK_HOME/conf/slaves
$SPARK_HOME/sbin/start-master.sh 
$SPARK_HOME/sbin/start-slaves.sh 
