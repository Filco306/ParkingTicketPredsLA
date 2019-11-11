FROM debian:stretch

LABEL org.label-schema.vcs-url="https://github.com/TUI-Nordic/ml-next-ancillary" \
    maintainer="Filip Cornell <filip.cornell@tui.se>"


#RUN apt-get update; apt-get install curl



#Debian 9
#RUN curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list



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
RUN yes | pip3 install pyproj pandas numpy holidays kaggle bokeh scipy flask tornado plotly


###
### Expose ports
###
EXPOSE 5000
EXPOSE 5006

### TODO: I need to prepare the .kaggle.json



###
### Load project into container - this will ignore all files in .dockerignore though
###
COPY . .


### Export pdf filename into bash_profile
RUN echo "export pdf_file_name=\"LADOT\-Xerox\ Crib\ Sheet\ Agency\ Codes\ 12\-31\-2015\ \(1\).pdf\"" >> /.bash_profile


###
### Run data fetching and
### TODO: setup_pip.sh is not necessary right?
### Here, we set up the directories, packages, fetch the data, preprocess it and then run the app
###
CMD ["sh","-c",". /.bash_profile \
      && sh Scripts/move_secret.sh \
      && sh setup_directories.sh \
      && sh fetch_data.sh \
      && sh Scripts/preprocess_all_data.sh \
      && sh run.sh"]
