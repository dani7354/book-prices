 -- Get the 100 latest failed price updates
 SELECT fpu.Created, fpu.Reason, b.Title, CONCAT(bs.Url, bsb.Url) AS Url, bs.Id AS BookStoreId, b.Id AS BookId
 FROM FailedPriceUpdate fpu
 INNER JOIN Book b ON b.Id = fpu.BookId
 INNER JOIN BookStore bs ON bs.Id = fpu.BookStoreId
 INNER JOIN BookStoreBook bsb ON bsb.BookId = fpu.BookId AND bsb.BookStoreId = fpu.BookStoreId
 ORDER BY fpu.created DESC
 LIMIT 100;


-- Get the 100 latest price updates
-- Slow
SELECT b.Id, MAX(b.Isbn), MAX(b.Title), MAX(b.Author), MAX(b.Format), MAX(b.ImageUrl), MAX(b.Created), MAX(bp.Id) AS PriceId
FROM Book b
INNER JOIN BookPrice bp ON b.Id = bp.BookId
GROUP BY b.Id
ORDER BY PriceId DESC
LIMIT 8;

-- Faster with temporary table
WITH LatestPriceUpdate AS (
    SELECT bp.BookId, MAX(bp.Id) AS NewestPriceId
    FROM BookPrice bp
    GROUP BY bp.BookId
    ORDER BY NewestPriceId DESC
    LIMIT 8
)

SELECT b.Id, b.Isbn, b.Title, b.Author, b.Format, b.ImageUrl, b.Created
FROM Book b
INNER JOIN LatestPriceUpdate lpu ON b.Id = lpu.BookId;
ORDER BY lpu.NewestPriceId DESC;


-- Get failed update count for bookstores by reason
SELECT fpu.Reason, bs.Id as BookStoreId, MAX(bs.Name) AS BookStore, COUNT(fpu.Id) AS FailedUpdateCount
FROM FailedPriceUpdate fpu
INNER JOIN BookStore bs ON bs.Id = fpu.BookStoreId
GROUP BY bs.Id, fpu.Reason
ORDER BY FailedUpdateCount DESC;


-- Get import count for bookstores
SET @FromDate = '2019-01-01';

SELECT bs.Name as BookStore, COUNT(*) as ImportCount
FROM Book b
INNER JOIN BookStoreBook bsb ON b.Id = bsb.BookId
INNER JOIN BookStore bs ON bsb.BookStoreId = bs.Id
WHERE b.Created >= @FromDate
GROUP BY bsb.BookStoreId
