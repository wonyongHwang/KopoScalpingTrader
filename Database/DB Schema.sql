CREATE DATABASE  IF NOT EXISTS `kopo_stock` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `kopo_stock`;
-- MySQL dump 10.13  Distrib 8.0.15, for Win64 (x86_64)
--
-- Host: localhost    Database: kopo_stock
-- ------------------------------------------------------
-- Server version	8.0.15

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
 SET NAMES utf8 ;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `observerlist`
--

DROP TABLE IF EXISTS `observerlist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `observerlist` (
  `shcode` varchar(45) NOT NULL,
  `date` varchar(45) DEFAULT NULL,
  `time` varchar(45) DEFAULT NULL,
  `msrate` varchar(45) DEFAULT NULL,
  `bidrem` varchar(45) DEFAULT NULL,
  `offerrem` varchar(45) DEFAULT NULL,
  `price` varchar(45) DEFAULT NULL,
  `bought` varchar(45) DEFAULT NULL,
  `excluded` varchar(45) DEFAULT NULL,
  `reserve1` varchar(45) DEFAULT NULL,
  `reserve2` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `orderlist`
--

DROP TABLE IF EXISTS `orderlist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `orderlist` (
  `shcode` varchar(45) DEFAULT NULL,
  `ordqty` varchar(45) DEFAULT NULL,
  `ordprc` varchar(45) DEFAULT NULL,
  `ordno` varchar(45) DEFAULT NULL,
  `ordtime` varchar(45) DEFAULT NULL,
  `isunm` varchar(45) DEFAULT NULL,
  `reserve1` varchar(45) DEFAULT NULL,
  `reserve2` varchar(45) DEFAULT NULL,
  `orderdate` varchar(45) DEFAULT NULL,
  `bnstpcode` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t1471outblock`
--

DROP TABLE IF EXISTS `t1471outblock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `t1471outblock` (
  `shcode` varchar(45) NOT NULL,
  `date` varchar(45) NOT NULL,
  `time` varchar(45) DEFAULT NULL,
  `price` varchar(45) DEFAULT NULL,
  `sign` varchar(45) DEFAULT NULL,
  `change` varchar(45) DEFAULT NULL,
  `diff` varchar(45) DEFAULT NULL,
  `volume` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='remains by hours';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t1471outblockoccurs`
--

DROP TABLE IF EXISTS `t1471outblockoccurs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `t1471outblockoccurs` (
  `shcode` varchar(45) NOT NULL,
  `date` varchar(45) NOT NULL,
  `time` varchar(45) DEFAULT NULL,
  `preoffercha1` varchar(45) DEFAULT NULL,
  `offerrem1` varchar(45) DEFAULT NULL,
  `offerho1` varchar(45) DEFAULT NULL,
  `bidho1` varchar(45) DEFAULT NULL,
  `bidrem1` varchar(45) DEFAULT NULL,
  `prebidcha1` varchar(45) DEFAULT NULL,
  `totofferrem` varchar(45) DEFAULT NULL,
  `totbidrem` varchar(45) DEFAULT NULL,
  `totsun` varchar(45) DEFAULT NULL,
  `msrate` varchar(45) DEFAULT NULL,
  `close` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-11-10 17:39:03
