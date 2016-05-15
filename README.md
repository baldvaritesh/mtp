# mtp


To take backup of postgres databse, run following command:

sudo -u postgres pg_dump -Fc -c db_name > file_name.pgdump  

To restore the database, first create that database and than run following command:

sudo -u postgres /usr/local/pgsql/bin/pg_restore -U postgres -d db_name -v file_name.pgdump
