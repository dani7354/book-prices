 -- Get the 100 latest failed price updates
 SELECT fpu.Created, fpu.Reason, b.Title, CONCAT(bs.Url, bsb.Url) AS Url, bs.Id AS BookStoreId, b.Id AS BookId
 FROM FailedPriceUpdate fpu
 INNER JOIN Book b ON b.Id = fpu.BookId
 INNER JOIN BookStore bs ON bs.Id = fpu.BookStoreId
 INNER JOIN BookStoreBook bsb ON bsb.BookId = fpu.BookId AND bsb.BookStoreId = fpu.BookStoreId
 ORDER BY fpu.created DESC
 LIMIT 100;


-- Get the 100 latest price updates
SELECT b.Id, b.Isbn, b.Title, b.Author, b.Format, b.ImageUrl, b.Created, MAX(bp.Created) AS PriceUpdated
FROM Book b
JOIN BookPrice bp ON b.Id = bp.BookId
GROUP BY b.Id, b.Isbn, b.Title, b.Author, b.Format, b.ImageUrl, b.Created
ORDER BY PriceUpdated DESC
LIMIT 100;