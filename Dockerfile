FROM python:3.7.6-buster

COPY requirements.txt requirements.txt


RUN pip3 install -U kaggle
RUN pip3 install -r requirements.txt
COPY secrets/kaggle.json ./root/.kaggle/kaggle.json
COPY secrets/kaggle.json ~/.kaggle/kaggle.json
COPY . .
EXPOSE 5000

RUN chmod +x Scripts/wait_with_starting.sh

##CMD sh Scripts/fetch_data.sh
CMD bash -c Scripts/wait_with_starting.sh
##CMD python3 -u ./index.py
