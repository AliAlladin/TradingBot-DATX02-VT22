
CREATE TABLE IF NOT EXISTS Buy(
    id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    buyTime TIMESTAMP NOT NULL,
    price DECIMAL NOT NULL
);

CREATE TABLE IF NOT EXISTS Sell(
    id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    SellTime TIMESTAMP NOT NULL,
    price DECIMAL NOT NULL
);

CREATE TABLE IF NOT EXISTS Short(
    id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    shortTIme TIMESTAMP NOT NULL,
    price DECIMAL NOT NULL
);

CREATE TABLE IF NOT EXISTS Pairs(
    stock1 TEXT,
    stock2 TEXT,
    CHECK (stock1 != stock2),
    PRIMARY KEY (stock1, stock2)
);

CREATE TABLE IF NOT EXISTS Prices(
    ticker PRIMARY KEY,
    price DECIMAL
);

