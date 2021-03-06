
CREATE TABLE IF NOT EXISTS BuyF(
    id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    buyTime TIMESTAMP NOT NULL,
    price DECIMAL NOT NULL,
    volume DECIMAL NOT NULL

);

CREATE TABLE IF NOT EXISTS SellF(
    id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    SellTime TIMESTAMP NOT NULL,
    price DECIMAL NOT NULL,
    volume DECIMAL NOT NULL
);

CREATE TABLE IF NOT EXISTS ShortF(
    id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    shortTIme TIMESTAMP NOT NULL,
    price DECIMAL NOT NULL
);

CREATE TABLE IF NOT EXISTS PairsF(
    stock1 TEXT,
    stock2 TEXT,
    CHECK (stock1 != stock2),
    PRIMARY KEY (stock1, stock2)
);

CREATE TABLE IF NOT EXISTS PricesF(
    ticker TEXT PRIMARY KEY,
    price DECIMAL
);

