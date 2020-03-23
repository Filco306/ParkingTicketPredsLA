while ping -c1 dataingestor &>/dev/null
do
  sleep 10
done
echo "No response from the data ingestor, so it should be finished!"
python3 ./index.py
