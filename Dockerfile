FROM debian:stretch

LABEL org.label-schema.vcs-url="https://github.com/filco306/ParkingTicketPredsLA" \
    maintainer="Filip Cornell <filip.cornell@tui.se>"

###
### Python and pip
###
RUN apt-get update && apt-get install -y \
      python3 \
      python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install unzip
RUN apt-get update && apt-get install -y unzip

### Packages
RUN pip3 install -r requirements.txt


###
### Expose ports
###
EXPOSE 5000
EXPOSE 5006

###
### Load project into container - this will ignore all files in .dockerignore though
###
COPY . .


### Export pdf filename into bash_profile
## RUN echo "export pdf_file_name=\"LADOT\-Xerox\ Crib\ Sheet\ Agency\ Codes\ 12\-31\-2015\ \(1\).pdf\"" >> /.bash_profile
RUN echo "export FLASK_APP=run.py" >> /.bash_profile
