-- Таблица для хранения свечных данных
-- drop table if exists candles;

CREATE TABLE candles (
    -- Уникальный идентификатор записи
    id BIGSERIAL PRIMARY KEY,
    
    -- Идентификатор инструмента (UID из Tinkoff API)
    instrument_uid VARCHAR(50) NOT NULL,
    
    -- Временная метка начала свечи (UTC)
    candle_time TIMESTAMPTZ NOT NULL,
    
    -- Ценовые данные (используем NUMERIC для точности)
    open_price NUMERIC(20, 6) NOT NULL,   -- Цена открытия
    close_price NUMERIC(20, 6) NOT NULL,  -- Цена закрытия
    high_price NUMERIC(20, 6) NOT NULL,   -- Максимальная цена
    low_price NUMERIC(20, 6) NOT NULL,    -- Минимальная цена
    
    -- Объём торгов в лотах
    volume BIGINT NOT NULL,
    
    -- Интервал свечи (опционально, для удобства)
    interval VARCHAR(10) DEFAULT '1min',  -- 1min, 5min, 15min, hour, day
    
    -- Служебная информация
    is_complete BOOLEAN DEFAULT TRUE,      -- Завершена ли свеча
    created_at TIMESTAMPTZ DEFAULT NOW(),  -- Когда запись добавлена в БД
    
    -- Ограничения
    UNIQUE(instrument_uid, candle_time, interval)
);

-- Индексы для быстрого поиска
CREATE INDEX idx_candles_instrument_time 
    ON candles(instrument_uid, candle_time DESC);

CREATE INDEX idx_candles_time 
    ON candles(candle_time DESC);

-- Комментарии к колонкам (документация)
COMMENT ON TABLE candles IS 'Свечные данные по инструментам';
COMMENT ON COLUMN candles.instrument_uid IS 'UID инструмента (из Tinkoff API)';
COMMENT ON COLUMN candles.candle_time IS 'Начало свечи в UTC';
COMMENT ON COLUMN candles.open_price IS 'Цена открытия';
COMMENT ON COLUMN candles.close_price IS 'Цена закрытия';
COMMENT ON COLUMN candles.high_price IS 'Максимальная цена за интервал';
COMMENT ON COLUMN candles.low_price IS 'Минимальная цена за интервал';
COMMENT ON COLUMN candles.volume IS 'Объём торгов в лотах';
COMMENT ON COLUMN candles.interval IS 'Интервал свечи (1min, 5min, hour, day)';
COMMENT ON COLUMN candles.is_complete IS 'Флаг завершённой свечи (True - можно использовать)';

select * from candles;

