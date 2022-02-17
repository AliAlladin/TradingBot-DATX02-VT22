 CREATE VIEW Purchase AS (
    SELECT id, ticker, buyTime, sellTime, , buyPrice, sellPrice, (sellPrice-buyPrice) as priceDifference
    FROM Buy , Sell
    WHERE Buy.id=Sell.id 
); 
