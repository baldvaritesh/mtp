#cat $( ls -1 *.csv | sort -n  ) > new.csv
cp 1.csv output.csv
for i in {2..17}
do 
    echo -e "\n" > t1
    tail -n +2 $i.csv >> t1 
    cat output.csv t1 > t2 
    mv t2 output.csv
done
