CREATE DATABASE IF NOT EXISTS facebook;
USE facebook;

CREATE TABLE IF NOT EXISTS `profile` (
  `username` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL,
  `about` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `no_of_followers` bigint(20) DEFAULT NULL,
  `no_of_likes` bigint(20) DEFAULT NULL,
  `category` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `log` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_inserted` datetime DEFAULT NULL,
  `date_updated` datetime DEFAULT NULL,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci

CREATE TABLE IF NOT EXISTS `post` (
  `id` bigint(20) NOT NULL,
  `username` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_posted` datetime DEFAULT NULL,
  `caption` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `no_of_likes` bigint(20) DEFAULT NULL,
  `no_of_views` bigint(20) DEFAULT NULL,
  `is_video` tinyint(1) DEFAULT NULL,
  `media_path` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_inserted` datetime DEFAULT NULL,
  `date_updated` datetime DEFAULT NULL,
  `status` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `log` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci

CREATE TABLE `product` (
  `id` bigint(20) NOT NULL,
  `username` varchar(256) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `price` double DEFAULT NULL,
  `currency` varchar(32) DEFAULT NULL,
  `media_path` varchar(256) DEFAULT NULL,
  `status` varchar(256) DEFAULT NULL,
  `log` text DEFAULT NULL,
  `date_inserted` datetime DEFAULT NULL,
  `date_updated` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1