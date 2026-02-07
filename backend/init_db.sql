-- ================================================================
-- MoodAtlas Database Initialization Script
-- ================================================================
-- PostgreSQL sürüm 12+ gerektirir
-- Bu script manuel olarak PostgreSQL'de çalıştırılmalıdır
-- ================================================================

-- 1. Database ve kullanıcı oluştur
CREATE USER moodatlas WITH PASSWORD 'moodatlas';
CREATE DATABASE moodatlas OWNER moodatlas;

-- 2. moodatlas database'ine bağlan
\c moodatlas

-- 3. Tabloları oluştur
CREATE TABLE country_mood (
    id SERIAL PRIMARY KEY,
    country_code VARCHAR(3) NOT NULL,
    country_name VARCHAR(120) NOT NULL,
    date TIMESTAMP NOT NULL,
    mood_score FLOAT NOT NULL,
    mood_label VARCHAR(20) NOT NULL,
    color_code VARCHAR(7) NOT NULL,
    valence FLOAT,
    energy FLOAT,
    danceability FLOAT,
    acousticness FLOAT,
    top_genre VARCHAR(60),
    top_track VARCHAR(200),
    news_sentiment FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_country_date UNIQUE (country_code, date)
);

CREATE TABLE mood_spike (
    id SERIAL PRIMARY KEY,
    country_code VARCHAR(3) NOT NULL,
    detected_at TIMESTAMP NOT NULL,
    previous_label VARCHAR(20) NOT NULL,
    new_label VARCHAR(20) NOT NULL,
    delta FLOAT NOT NULL,
    reason TEXT
);

-- 4. İndeksleri oluştur
CREATE INDEX idx_country_mood_code ON country_mood(country_code);
CREATE INDEX idx_country_mood_date ON country_mood(date);
CREATE INDEX idx_country_mood_code_date ON country_mood(country_code, date);
CREATE INDEX idx_mood_spike_code ON mood_spike(country_code);
CREATE INDEX idx_mood_spike_detected ON mood_spike(detected_at);
CREATE INDEX idx_mood_spike_code_detected ON mood_spike(country_code, detected_at);

-- 5. Kullanıcı izinlerini ayarla
GRANT ALL PRIVILEGES ON DATABASE moodatlas TO moodatlas;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO moodatlas;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO moodatlas;

-- 6. Varsayılan izinleri ayarla (gelecekte oluşturulacak tablolar için)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO moodatlas;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO moodatlas;
