-- database name : epic_games --


-- 1) publishers
CREATE TABLE IF NOT EXISTS publishers (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  website TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2) developers
CREATE TABLE IF NOT EXISTS developers (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  website TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3) genres
CREATE TABLE IF NOT EXISTS genres (
  id SERIAL PRIMARY KEY,
  name VARCHAR(128) UNIQUE NOT NULL
);

-- 4) platforms
CREATE TABLE IF NOT EXISTS platforms (
  id SERIAL PRIMARY KEY,
  name VARCHAR(128) UNIQUE NOT NULL
);

-- 5) games
CREATE TABLE IF NOT EXISTS games (
  id SERIAL PRIMARY KEY,
  slug VARCHAR(255) UNIQUE NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  release_date DATE,
  publisher_id INT REFERENCES publishers(id) ON DELETE SET NULL,
  developer_id INT REFERENCES developers(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_games_publisher_id ON games(publisher_id);
CREATE INDEX IF NOT EXISTS idx_games_developer_id ON games(developer_id);

-- 6) price_offers (قیمت/تخفیف لحظه‌ای)
CREATE TABLE IF NOT EXISTS price_offers (
  id SERIAL PRIMARY KEY,
  game_id INT NOT NULL REFERENCES games(id) ON DELETE CASCADE,
  original_price_cents INT,
  discounted_price_cents INT,
  currency VARCHAR(8) DEFAULT 'USD',
  starts_at TIMESTAMPTZ,
  ends_at TIMESTAMPTZ,
  scraped_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_price_offers_game_id ON price_offers(game_id);

-- 7) game_genres (M2M)
CREATE TABLE IF NOT EXISTS game_genres (
  game_id INT NOT NULL REFERENCES games(id) ON DELETE CASCADE,
  genre_id INT NOT NULL REFERENCES genres(id) ON DELETE CASCADE,
  PRIMARY KEY (game_id, genre_id)
);

-- 8) game_platforms (M2M)
CREATE TABLE IF NOT EXISTS game_platforms (
  game_id INT NOT NULL REFERENCES games(id) ON DELETE CASCADE,
  platform_id INT NOT NULL REFERENCES platforms(id) ON DELETE CASCADE,
  PRIMARY KEY (game_id, platform_id)
);
