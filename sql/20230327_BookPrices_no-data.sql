-- MySQL dump 10.13  Distrib 8.0.30, for Linux (aarch64)
--
-- Host: localhost    Database: BookPrices
-- ------------------------------------------------------
-- Server version	8.0.30

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Book`
--

DROP TABLE IF EXISTS `Book`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Book` (
  `Id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `Isbn` varchar(13) NOT NULL DEFAULT '',
  `Title` varchar(255) NOT NULL,
  `Author` varchar(255) NOT NULL,
  `ImageUrl` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `Title` (`Title`),
  KEY `Author` (`Author`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `BookPrice`
--

DROP TABLE IF EXISTS `BookPrice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BookPrice` (
  `Id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `BookId` mediumint unsigned DEFAULT NULL,
  `BookStoreId` mediumint unsigned DEFAULT NULL,
  `Price` float(10,2) NOT NULL,
  `Created` datetime NOT NULL,
  PRIMARY KEY (`Id`),
  KEY `BookId` (`BookId`),
  KEY `BookStoreId` (`BookStoreId`),
  KEY `Created` (`Created`),
  CONSTRAINT `BookPrice_ibfk_1` FOREIGN KEY (`BookId`) REFERENCES `Book` (`Id`) ON DELETE CASCADE,
  CONSTRAINT `BookPrice_ibfk_2` FOREIGN KEY (`BookStoreId`) REFERENCES `BookStore` (`Id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21749 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `BookStore`
--

DROP TABLE IF EXISTS `BookStore`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BookStore` (
  `Id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) NOT NULL,
  `Url` varchar(255) NOT NULL,
  `SearchUrl` varchar(255) DEFAULT NULL,
  `SearchResultCssSelector` varchar(255) DEFAULT NULL,
  `PriceCssSelector` varchar(255) DEFAULT NULL,
  `ImageCssSelector` varchar(255) DEFAULT NULL,
  `PriceFormat` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `BookStoreBook`
--

DROP TABLE IF EXISTS `BookStoreBook`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BookStoreBook` (
  `BookId` mediumint unsigned NOT NULL,
  `BookStoreId` mediumint unsigned NOT NULL,
  `Url` varchar(255) NOT NULL,
  PRIMARY KEY (`BookId`,`BookStoreId`),
  KEY `BookStoreId` (`BookStoreId`),
  CONSTRAINT `BookStoreBook_ibfk_1` FOREIGN KEY (`BookId`) REFERENCES `Book` (`Id`) ON DELETE CASCADE,
  CONSTRAINT `BookStoreBook_ibfk_2` FOREIGN KEY (`BookStoreId`) REFERENCES `BookStore` (`Id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `BookStoreSitemap`
--

DROP TABLE IF EXISTS `BookStoreSitemap`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BookStoreSitemap` (
  `Id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `BookStoreId` mediumint unsigned NOT NULL,
  `Url` varchar(255) NOT NULL,
  PRIMARY KEY (`Id`),
  KEY `BookStoreId` (`BookStoreId`),
  CONSTRAINT `BookStoreSitemap_ibfk_1` FOREIGN KEY (`BookStoreId`) REFERENCES `BookStore` (`Id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-03-27 16:46:56
