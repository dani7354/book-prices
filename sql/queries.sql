 -- Get the 100 latest failed price updates
 select fpu.Created, fpu.Reason, b.Title, CONCAT(bs.Url, bsb.Url) as Url, bs.Id as BookStoreId, b.Id as BookId
 from FailedPriceUpdate fpu
 inner join Book b on b.Id = fpu.BookId
 inner join BookStore bs on bs.Id = fpu.BookStoreId
 inner join BookStoreBook bsb on bsb.BookId = fpu.BookId and bsb.BookStoreId = fpu.BookStoreId
 order by fpu.created DESC limit 100;


-- Get the 100 latest price updates
SELECT b.Id, b.Isbn, b.Title, b.Author, b.Format, b.ImageUrl, b.Created, MAX(bp.Created) as PriceUpdated
FROM Book b
JOIN BookPrice bp ON b.Id = bp.BookId
GROUP BY b.Id, b.Isbn, b.Title, b.Author, b.Format, b.ImageUrl, b.Created
ORDER BY PriceUpdated DESC
LIMIT 100;