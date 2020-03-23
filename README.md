# ParkingTicketPredsLA

This project is a project for me to learn how to create an entire dashboard application using docker orchestration, a postgres database and then visualizing this data using Bokeh, another tool I wanted to learn.

## What this project does

This project basically sets up a database for the LA Parking Ticket dataset, combined with addresses from LA. This later is queried by a flask/Bokeh application, creating visualizations for the data set.

I mainly did this project to create an end-to-end solution using all different techniques needed to create something like this, and just learn and get better. If you have any ideas, issues or anything, feel free to drop me a message.

## How to run it

The steps are simple.

### Set up

- Make sure you have Docker.
- Define the keys inside (just copying the .example-files would make it work):
  - `.api_env`
  - `.db_env`
  - `.ingest_env`
- Place a `kaggle.json` file in `secrets`. That is the set up you need. This is a .json-file with your kaggle-credentials that you get from Kaggle.

### Run - for the first time or once it is set up.

The first time you run the repo, you need to build the different images and run the containers. This will create a postgres database, followed by running a container of the image `dataingestor`  which will download all of the data and process it as necessary.

```
docker-compose up --build
```

Let it run, until it is done. When it has run once, in the future, use `bash run_app.sh` to start the application with the dashboard.

## NOTE

- The first time you run it, it may take some time to digest and process everything, since the data contains more than 10 million parking tickets. You can limit this by setting `MAX_TO_PROCESS` to the maximum number of tickets you would like to process, if you would like to try this out a bit faster.
- Some parking tickets are dropped in the preprocessing, so all are not visualized necessarily.
