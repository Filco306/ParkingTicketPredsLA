# Moves the kaggle json api key to the correct direcotry
echo "Creating dir"
mkdir ~/.kaggle
echo "Moving file to dir"
mv secrets/kaggle.json ~/.kaggle/
