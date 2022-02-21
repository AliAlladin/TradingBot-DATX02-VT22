CREATE TABLE Stocks(
    ticker TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    market TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE Buy(
    id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    FOREIGN KEY (ticker) REFERENCES Stocks(ticker),
    buyTime TIMESTAMP NOT NULL,
    price DECIMAL NOT NULL,
    active TEXT NOT NULL
);

CREATE TABLE Sell(
    id SERIAL NOT NULL,
    ticker TEXT NOT NULL,
    FOREIGN KEY (id) REFERENCES Buy(id),
    FOREIGN KEY (ticker) REFERENCES Stocks(ticker),
    sellTime TIMESTAMP NOT NULL,
    price DECIMAL NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE Blank(
    id SERIAL PRIMARY KEY,
    ticker TEXT,
    FOREIGN KEY (ticker) REFERENCES Stocks(ticker),
    blankTime TIMESTAMP NOT NULL,
    price DECIMAL NOT NULL
);

CREATE TABLE Pairs(
    stock1 TEXT,
    stock2 TEXT,
    FOREIGN KEY (stock1) REFERENCES Stocks(ticker),
    FOREIGN KEY (stock2) REFERENCES Stocks(ticker),
    standardDiv DECIMAL,
    CHECK (stock1 != stock2),
    PRIMARY KEY (stock1, stock2)
);

