
for (( i=1; i < 37; i++ )); do
    ssdeep -s ./data/$i/* >> ssdeep_digests.txt
done

# remove ssdeep,1.1--blocksize:hash:hash,filename
