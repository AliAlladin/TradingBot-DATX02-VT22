 CREATE OR REPLACE VIEW  Purchase AS (
    SELECT Buy.id as buyID, Sell.id sellID, Buy.ticker buyTicker,  Sell.ticker SellTicker, buyTime, sellTime, Buy.price as bPrice, Sell.price as sPrice, (Sell.price - Buy.price) as priceDifference
    FROM Buy, Sell
    WHERE Buy.ticker=Sell.ticker 
); 