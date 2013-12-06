echo 'Removing old files:'
rm -f op_withbluevec.txt op_withoutbluevec.txt

echo 'Running:'
export LD_LIBRARY_PATH="/home/mh735/hw/hdf-jive/lib/:$LD_LIBRARY_PATH";  /tmp/nu/compilation/sim_WITHBLUE.x > op_withbluevec.txt
export LD_LIBRARY_PATH="/home/mh735/hw/hdf-jive/lib/:$LD_LIBRARY_PATH";  /tmp/nu/compilation/sim_WITHOUTBLUE.x > op_withoutbluevec.txt


echo "Diff of cpp files:"
diff /tmp/nu/compilation/sim_WITHBLUE.cpp /tmp/nu/compilation/sim_WITHOUTBLUE.cpp
echo "-----"

echo 'Diffs:'
meld op_withoutbluevec.txt op_withbluevec.txt 
