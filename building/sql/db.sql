/*
SQLyog Ultimate v12.09 (64 bit)
MySQL - 5.7.20 : Database - shancha_taobao
*********************************************************************
*/


/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`shancha_taobao` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `shancha_taobao`;

/*Table structure for table `auctioning_item` */

DROP TABLE IF EXISTS `auctioning_item`;

CREATE TABLE `auctioning_item` (
  `id` varchar(60) NOT NULL COMMENT '淘宝ID',
  `url` varchar(600) NOT NULL COMMENT '淘宝url',
  `title` varchar(600) NOT NULL COMMENT '淘宝拍卖标题',
  `sell_start` bigint(20) NOT NULL COMMENT '开始拍卖时间',
  `sell_end` bigint(20) NOT NULL COMMENT '结束拍卖时间',
  `type` varchar(2) NOT NULL COMMENT '类型, 01-房产, 02-债权',
  `state` varchar(2) NOT NULL COMMENT '状态, 00-未生成报告, 01-已生成报告',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
