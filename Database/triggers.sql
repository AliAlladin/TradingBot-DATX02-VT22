DROP TRIGGER IF EXISTS sell_stock
ON Sell;

CREATE OR REPLACE FUNCTION  set_sold()
  RETURNS trigger AS $$
BEGIN
    IF NEW.ticker IN (SELECT ticker FROM Buy) AND Buy.active = 'Active';
        THEN
        UPDATE Buy SET active = 'Sold' WHERE NEW.ticker = Buy.ticker AND Buy.active = 'Active';
    ELSE
        RAISE EXCEPTION 'cannot sell if its not bought'; 
    END IF;
    RETURN NEW;
END;   
$$ LANGUAGE plpgsql;

CREATE TRIGGER sell_stock
    AFTER INSERT ON Sell
    FOR EACH ROW
    EXECUTE PROCEDURE set_sold();


CREATE OR REPLACE FUNCTION coverBlanking()
    RETURNS trigger AS $$
BEGIN
    IF NEW.ticker IN (SELECT ticker FROM Blank) AND Blank.active = 'Active';
        THEN
        UPDATE Blank SET active = 'false' WHERE NEW.ticker = Blank.ticker AND Blank.active = 'Active';
        INSERT INTO Buy VALUES (NEW.id,NEW.ticker,NEW.buyTime,New.price,'cover blank');
    ELSE 
        INSERT INTO Buy VALUES (NEW.id,NEW.ticker,NEW.buyTime,New.price,'active');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER onBlankCover
    BEFORE INSERT ON Buy
    FOR EACH ROW
    EXECUTE PROCEDURE coverBlanking();
