-- MySQL dump 10.13  Distrib 8.4.7, for Linux (x86_64)
--
-- Host: localhost    Database: BookPrices
-- ------------------------------------------------------
-- Server version	8.4.7

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
-- Table structure for table `ApiKey`
--

DROP TABLE IF EXISTS `ApiKey`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ApiKey` (
  `Id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `ApiName` varchar(255) NOT NULL,
  `ApiUser` varchar(255) NOT NULL,
  `ApiKey` varchar(1024) NOT NULL,
  `updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

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
  `Format` varchar(255) NOT NULL DEFAULT '',
  `ImageUrl` varchar(255) DEFAULT NULL,
  `Created` datetime NOT NULL DEFAULT '0001-01-01 00:00:00',
  PRIMARY KEY (`Id`),
  UNIQUE KEY `Isbn` (`Isbn`),
  KEY `Title` (`Title`),
  KEY `Author` (`Author`)
) ENGINE=InnoDB AUTO_INCREMENT=6766 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `BookList`
--

DROP TABLE IF EXISTS `BookList`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BookList` (
  `Id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `UserId` char(36) NOT NULL,
  `Name` varchar(255) NOT NULL,
  `Description` varchar(512) DEFAULT NULL,
  `Created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`Id`),
  KEY `UserId` (`UserId`),
  CONSTRAINT `BookList_ibfk_1` FOREIGN KEY (`UserId`) REFERENCES `User` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `BookListBook`
--

DROP TABLE IF EXISTS `BookListBook`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BookListBook` (
  `BookListId` mediumint unsigned NOT NULL,
  `BookId` mediumint unsigned NOT NULL,
  `Created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`BookListId`,`BookId`),
  KEY `BookId` (`BookId`),
  CONSTRAINT `BookListBook_ibfk_1` FOREIGN KEY (`BookListId`) REFERENCES `BookList` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `BookListBook_ibfk_2` FOREIGN KEY (`BookId`) REFERENCES `Book` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=339017 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
  `IsbnCssSelector` varchar(255) DEFAULT NULL,
  `PriceFormat` varchar(80) DEFAULT NULL,
  `ColorHex` char(6) DEFAULT NULL,
  `ScraperId` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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

--
-- Table structure for table `FailedPriceUpdate`
--

DROP TABLE IF EXISTS `FailedPriceUpdate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FailedPriceUpdate` (
  `Id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `BookId` mediumint unsigned NOT NULL,
  `BookStoreId` mediumint unsigned NOT NULL,
  `Reason` varchar(100) NOT NULL,
  `Created` datetime NOT NULL,
  PRIMARY KEY (`Id`),
  KEY `PriceUpdateFailed_ibfk_1` (`BookId`),
  KEY `PriceUpdateFailed_ibfk_2` (`BookStoreId`),
  KEY `Created` (`Created`),
  CONSTRAINT `PriceUpdateFailed_ibfk_1` FOREIGN KEY (`BookId`) REFERENCES `Book` (`Id`) ON DELETE CASCADE,
  CONSTRAINT `PriceUpdateFailed_ibfk_2` FOREIGN KEY (`BookStoreId`) REFERENCES `BookStore` (`Id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=58934 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `User`
--

DROP TABLE IF EXISTS `User`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `User` (
  `Id` char(36) NOT NULL,
  `Email` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `FirstName` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `LastName` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `IsActive` bit(1) NOT NULL,
  `GoogleApiToken` varchar(512) NOT NULL,
  `Created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `ImageUrl` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `AccessLevel` tinyint unsigned NOT NULL DEFAULT '1',
  `BookListId` mediumint unsigned DEFAULT NULL,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `Email` (`Email`),
  KEY `User_FK_BookList` (`BookListId`),
  CONSTRAINT `User_FK_BookList` FOREIGN KEY (`BookListId`) REFERENCES `BookList` (`Id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-18 16:09:05
