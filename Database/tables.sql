CREATE TABLE Stocks(
    ticker TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    market TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE Buy(
    id SERIAL PRIMARY KEY,
    FOREIGN KEY (ticker) REFERENCES Stocks(ticker),
    buyTime TIMESTAMP NOT NULL,
    price DECIMAL NOT NULL,
);

CREATE TABLE Sell(
    id SERIAL PRIMARY KEY
    FOREIGN KEY (ticker) REFERENCES Stocks(ticker),
    sellTime TIMESTAMP NOT NULL,
    price DECIMAL NOT NULL,
);

CREATE TABLE Blank(
    id SERIAL PRIMARY KEY
    FOREIGN KEY (ticker) REFERENCES Stocks(ticker),
    blankTime TIMESTAMP NOT NULL,
    price DECIMAL NOT NULL,
);

CREATE TABLE Pairs(
    FOREIGN KEY (stock1) REFERENCES Stocks(ticker),
    FOREIGN KEY (stock2) REFERENCES Stocks(ticker),
    standardDiv DECIMAL,
    CHECK (stock1 != stock2),
    PRIMARY KEY (stock1, stock2)
);

