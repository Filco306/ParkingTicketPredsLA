CREATE TABLE TEST (
  ID SERIAL PRIMARY KEY,
  NAME VARCHAR NOT NULL DEFAULT 'test',
  amount INTEGER NOT NULL DEFAULT 10
);

create type DIRECTION as enum('N', 'S', 'E', 'W');

CREATE TABLE ADDRESSES (
  ID SERIAL PRIMARY KEY,
  HSE_ID INTEGER UNIQUE,
  PIN VARCHAR(20),
  PIND VARCHAR(20),
  HSE_NBR VARCHAR(20),
  HSE_FRAC_NBR VARCHAR(20),
  HSE_DIR_CD VARCHAR(100),
  STR_NM VARCHAR(200),
  STR_SFX_CD DIRECTION,
  STR_SFX_DIR_CD VARCHAR(20),
  UNIT_RANGE VARCHAR(100),
 ZIP_CD VARCHAR(10),
 LAT FLOAT,
 LON FLOAT,
 X_COORD_NBR FLOAT,
 Y_COORD_NBR FLOAT,
 ASGN_STTS_IND VARCHAR(2),
 ENG_DIST VARCHAR(2),
 CNCL_DIST INTEGER
);

CREATE TABLE PARKINGTICKET_RAW (
  ID SERIAL PRIMARY KEY,
  TICKETNUMBER VARCHAR(50),
  ISSUEDATE DATE,
  ISSUETIME INTEGER,
  METERID VARCHAR(50),
  MARKEDTIME INTEGER,
  RPSTATEPLATE VARCHAR(100),
  PLATEEXPIRYDATE INTEGER,
  VIN VARCHAR(100),
  MAKE VARCHAR(100),
  BODYSTYLE VARCHAR(100),
  COLOR VARCHAR(100),
  LOCATION VARCHAR(200),
  ROUTE VARCHAR(100),
  AGENCYCODE INTEGER,
  VIOLATIONCODE VARCHAR(300),
  VIOLATIONDESC VARCHAR(300),
  FINEAMOUNT INTEGER,
  LATITUDE FLOAT,
  LONGITUDE FLOAT,
  AGENCYDESCRIPTION VARCHAR(300),
  COLORDESCRIPTION VARCHAR(300),
  BODYSTYLEDESC VARCHAR(300)
);

CREATE TABLE PARKINGTICKET (
  ID SERIAL PRIMARY KEY,
  ticketnumber VARCHAR(40) UNIQUE,
 meterid VARCHAR(50),
 markedtime INTEGER,
 rpstateplate VARCHAR(100),
 plateexpirydate INTEGER,
 vin VARCHAR(100),
 make VARCHAR(100),
 bodystyle VARCHAR(100),
 color VARCHAR(100),
 location_x VARCHAR(100),
 route VARCHAR(100),
 agency INTEGER,
 violationcode VARCHAR(100),
 violationdescription VARCHAR(200),
 fineamount INTEGER,
 latitude FLOAT,
 longitude FLOAT,
 agencydescription VARCHAR(200),
 colordescription VARCHAR(200),
 bodystyledescription VARCHAR(200),
 location VARCHAR(100),
 hse_dir_cd VARCHAR(100),
 hse_nbr VARCHAR(100),
 str_sfx_cd VARCHAR(100),
 str_nm VARCHAR(100),
 exactissuingtime TIMESTAMPTZ
);

CREATE TABLE AGENCY (
  ID SERIAL PRIMARY KEY,
  AGENCYCODE INTEGER UNIQUE,
  AGENCYNAME VARCHAR(100) UNIQUE,
  AGENCYSHORTNAME VARCHAR(100) UNIQUE
);