# database


* We have used Postgres databse.

* To take backup of postgres databse, run following command:

sudo -u postgres pg_dump -Fc -c db_name > file_name.pgdump

* To restore the database, first create that database and than run following command:

sudo -u postgres pg_restore -U postgres -d db_name -v file_name.pgdump

------------------------------------------------------------------------------------------------------

We have 2 databses for our project. One is for onion and other is for news articles. Files for them are "onion.db_bkup" and "news_articles.db_bkup" respectively.

To resore them, first create respective databse in postgres using command:

	CREATE DATABASE <db_name>;
	
Then use above stated commands to export on your system.

Structure for onion database can be found here:

	- mtp/database_backup/onionData/ReadMe.md
	
Structure for news article database can be found here:

	- mtp/newsArticleWork/sil.sql
