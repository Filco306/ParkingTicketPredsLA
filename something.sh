TMPDIR="/gisdata/temp/"
UNZIPTOOL=unzip
WGETTOOL="/usr/bin/wget"
export PGBIN=/usr/lib/postgresql/10/bin
export PGPORT=5432
export PGHOST=localhost
export PGUSER=postgres
export PGPASSWORD=yourpasswordhere
export PGDATABASE=geocoder
PSQL=${PGBIN}/psql
SHP2PGSQL=shp2pgsql
cd /gisdata

cd /gisdata
wget https://www2.census.gov/geo/tiger/TIGER2017/PLACE/tl_2017_06_place.zip --mirror --reject=html
cd gisdata/www2.census.gov/geo/tiger/TIGER2017/PLACE
rm -f ${TMPDIR}/*.*
psql geo_db -c "DROP SCHEMA IF EXISTS tiger_staging CASCADE;"
psql geo_db -c "CREATE SCHEMA tiger_staging;"
for z in tl_2017_06*_place.zip ; do $UNZIPTOOL -o -d $TMPDIR $z; done
cd $TMPDIR;

psql geo_db -c "CREATE TABLE tiger_data.CA_place(CONSTRAINT pk_CA_place PRIMARY KEY (plcidfp) ) INHERITS(tiger.place);"
${SHP2PGSQL} -D -c -s 4269 -g the_geom   -W "latin1" tl_2017_06_place.dbf tiger_staging.ca_place | psql geo_db
psql geo_db -c "ALTER TABLE tiger_staging.CA_place RENAME geoid TO plcidfp;SELECT loader_load_staged_data(lower('CA_place'), lower('CA_place')); ALTER TABLE tiger_data.CA_place ADD CONSTRAINT uidx_CA_place_gid UNIQUE (gid);"
psql geo_db -c "CREATE INDEX idx_CA_place_soundex_name ON tiger_data.CA_place USING btree (soundex(name));"
psql geo_db -c "CREATE INDEX tiger_data_CA_place_the_geom_gist ON tiger_data.CA_place USING gist(the_geom);"
psql geo_db -c "ALTER TABLE tiger_data.CA_place ADD CONSTRAINT chk_statefp CHECK (statefp = '06');"
cd /gisdata
wget https://www2.census.gov/geo/tiger/TIGER2017/COUSUB/tl_2017_06_cousub.zip --mirror --reject=html
cd /gisdata/www2.census.gov/geo/tiger/TIGER2017/COUSUB
rm -f ${TMPDIR}/*.*
psql geo_db -c "DROP SCHEMA IF EXISTS tiger_staging CASCADE;"
psql geo_db -c "CREATE SCHEMA tiger_staging;"
for z in tl_2017_06*_cousub.zip ; do $UNZIPTOOL -o -d $TMPDIR $z; done
cd $TMPDIR;

psql geo_db -c "CREATE TABLE tiger_data.CA_cousub(CONSTRAINT pk_CA_cousub PRIMARY KEY (cosbidfp), CONSTRAINT uidx_CA_cousub_gid UNIQUE (gid)) INHERITS(tiger.cousub);"
${SHP2PGSQL} -D -c -s 4269 -g the_geom   -W "latin1" tl_2017_06_cousub.dbf tiger_staging.ca_cousub | psql geo_db
psql geo_db -c "ALTER TABLE tiger_staging.CA_cousub RENAME geoid TO cosbidfp;SELECT loader_load_staged_data(lower('CA_cousub'), lower('CA_cousub')); ALTER TABLE tiger_data.CA_cousub ADD CONSTRAINT chk_statefp CHECK (statefp = '06');"
psql geo_db -c "CREATE INDEX tiger_data_CA_cousub_the_geom_gist ON tiger_data.CA_cousub USING gist(the_geom);"
psql geo_db -c "CREATE INDEX idx_tiger_data_CA_cousub_countyfp ON tiger_data.CA_cousub USING btree(countyfp);"
cd /gisdata
wget https://www2.census.gov/geo/tiger/TIGER2017/TRACT/tl_2017_06_tract.zip --mirror --reject=html
cd /gisdata/www2.census.gov/geo/tiger/TIGER2017/TRACT
rm -f ${TMPDIR}/*.*
psql geo_db -c "DROP SCHEMA IF EXISTS tiger_staging CASCADE;"
psql geo_db -c "CREATE SCHEMA tiger_staging;"
for z in tl_2017_06*_tract.zip ; do $UNZIPTOOL -o -d $TMPDIR $z; done
cd $TMPDIR;

psql geo_db -c "CREATE TABLE tiger_data.CA_tract(CONSTRAINT pk_CA_tract PRIMARY KEY (tract_id) ) INHERITS(tiger.tract); "
${SHP2PGSQL} -D -c -s 4269 -g the_geom   -W "latin1" tl_2017_06_tract.dbf tiger_staging.ca_tract | psql geo_db
psql geo_db -c "ALTER TABLE tiger_staging.CA_tract RENAME geoid TO tract_id;  SELECT loader_load_staged_data(lower('CA_tract'), lower('CA_tract')); "
        psql geo_db -c "CREATE INDEX tiger_data_CA_tract_the_geom_gist ON tiger_data.CA_tract USING gist(the_geom);"
        psql geo_db -c "VACUUM ANALYZE tiger_data.CA_tract;"
        psql geo_db -c "ALTER TABLE tiger_data.CA_tract ADD CONSTRAINT chk_statefp CHECK (statefp = '06');"
cd /gisdata
cd /gisdata/www2.census.gov/geo/tiger/TIGER2017/FACES/
rm -f ${TMPDIR}/*.*
psql geo_db -c "DROP SCHEMA IF EXISTS tiger_staging CASCADE;"
psql geo_db -c "CREATE SCHEMA tiger_staging;"
for z in tl_*_06*_faces*.zip ; do $UNZIPTOOL -o -d $TMPDIR $z; done
cd $TMPDIR;

psql geo_db -c "CREATE TABLE tiger_data.CA_faces(CONSTRAINT pk_CA_faces PRIMARY KEY (gid)) INHERITS(tiger.faces);"
for z in *faces*.dbf; do
${SHP2PGSQL} -D   -D -s 4269 -g the_geom -W "latin1" $z tiger_staging.CA_faces | psql geo_db
psql geo_db -c "SELECT loader_load_staged_data(lower('CA_faces'), lower('CA_faces'));"
done

psql geo_db -c "CREATE INDEX tiger_data_CA_faces_the_geom_gist ON tiger_data.CA_faces USING gist(the_geom);"
        psql geo_db -c "CREATE INDEX idx_tiger_data_CA_faces_tfid ON tiger_data.CA_faces USING btree (tfid);"
        psql geo_db -c "CREATE INDEX idx_tiger_data_CA_faces_countyfp ON tiger_data.CA_faces USING btree (countyfp);"
        psql geo_db -c "ALTER TABLE tiger_data.CA_faces ADD CONSTRAINT chk_statefp CHECK (statefp = '06');"
        psql geo_db -c "vacuum analyze tiger_data.CA_faces;"
cd /gisdata
cd /gisdata/www2.census.gov/geo/tiger/TIGER2017/FEATNAMES/
rm -f ${TMPDIR}/*.*
psql geo_db -c "DROP SCHEMA IF EXISTS tiger_staging CASCADE;"
psql geo_db -c "CREATE SCHEMA tiger_staging;"
for z in tl_*_06*_featnames*.zip ; do $UNZIPTOOL -o -d $TMPDIR $z; done
cd $TMPDIR;

psql geo_db -c "CREATE TABLE tiger_data.CA_featnames(CONSTRAINT pk_CA_featnames PRIMARY KEY (gid)) INHERITS(tiger.featnames);ALTER TABLE tiger_data.CA_featnames ALTER COLUMN statefp SET DEFAULT '06';"
for z in *featnames*.dbf; do
${SHP2PGSQL} -D   -D -s 4269 -g the_geom -W "latin1" $z tiger_staging.CA_featnames | psql geo_db
psql geo_db -c "SELECT loader_load_staged_data(lower('CA_featnames'), lower('CA_featnames'));"
done

psql geo_db -c "CREATE INDEX idx_tiger_data_CA_featnames_snd_name ON tiger_data.CA_featnames USING btree (soundex(name));"
psql geo_db -c "CREATE INDEX idx_tiger_data_CA_featnames_lname ON tiger_data.CA_featnames USING btree (lower(name));"
psql geo_db -c "CREATE INDEX idx_tiger_data_CA_featnames_tlid_statefp ON tiger_data.CA_featnames USING btree (tlid,statefp);"
psql geo_db -c "ALTER TABLE tiger_data.CA_featnames ADD CONSTRAINT chk_statefp CHECK (statefp = '06');"
psql geo_db -c "vacuum analyze tiger_data.CA_featnames;"
cd /gisdata
cd /gisdata/www2.census.gov/geo/tiger/TIGER2017/EDGES/
rm -f ${TMPDIR}/*.*
psql geo_db -c "DROP SCHEMA IF EXISTS tiger_staging CASCADE;"
psql geo_db -c "CREATE SCHEMA tiger_staging;"
for z in tl_*_06*_edges*.zip ; do $UNZIPTOOL -o -d $TMPDIR $z; done
cd $TMPDIR;

psql geo_db -c "CREATE TABLE tiger_data.CA_edges(CONSTRAINT pk_CA_edges PRIMARY KEY (gid)) INHERITS(tiger.edges);"
for z in *edges*.dbf; do
${SHP2PGSQL} -D   -D -s 4269 -g the_geom -W "latin1" $z tiger_staging.CA_edges | psql geo_db
psql geo_db -c "SELECT loader_load_staged_data(lower('CA_edges'), lower('CA_edges'));"
done

psql geo_db -c "ALTER TABLE tiger_data.CA_edges ADD CONSTRAINT chk_statefp CHECK (statefp = '06');"
psql geo_db -c "CREATE INDEX idx_tiger_data_CA_edges_tlid ON tiger_data.CA_edges USING btree (tlid);"
psql geo_db -c "CREATE INDEX idx_tiger_data_CA_edgestfidr ON tiger_data.CA_edges USING btree (tfidr);"
psql geo_db -c "CREATE INDEX idx_tiger_data_CA_edges_tfidl ON tiger_data.CA_edges USING btree (tfidl);"
psql geo_db -c "CREATE INDEX idx_tiger_data_CA_edges_countyfp ON tiger_data.CA_edges USING btree (countyfp);"
psql geo_db -c "CREATE INDEX tiger_data_CA_edges_the_geom_gist ON tiger_data.CA_edges USING gist(the_geom);"
psql geo_db -c "CREATE INDEX idx_tiger_data_CA_edges_zipl ON tiger_data.CA_edges USING btree (zipl);"
psql geo_db -c "CREATE TABLE tiger_data.CA_zip_state_loc(CONSTRAINT pk_CA_zip_state_loc PRIMARY KEY(zip,stusps,place)) INHERITS(tiger.zip_state_loc);"
psql geo_db -c "INSERT INTO tiger_data.CA_zip_state_loc(zip,stusps,statefp,place) SELECT DISTINCT e.zipl, 'CA', '06', p.name FROM tiger_data.CA_edges AS e INNER JOIN tiger_data.CA_faces AS f ON (e.tfidl = f.tfid OR e.tfidr = f.tfid) INNER JOIN tiger_data.CA_place As p ON(f.statefp = p.statefp AND f.placefp = p.placefp ) WHERE e.zipl IS NOT NULL;"
psql geo_db -c "CREATE INDEX idx_tiger_data_CA_zip_state_loc_place ON tiger_data.CA_zip_state_loc USING btree(soundex(place));"
psql geo_db -c "ALTER TABLE tiger_data.CA_zip_state_loc ADD CONSTRAINT chk_statefp CHECK (statefp = '06');"
psql geo_db -c "vacuum analyze tiger_data.CA_edges;"
psql geo_db -c "vacuum analyze tiger_data.CA_zip_state_loc;"
psql geo_db -c "CREATE TABLE tiger_data.CA_zip_lookup_base(CONSTRAINT pk_CA_zip_state_loc_city PRIMARY KEY(zip,state, county, city, statefp)) INHERITS(tiger.zip_lookup_base);"
psql geo_db -c "INSERT INTO tiger_data.CA_zip_lookup_base(zip,state,county,city, statefp) SELECT DISTINCT e.zipl, 'CA', c.name,p.name,'06'  FROM tiger_data.CA_edges AS e INNER JOIN tiger.county As c  ON (e.countyfp = c.countyfp AND e.statefp = c.statefp AND e.statefp = '06') INNER JOIN tiger_data.CA_faces AS f ON (e.tfidl = f.tfid OR e.tfidr = f.tfid) INNER JOIN tiger_data.CA_place As p ON(f.statefp = p.statefp AND f.placefp = p.placefp ) WHERE e.zipl IS NOT NULL;"
psql geo_db -c "ALTER TABLE tiger_data.CA_zip_lookup_base ADD CONSTRAINT chk_statefp CHECK (statefp = '06');"
psql geo_db -c "CREATE INDEX idx_tiger_data_CA_zip_lookup_base_citysnd ON tiger_data.CA_zip_lookup_base USING btree(soundex(city));"
cd /gisdata
cd /gisdata/www2.census.gov/geo/tiger/TIGER2017/ADDR/
rm -f ${TMPDIR}/*.*
psql geo_db -c "DROP SCHEMA IF EXISTS tiger_staging CASCADE;"
psql geo_db -c "CREATE SCHEMA tiger_staging;"
for z in tl_*_06*_addr*.zip ; do $UNZIPTOOL -o -d $TMPDIR $z; done
cd $TMPDIR;

psql geo_db -c "CREATE TABLE tiger_data.CA_addr(CONSTRAINT pk_CA_addr PRIMARY KEY (gid)) INHERITS(tiger.addr);ALTER TABLE tiger_data.CA_addr ALTER COLUMN statefp SET DEFAULT '06';"
for z in *addr*.dbf; do
${SHP2PGSQL} -D   -D -s 4269 -g the_geom -W "latin1" $z tiger_staging.CA_addr | psql geo_db
psql geo_db -c "SELECT loader_load_staged_data(lower('CA_addr'), lower('CA_addr'));"
done

psql geo_db -c "ALTER TABLE tiger_data.CA_addr ADD CONSTRAINT chk_statefp CHECK (statefp = '06');"
        psql geo_db -c "CREATE INDEX idx_tiger_data_CA_addr_least_address ON tiger_data.CA_addr USING btree (least_hn(fromhn,tohn) );"
        psql geo_db -c "CREATE INDEX idx_tiger_data_CA_addr_tlid_statefp ON tiger_data.CA_addr USING btree (tlid, statefp);"
        psql geo_db -c "CREATE INDEX idx_tiger_data_CA_addr_zip ON tiger_data.CA_addr USING btree (zip);"
        psql geo_db -c "CREATE TABLE tiger_data.CA_zip_state(CONSTRAINT pk_CA_zip_state PRIMARY KEY(zip,stusps)) INHERITS(tiger.zip_state); "
        psql geo_db -c "INSERT INTO tiger_data.CA_zip_state(zip,stusps,statefp) SELECT DISTINCT zip, 'CA', '06' FROM tiger_data.CA_addr WHERE zip is not null;"
        psql geo_db -c "ALTER TABLE tiger_data.CA_zip_state ADD CONSTRAINT chk_statefp CHECK (statefp = '06');"
        psql geo_db -c "vacuum analyze tiger_data.CA_addr;"
