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
