-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: virtualpet
-- ------------------------------------------------------
-- Server version	8.0.44

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
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('e4e858e5f6cf');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `parent_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`),
  KEY `parent_id` (`parent_id`),
  CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Alimentos','Alimentos secos, húmedos y snacks para todo tipo de mascotas',NULL),(2,'Juguetes','Juguetes interactivos y de entretenimiento',NULL),(3,'Accesorios','Collares, correas, ropa y complementos',NULL),(4,'Higiene','Shampoos, cepillos y productos de cuidado',NULL),(5,'Vivienda','Cuchas, camas, jaulas y transportines',NULL),(6,'Salud','Vitaminas, suplementos y antiparasitarios',NULL),(7,'Alimentos para perros','Croquetas y húmedos para perros',1),(8,'Alimentos para gatos','Croquetas y húmedos para gatos',1),(9,'Alimentos para peces','Escamas, pellets y alimentos acuáticos',1),(10,'Alimentos para aves','Semillas y mezclas para pájaros',1),(11,'Cuchas y camas','Descanso cómodo para perros y gatos',5),(12,'Jaulas y acuarios','Hábitats para aves, roedores y peces',5);
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `product_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `precio_unitario` float NOT NULL,
  `subtotal` float NOT NULL,
  `producto_nombre` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` VALUES (1,1,1,1,28500,28500,NULL),(2,3,1,1,28500,28500,NULL),(3,4,2,1,32000,32000,NULL),(4,5,3,1,18900,18900,NULL),(5,6,4,1,9800,9800,NULL),(6,7,5,1,14500,14500,NULL),(7,8,1,1,28500,28500,NULL),(8,9,2,1,32000,32000,NULL),(9,10,3,1,18900,18900,NULL),(10,11,4,1,9800,9800,NULL),(11,12,5,1,14500,14500,NULL),(12,17,2,1,32000,32000,'Eukanuba Adult Large Breed 14kg'),(13,17,7,1,11400,11400,'Hills Science Diet Gatito 1.6kg'),(14,18,6,1,16200,16200,'Royal Canin Indoor 7 4kg'),(15,18,9,1,4200,4200,'Sera Vipan Nature 1000ml'),(16,19,2,1,32000,32000,'Eukanuba Adult Large Breed 14kg'),(17,20,6,1,16200,16200,'Royal Canin Indoor 7 4kg'),(18,21,7,2,11400,22800,'Hills Science Diet Gatito 1.6kg'),(19,21,8,1,2800,2800,'Tetra Goldfish Granules 250ml'),(20,21,9,1,4200,4200,'Sera Vipan Nature 1000ml'),(21,22,20,1,35000,35000,'Acuario completo kit 60 litros'),(22,23,19,1,7500,7500,'Cama redonda antideslizante para mascotas'),(23,24,14,1,8900,8900,'Correa retráctil Flexi Classic 5m Talla L'),(24,25,21,1,9200,9200,'Frontline Combo perros 10-20kg x3 pipetas'),(25,26,3,1,18900,18900,'Pedigree Adultos Carne y Verduras 21kg'),(26,27,13,1,2400,2400,'Pelota tenis para perros pack x3'),(27,28,20,1,35000,35000,'Acuario completo kit 60 litros'),(28,29,17,1,2100,2100,'Cepillo de cerdas dobles para gatos'),(29,29,19,1,7500,7500,'Cama redonda antideslizante para mascotas'),(30,30,17,1,2100,2100,'Cepillo de cerdas dobles para gatos'),(31,31,20,1,35000,35000,'Acuario completo kit 60 litros'),(32,31,19,1,7500,7500,'Cama redonda antideslizante para mascotas'),(33,31,17,1,2100,2100,'Cepillo de cerdas dobles para gatos');
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `estado` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `total` float NOT NULL,
  `direccion_entrega` varchar(300) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,3,'preparado',28500,'Calle falsa','2026-05-19 13:46:58','2026-05-20 13:53:37'),(3,3,'pendiente',28500,'Av. Colón 1234, Mar del Plata','2026-05-20 14:00:00','2026-05-20 14:00:00'),(4,3,'pendiente',32000,'Guemes 2500, Mar del Plata','2026-05-20 14:00:00','2026-05-20 14:00:00'),(5,3,'preparado',18900,'San Juan 500, Mar del Plata','2026-05-20 14:00:00','2026-05-20 14:00:00'),(6,3,'pendiente',9800,'Alvarado 3200, Mar del Plata','2026-05-20 14:00:00','2026-05-20 14:00:25'),(7,3,'entregado',14500,'Rivadavia 150, Mar del Plata','2026-05-20 14:00:00','2026-05-25 18:39:07'),(8,3,'pendiente',28500,'Av. Colón 1234, Mar del Plata','2026-05-20 14:05:09','2026-05-20 14:05:09'),(9,3,'pendiente',32000,'Guemes 2500, Mar del Plata','2026-05-20 14:05:09','2026-05-20 14:05:09'),(10,3,'en_preparacion',18900,'San Juan 500, Mar del Plata','2026-05-20 14:05:09','2026-05-25 18:47:07'),(11,3,'entregado',9800,'Alvarado 3200, Mar del Plata','2026-05-20 14:05:09','2026-05-25 18:48:56'),(12,3,'entregado',14500,'Rivadavia 150, Mar del Plata','2026-05-20 14:05:09','2026-05-25 18:39:07'),(17,4,'pendiente',43400,'Falucho 23423','2026-05-20 14:12:21','2026-05-20 14:12:21'),(18,4,'pendiente',20400,'Calle 32 nro 3835','2026-05-20 19:47:40','2026-05-20 19:50:57'),(19,5,'pendiente',32000,'Calle 32 nro 3835','2026-05-20 19:50:28','2026-05-20 19:50:28'),(20,5,'pendiente',16200,'jskjflksdfj','2026-05-20 20:04:11','2026-05-20 20:04:11'),(21,3,'pendiente',29800,'vdskmvkjsdnvkjsdf','2026-05-22 09:27:40','2026-05-22 09:27:40'),(22,3,'pendiente',35000,'jujuuuuuuuuuuuuuuuuuuuuu','2026-05-22 09:29:44','2026-05-22 09:29:44'),(23,3,'pendiente',7500,'comprar comprarrrr','2026-05-22 09:32:03','2026-05-22 09:32:03'),(24,3,'pendiente',8900,'comprar comprarrrr','2026-05-22 09:34:33','2026-05-22 09:34:33'),(25,3,'pendiente',9200,'comprar comprarrrr','2026-05-22 09:37:21','2026-05-22 09:37:21'),(26,3,'pendiente',18900,'comprar comprarrrr','2026-05-22 09:39:31','2026-05-22 09:39:31'),(27,3,'pendiente',2400,'comprar comprarrrr','2026-05-22 09:41:11','2026-05-22 09:41:11'),(28,3,'entregado',35000,'holaaaaaaa','2026-05-22 09:57:54','2026-05-25 18:39:07'),(29,3,'entregado',9600,'oihefiasdhf','2026-05-22 10:05:28','2026-05-25 18:48:44'),(30,3,'pendiente',2100,'sdfgsdfhgh','2026-05-25 18:58:06','2026-05-25 18:58:06'),(31,3,'pendiente',44600,'Calle re falsa ','2026-05-26 22:26:54','2026-05-26 22:26:54');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `orden_id` int NOT NULL,
  `monto` float NOT NULL,
  `estado` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `metodo` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `referencia_externa` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `orden_id` (`orden_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`orden_id`) REFERENCES `orders` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
INSERT INTO `payments` VALUES (1,1,28500,'aprobado','simulado',NULL,'2026-05-19 13:46:58'),(2,17,43400,'aprobado','simulado',NULL,'2026-05-20 14:12:21'),(3,18,20400,'aprobado','simulado',NULL,'2026-05-20 19:47:40'),(4,19,32000,'aprobado','simulado',NULL,'2026-05-20 19:50:28'),(5,20,16200,'aprobado','simulado',NULL,'2026-05-20 20:04:11'),(6,21,29800,'aprobado','simulado',NULL,'2026-05-22 09:27:40'),(7,22,35000,'aprobado','simulado',NULL,'2026-05-22 09:29:44'),(8,23,7500,'aprobado','simulado',NULL,'2026-05-22 09:32:03'),(9,24,8900,'aprobado','simulado',NULL,'2026-05-22 09:34:34'),(10,25,9200,'aprobado','simulado',NULL,'2026-05-22 09:37:21'),(11,26,18900,'aprobado','simulado',NULL,'2026-05-22 09:39:31'),(12,27,2400,'aprobado','simulado',NULL,'2026-05-22 09:41:11'),(13,28,35000,'aprobado','simulado',NULL,'2026-05-22 09:57:54'),(14,29,9600,'aprobado','simulado',NULL,'2026-05-22 10:05:28'),(15,30,2100,'aprobado','simulado',NULL,'2026-05-25 18:58:06'),(16,31,44600,'aprobado','simulado',NULL,'2026-05-26 22:26:54');
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci,
  `precio` float NOT NULL,
  `imagen_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `category_id` int DEFAULT NULL,
  `activo` tinyint(1) NOT NULL,
  `erp_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `erp_id` (`erp_id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,'Royal Canin Medium Adult 15kg','Alimento completo para perros adultos de raza mediana. Formulado para mantener el peso ideal y la salud digestiva.',28500,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Royal Canin Medium Adult 15kg.jpg',7,1,'ERP-001','2026-05-19 13:41:11','2026-05-26 23:03:38'),(2,'Eukanuba Adult Large Breed 14kg','Croquetas para perros adultos de raza grande. Rica en proteínas de pollo para mantener la masa muscular.',32000,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Eukanuba Adult Large Breed 14kg.jpg',7,1,'ERP-002','2026-05-19 13:41:11','2026-05-26 23:03:38'),(3,'Pedigree Adultos Carne y Verduras 21kg','Alimento balanceado con carne y vegetales. Ideal para perros adultos de todas las razas.',18900,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Pedigree Adultos Carne y Verduras 21kg.jpg',7,1,'ERP-003','2026-05-19 13:41:11','2026-05-26 23:03:38'),(4,'Purina Pro Plan Cachorro 3kg','Fórmula especial para cachorros con DHA para el desarrollo cerebral. Proteína de pollo como primer ingrediente.',9800,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Purina Pro Plan Cachorro 3kg.jpg',7,1,'ERP-004','2026-05-19 13:41:11','2026-05-26 23:03:38'),(5,'Whiskas Adultos Pollo y Conejo 10kg','Croquetas para gatos adultos con sabor a pollo y conejo. Enriquecidas con taurina para la salud cardiovascular.',14500,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Whiskas Adultos Pollo y Conejo 10kg.jpg',8,1,'ERP-005','2026-05-19 13:41:11','2026-05-26 23:03:38'),(6,'Royal Canin Indoor 7 4kg','Especial para gatos de interior. Controla la formación de bolas de pelo y mantiene el peso ideal.',16200,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Royal Canin Indoor 7 4kg.jpg',8,1,'ERP-006','2026-05-19 13:41:11','2026-05-26 23:03:38'),(7,'Hills Science Diet Gatito 1.6kg','Alimento premium para gatitos hasta 12 meses. Nutrición precisa para un desarrollo saludable.',11400,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Hills Science Diet Gatito 1.6kg.png',8,1,'ERP-007','2026-05-19 13:41:11','2026-05-26 23:03:38'),(8,'Tetra Goldfish Granules 250ml','Gránulos flotantes para peces dorados y carpas koi. Fórmula especial para reducir la contaminación del agua.',2800,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Tetra Goldfish Granules 250ml.jpg',9,1,'ERP-008','2026-05-19 13:41:11','2026-05-26 23:03:38'),(9,'Sera Vipan Nature 1000ml','Escamas naturales para peces tropicales. Sin colorantes artificiales, ingredientes 100% naturales.',4200,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Sera Vipan Nature 1000ml.jpg',9,1,'ERP-009','2026-05-19 13:41:11','2026-05-26 23:03:38'),(10,'Vitakraft Menu Vital Canarios 1kg','Mezcla de semillas seleccionadas para canarios. Enriquecida con vitaminas y minerales esenciales.',3500,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Vitakraft Menu Vital Canarios 1kg.jpg',10,1,'ERP-010','2026-05-19 13:41:11','2026-05-26 23:03:38'),(11,'Kong Classic Rojo Talla M','Juguete resistente de goma natural para perros. Se puede rellenar con premios para estimulación mental.',6800,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Kong Classic Rojo Talla M.jpg',2,1,'ERP-011','2026-05-19 13:41:11','2026-05-26 23:03:38'),(12,'Pluma interactiva para gatos con luz LED','Varita con plumas naturales y puntero láser integrado. Estimula el instinto cazador del gato.',1900,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Pluma interactiva para gatos con luz LED.jpg',2,1,'ERP-012','2026-05-19 13:41:11','2026-05-26 23:03:38'),(13,'Pelota tenis para perros pack x3','Pelotas de tenis resistentes al mordido. Tamaño estándar, aptas para lanzadores automáticos.',2400,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Pelota tenis para perros pack x3.jpg',2,1,'ERP-013','2026-05-19 13:41:11','2026-05-26 23:03:38'),(14,'Correa retráctil Flexi Classic 5m Talla L','Correa extensible hasta 5 metros para perros de hasta 50kg. Sistema de freno y bloqueo de seguridad.',8900,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Correa retráctil Flexi Classic 5m Talla L.jpg',3,1,'ERP-014','2026-05-19 13:41:11','2026-05-26 23:03:38'),(15,'Collar antipulgas Seresto perros grandes','Collar antiparasitario de larga duración (hasta 8 meses). Repele pulgas, garrapatas y mosquitos.',12500,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Collar antipulgas Seresto perros grandes.jpg',3,1,'ERP-015','2026-05-19 13:41:11','2026-05-26 23:03:38'),(16,'Shampoo Pelo de Oro Perros Pelaje Oscuro 500ml','Shampoo específico para perros de pelaje oscuro. Realza el brillo y suaviza el pelo sin resecar.',3200,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Shampoo Pelo de Oro Perros Pelaje Oscuro 500ml.jpg',4,1,'ERP-016','2026-05-19 13:41:11','2026-05-26 23:03:38'),(17,'Cepillo de cerdas dobles para gatos','Doble cara: cerdas metálicas para desenredar y cerdas suaves para pulir el pelaje.',2100,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Cepillo de cerdas dobles para gatos.jpg',4,1,'ERP-017','2026-05-19 13:41:11','2026-05-26 23:03:38'),(18,'Cucha de madera para perros medianos','Cucha de pino tratado para exterior e interior. Techo desmontable para fácil limpieza. 70x60x65cm.',24000,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Cucha de madera para perros medianos.jpg',11,1,'ERP-018','2026-05-19 13:41:11','2026-05-26 23:03:38'),(19,'Cama redonda antideslizante para mascotas','Cama acolchada 60cm de diámetro. Relleno de espuma de alta densidad, base antideslizante. Lavable.',7500,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Cama redonda antideslizante para mascotas.jpg',11,1,'ERP-019','2026-05-19 13:41:11','2026-05-26 23:03:38'),(20,'Acuario completo kit 60 litros','Kit completo con filtro, iluminación LED y calefactor. Listo para usar. Incluye manual de inicio.',35000,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Acuario completo kit 60 litros.jpg',12,1,'ERP-020','2026-05-19 13:41:11','2026-05-26 23:03:38'),(21,'Frontline Combo perros 10-20kg x3 pipetas','Antiparasitario externo spot-on. Elimina pulgas, garrapatas y piojos. Efecto residual 4 semanas.',9200,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Frontline Combo perros 10-20kg x3 pipetas.jpg',6,1,'ERP-021','2026-05-19 13:41:11','2026-05-26 23:03:38'),(22,'Suplemento articular Condro Plus para perros 60 comp','Condroitina y glucosamina para la salud articular. Ideal para perros mayores o razas grandes.',6700,'https://virtual-pet-assets.s3.us-east-2.amazonaws.com/products/Suplemento articular Condro Plus para perros 60 comp.jpg',6,1,'ERP-022','2026-05-19 13:41:11','2026-05-26 23:03:38');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stock`
--

DROP TABLE IF EXISTS `stock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stock` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `product_id` (`product_id`),
  CONSTRAINT `stock_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock`
--

LOCK TABLES `stock` WRITE;
/*!40000 ALTER TABLE `stock` DISABLE KEYS */;
INSERT INTO `stock` VALUES (1,1,44,'2026-05-19 13:46:58'),(2,2,28,'2026-05-20 19:50:28'),(3,3,59,'2026-05-22 09:39:31'),(4,4,25,'2026-05-19 13:41:11'),(5,5,40,'2026-05-19 13:41:11'),(6,6,18,'2026-05-20 20:04:11'),(7,7,12,'2026-05-22 09:27:40'),(8,8,79,'2026-05-22 09:27:40'),(9,9,48,'2026-05-22 09:27:40'),(10,10,35,'2026-05-19 13:41:11'),(11,11,40,'2026-05-19 13:41:11'),(12,12,55,'2026-05-19 13:41:11'),(13,13,69,'2026-05-22 09:41:11'),(14,14,21,'2026-05-22 09:34:34'),(15,15,18,'2026-05-19 13:41:11'),(16,16,30,'2026-05-19 13:41:11'),(17,17,42,'2026-05-26 22:26:54'),(18,18,10,'2026-05-19 13:41:11'),(19,19,25,'2026-05-26 22:26:54'),(20,20,2,'2026-05-26 22:26:54'),(21,21,32,'2026-05-22 09:37:21'),(22,22,20,'2026-05-19 13:41:11');
/*!40000 ALTER TABLE `stock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `apellido` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` enum('CLIENTE','DEPOSITO','ADMIN') COLLATE utf8mb4_unicode_ci NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Admin','Virtual Pet','admin@virtualpet.com.ar','$2b$12$HalZf7rqLJrthiTl7UYtRuRwdP5twH0LGesNm1Ot001BicqfhGoCO','ADMIN',1,'2026-05-19 13:41:11','2026-05-19 13:41:11'),(2,'Juan','Depósito','deposito@virtualpet.com.ar','$2b$12$wOjEUen2S.MpWe1Ggm0ADeubPG9tZcW.3mXKF4P4xMRqc/JySRosu','DEPOSITO',1,'2026-05-19 13:41:11','2026-05-19 13:41:11'),(3,'María','González','cliente@test.com','$2b$12$tpLHDPgHtU6A8lus0XOEwOpSU4eJDD.1XpRKdAqF/tMKpucLMVE5i','CLIENTE',1,'2026-05-19 13:41:11','2026-05-19 13:41:11'),(4,'Laura','Stadler','stadlerlaum@gmail.com','$2b$12$QLt6I2WQrcA8wLq/kOUoMuudOm4cFZAOJZBtfvMgolLfyR5qynvlO','CLIENTE',1,'2026-05-20 12:24:23','2026-05-20 12:24:23'),(5,'Nico','Kar','karstadler97@gmail.com','$2b$12$zEaG2AdiS6DfCpJgcMbl4uyfJCZ4XpUjyAnxa75mPVoOvlh62mBxG','CLIENTE',1,'2026-05-20 19:50:01','2026-05-20 19:50:01');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-26 23:13:05
