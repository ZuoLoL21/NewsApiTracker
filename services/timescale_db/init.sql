 CREATE EXTENSION IF NOT EXISTS timescaledb;

  CREATE TABLE articles (
      id SERIAL,
      topic VARCHAR(255) NOT NULL,
      published_at TIMESTAMPTZ NOT NULL,
      source_name VARCHAR(255),
      author VARCHAR(255),
      title TEXT,
      description TEXT,
      url TEXT UNIQUE,
      url_to_image TEXT,
      content TEXT,
      sentiment VARCHAR(20) NOT NULL,
      created_at TIMESTAMPTZ DEFAULT NOW(),
      PRIMARY KEY (id, published_at)
  );

  SELECT create_hypertable('articles', 'published_at');

  CREATE INDEX idx_topic_time ON articles (topic, published_at DESC);
  CREATE INDEX idx_sentiment ON articles (sentiment);