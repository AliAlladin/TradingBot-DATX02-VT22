DROP TRIGGER IF EXISTS sell_stock
ON Sell;

CREATE OR REPLACE FUNCTION  set_sold()
  RETURNS trigger AS $$
BEGIN
    IF NEW.ticker IN (SELECT ticker FROM Stocks)
        THEN
        raise notice 'Hello World!';
        UPDATE Buy SET active = 'Sold' WHERE NEW.ticker = Buy.ticker AND Buy.active = 'Active';
    END IF;
    RETURN NEW;
END;   
$$ LANGUAGE plpgsql;

CREATE TRIGGER sell_stock
    AFTER INSERT ON Sell
    FOR EACH ROW
    EXECUTE PROCEDURE set_sold();
