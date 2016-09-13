CREATE DATABASE "onion";

create table wholesaleoniondata (

dateofdata       date                   ,
 mandicode        integer                ,
 arrivalsintons   numeric                ,
 origin           character varying(50)  ,
 variety          character varying(100) ,
 minpricersqtl    numeric                ,
 maxpricersqtl    numeric                ,
 modalpricersqtl  numeric );

-- COPY wholesaleoniondata FROM 'C:\Users\KAPILT~1\Downloads\ONIOND~1\Wholesaledata.csv' DELIMITER ',' NULL AS 'NULL' CSV;


 create table mandis(
 mandicode  SERIAL                ,
 mandiname  character varying(200) ,
 statecode  integer                 not null,
 latitude   numeric                ,
 longitude  numeric                ,
 centreid   integer
 );

--COPY mandis(mandiname,statecode,latitude,longitude,centreid) FROM '/home/reshma/Desktop/Reshma/Major/project/Onion Data Cleared/Mandi.csv' DELIMITER ',' NULL AS 'NULL' CSV;


 create table states (
 statecode SERIAL,
 state varchar(100)
 );


--COPY states(state) FROM '/home/kapil/Desktop/project/Onion Data Cleared/States.csv'  DELIMITER ',' NULL AS 'NULL' CSV;

 create table centres(
 CentreId SERIAL,
 statecode INT,
 centrename varchar(100),
 longitude DECIMAL,
 latitude DECIMAL
 );

-- COPY centres(statecode,centrename,longitude,latitude) FROM '/home/kapil/Desktop/project/Onion Data Cleared/centres.csv'  DELIMITER ',' NULL AS 'NULL' CSV;

CREATE TABLE RetailOnionData(
    DateOfData DATE,
    CentreId INT,
    Price DECIMAL
);

-- COPY RetailOnionData FROM 'C:\Users\KAPILT~1\Downloads\ONIOND~1\retaildata.csv' DELIMITER ',' NULL AS 'NULL' CSV;


-- This command is used to set empty modalprice based on minimum and maximum price
update wholesaleoniondata
set modalpricersqtl = (minpricersqtl + maxpricersqtl * 2) / 3
where modalpricersqtl is NULL and minpricersqtl is not null and maxpricersqtl is not null;

-- This command is used to set empty modalprice based on minimum price if maximum price is null
update wholesaleoniondata
set modalpricersqtl = minpricersqtl
where modalpricersqtl is NULL and minpricersqtl is not null and maxpricersqtl is null;

-- This command is used to set empty modalprice based on maximum price if minimum price is null
update wholesaleoniondata
set modalpricersqtl = maxpricersqtl
where modalpricersqtl is NULL and minpricersqtl is null and maxpricersqtl is not null;


CREATE TABLE expoAvgSmoothedData(
dateofdata DATE,
centreid INT,
wholesaleprice DECIMAL,
retailprice DECIMAL,
arrivalsintons DECIMAL
);

-- COPY expoavgsmootheddata FROM 'C:\Users\KAPILT~1\Desktop\Project\ONIOND~1\expoavgsmootheddata.csv'  DELIMITER ',' CSV NULL AS 'NULL';

-- To take back up of database

pg_dump onion > onion.database

-- Back up Commands

COPY wholesaleoniondata TO '/home/kapil/Desktop/project/Onion Data Cleared/csv_bkup/wholesaleoniondata.csv' DELIMITER ',' NULL AS 'NULL' CSV;
COPY mandis TO '/home/kapil/Desktop/project/Onion Data Cleared/csv_bkup/mandis.csv' DELIMITER ',' NULL AS 'NULL' CSV;
COPY states TO '/home/kapil/Desktop/project/Onion Data Cleared/csv_bkup/states.csv' DELIMITER ',' NULL AS 'NULL' CSV;
COPY centres TO '/home/kapil/Desktop/project/Onion Data Cleared/csv_bkup/centres.csv' DELIMITER ',' NULL AS 'NULL' CSV;
COPY RetailOnionData TO '/home/kapil/Desktop/project/Onion Data Cleared/csv_bkup/RetailOnionData.csv' DELIMITER ',' NULL AS 'NULL' CSV;
COPY expoAvgSmoothedData TO '/home/kapil/Desktop/project/Onion Data Cleared/csv_bkup/expoAvgSmoothedData.csv' DELIMITER ',' NULL AS 'NULL' CSV;

