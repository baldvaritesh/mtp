CREATE TYPE senti_enum AS ENUM ('positive','negative','neutral');
CREATE TYPE option_enum AS ENUM('Yes','No');
CREATE TYPE confi_enum AS ENUM('yes','no','NA');

CREATE TABLE ArticleMetaData(
article_hash_url VARCHAR(100) NOT NULL,
title TEXT,
publish_date DATE,
onlytext TEXT,
source_id INT,
source_url VARCHAR(200),
exact_url VARCHAR(200),
opinion_section option_enum,
search_text_hash VARCHAR(100),
word_count INT,
analysis_date DATE,
document_sentiment senti_enum,
pos_on_page INT,
page_number INT,
score FLOAT,
anger FLOAT,
disgust FLOAT,
fear FLOAT,
joy FLOAT,
sadness FLOAT,
PRIMARY KEY (article_hash_url)
);

CREATE TABLE ArticleAuthor(
article_id VARCHAR(100),
author TEXT,
id SERIAL,
PRIMARY KEY(id),
FOREIGN KEY (article_id) REFERENCES ArticleMetaData(article_hash_url)
);

CREATE TABLE AlchemyTaxonomy(
article_id VARCHAR(100),
id SERIAL,
taxonomy_label TEXT,
score FLOAT,
confident confi_enum,
PRIMARY KEY(id),
FOREIGN KEY (article_id) REFERENCES ArticleMetaData(article_hash_url)
);

CREATE TABLE AlchemyEntity(
article_id VARCHAR(100),
id SERIAL,
entity TEXT,
relevance FLOAT,
sentiment senti_enum,
type TEXT,
dbpedia VARCHAR(200),
PRIMARY KEY(id),
FOREIGN KEY (article_id) REFERENCES ArticleMetaData(article_hash_url)
);

CREATE TABLE AlchemyKeyword(
article_id VARCHAR(100),
id SERIAL,
keyword TEXT,
relevance FLOAT,
sentiment senti_enum,
PRIMARY KEY(id),
FOREIGN KEY (article_id) REFERENCES ArticleMetaData(article_hash_url)
);

CREATE TABLE NewsSource(
id SERIAL,
name TEXT,
url VARCHAR(200),
PRIMARY KEY(id)
);

CREATE TABLE analysis(
article_id VARCHAR(100),
place VARCHAR(200),
reason VARCHAR(200),
comment VARCHAR(500),
FOREIGN KEY (article_id) REFERENCES ArticleMetaData(article_hash_url)
);

CREATE INDEX pub_date_index ON ArticleMetaData(publish_date);
CREATE INDEX ana_date_index ON ArticleMetaData(analysis_date);
