k=37

for (( i=0; i < k-1; i++ )); do
    for (( j=i+1; j < k; j++ )); do
        ssdeep -k ssdeep_digests${i}.txt -s -t 49 ssdeep_digests${j}.txt >> ssdeep.txt
    done
done

for (( i=0; i < k; i++ )); do
    ssdeep -k ssdeep_digests${i}.txt -s -t 49 ssdeep_digests${i}.txt >> ssdeep_dup.txt
done
