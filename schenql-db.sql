-- MySQL Script generated by MySQL Workbench
-- Sat Mar 30 16:27:17 2019
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema schenql-db
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `schenql-db` ;

-- -----------------------------------------------------
-- Schema schenql-db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `schenql-db` DEFAULT CHARACTER SET utf8 ;
USE `schenql-db` ;

-- -----------------------------------------------------
-- Table `schenql-db`.`person`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`person` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`person` (
  `dblpKey` VARCHAR(50) NOT NULL,
  `orcid` VARCHAR(20) NULL,
  `h-index` INT NULL,
  PRIMARY KEY (`dblpKey`))
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `schenql-db`.`person_names`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`person_names` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`person_names` (
  `name` VARCHAR(200) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `personKey` VARCHAR(200) NULL,
  PRIMARY KEY (`name`),
  INDEX `fk_personKey_idx` (`personKey` ASC),
  CONSTRAINT `fk_personKey`
    FOREIGN KEY (`personKey`)
    REFERENCES `schenql-db`.`person` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `schenql-db`.`continent`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`continent` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`continent` (
  `id` INT NOT NULL,
  `name` VARCHAR(45) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `schenql-db`.`country`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`country` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`country` (
  `id` INT NOT NULL,
  `name` VARCHAR(45) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `schenql-db`.`city`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`city` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`city` (
  `id` INT NOT NULL,
  `name` VARCHAR(45) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `schenql-db`.`state`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`state` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`state` (
  `id` INT NOT NULL,
  `name` VARCHAR(45) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `schenql-db`.`conference`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`conference` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`conference` (
  `dblpKey` VARCHAR(50) NOT NULL,
  `acronym` VARCHAR(10) NULL,
  `corerank` VARCHAR(3) NULL,
  `continent_id` INT NOT NULL,
  `country_id` INT NOT NULL,
  `state_id` INT NOT NULL,
  `city_id` INT NOT NULL,
  PRIMARY KEY (`dblpKey`),
  INDEX `fk_conference_continent_idx` (`continent_id` ASC),
  INDEX `fk_conference_country_idx` (`country_id` ASC),
  INDEX `fk_conference_city_idx` (`city_id` ASC),
  INDEX `fk_conference_state_idx` (`state_id` ASC),
  CONSTRAINT `fk_conference_continent`
    FOREIGN KEY (`continent_id`)
    REFERENCES `schenql-db`.`continent` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_conference_country`
    FOREIGN KEY (`country_id`)
    REFERENCES `schenql-db`.`country` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_conference_city`
    FOREIGN KEY (`city_id`)
    REFERENCES `schenql-db`.`city` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_conference_state`
    FOREIGN KEY (`state_id`)
    REFERENCES `schenql-db`.`state` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `schenql-db`.`journal`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`journal` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`journal` (
  `dblpKey` VARCHAR(50) NOT NULL,
  `acronym` VARCHAR(10) NULL,
  `volume` VARCHAR(10) NULL,
  PRIMARY KEY (`dblpKey`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `schenql-db`.`journal_name`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`journal_name` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`journal_name` (
  `name`VARCHAR(200) NULL,
  `journalKey` VARCHAR(50) NULL,
  PRIMARY KEY (`name`),
  INDEX `fk_journalKey_idx` (`journalKey`ASC),
  CONSTRAINT `fk_journalKey`
    FOREIGN KEY (`journalKey`)
    REFERENCES `schenql-db`.`journal` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `schenql-db`.`publication`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`publication` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`publication` (
  `dblpKey` VARCHAR(50) NOT NULL,
  `title` VARCHAR(200) NULL,
  `ee` VARCHAR(200) NULL,
  `url` VARCHAR(255) NULL,
  `year` INT NULL,
  `volume` VARCHAR(50) NULL,
  `conference_dblpKey` VARCHAR(50) NULL,
  `journal_dblpKey` VARCHAR(50) NULL,
  PRIMARY KEY (`dblpKey`),
  INDEX `fk_publication_conference_idx` (`conference_dblpKey` ASC),
  INDEX `fk_publication_journal_idx` (`journal_dblpKey` ASC),
  CONSTRAINT `fk_publication_conference`
    FOREIGN KEY (`conference_dblpKey`)
    REFERENCES `schenql-db`.`conference` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_publication_journal`
    FOREIGN KEY (`journal_dblpKey`)
    REFERENCES `schenql-db`.`journal` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `schenql-db`.`keyword`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`keyword` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`keyword` (
  `keyword` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`keyword`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `schenql-db`.`publication_has_keyword`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`publication_has_keyword` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`publication_has_keyword` (
  `dblpKey` VARCHAR(50) NOT NULL,
  `keyword` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`dblpKey`, `keyword`),
  INDEX `fk_publication_has_keyword_keyword_idx` (`keyword` ASC),
  INDEX `fk_publication_has_keyword_publication_idx` (`dblpKey` ASC),
  CONSTRAINT `fk_publication_has_keyword_publication`
    FOREIGN KEY (`dblpKey`)
    REFERENCES `schenql-db`.`publication` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_publication_has_keyword_keyword`
    FOREIGN KEY (`keyword`)
    REFERENCES `schenql-db`.`keyword` (`keyword`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `schenql-db`.`person_authored_publication`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`person_authored_publication` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`person_authored_publication` (
  `personKey` VARCHAR(50) NOT NULL,
  `publicationKey` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`personKey`, `publicationKey`),
  INDEX `fk_person_authored_publication_publication_idx` (`publicationKey` ASC),
  INDEX `fk_person_authored_publication_person_idx` (`personKey` ASC),
  CONSTRAINT `fk_person_authored_publication_person`
    FOREIGN KEY (`personKey`)
    REFERENCES `schenql-db`.`person` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_person_authored_publication_publication`
    FOREIGN KEY (`publicationKey`)
    REFERENCES `schenql-db`.`publication` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `schenql-db`.`person_edited_publication`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`person_edited_publication` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`person_edited_publication` (
  `personKey` VARCHAR(50) NOT NULL,
  `publicationKey` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`personKey`, `publicationKey`),
  INDEX `fk_person_edited_publication_publication_idx` (`publicationKey` ASC),
  INDEX `fk_person_edited_publication_person_idx` (`personKey` ASC),
  CONSTRAINT `fk_person_edited_publication_person`
    FOREIGN KEY (`personKey`)
    REFERENCES `schenql-db`.`person` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_person_edited_publication_publication`
    FOREIGN KEY (`publicationKey`)
    REFERENCES `schenql-db`.`publication` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `schenql-db`.`person_reviewed_publication`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`person_reviewed_publication` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`person_reviewed_publication` (
  `personKey` VARCHAR(50) NOT NULL,
  `publicationKey` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`personKey`, `publicationKey`),
  INDEX `fk_person_reviewed_publication_publication_idx` (`publicationKey` ASC),
  INDEX `fk_person_reviewed_publication_person_idx` (`personKey` ASC),
  CONSTRAINT `fk_person_reviewed_publication_person`
    FOREIGN KEY (`personKey`)
    REFERENCES `schenql-db`.`person` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_person_reviewed_publication_publication`
    FOREIGN KEY (`publicationKey`)
    REFERENCES `schenql-db`.`publication` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `schenql-db`.`instituion`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`instituion` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`instituion` (
  `key` VARCHAR(50) NOT NULL,
  `name` VARCHAR(100) NULL,
  `type` ENUM('eins', 'zwei') NULL,
  `continent_id` INT NOT NULL,
  `country_id` INT NOT NULL,
  `state_id` INT NOT NULL,
  `city_id` INT NOT NULL,
  PRIMARY KEY (`key`),
  INDEX `fk_instituion_state_idx` (`state_id` ASC),
  INDEX `fk_instituion_city_idx` (`city_id` ASC),
  INDEX `fk_instituion_country_idx` (`country_id` ASC),
  INDEX `fk_instituion_continent_idx` (`continent_id` ASC),
  CONSTRAINT `fk_instituion_state`
    FOREIGN KEY (`state_id`)
    REFERENCES `schenql-db`.`state` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_instituion_city`
    FOREIGN KEY (`city_id`)
    REFERENCES `schenql-db`.`city` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_instituion_country`
    FOREIGN KEY (`country_id`)
    REFERENCES `schenql-db`.`country` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_instituion_continent`
    FOREIGN KEY (`continent_id`)
    REFERENCES `schenql-db`.`continent` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `schenql-db`.`publication_cites`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`publication_cites` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`publication_cites` (
  `pub_id` VARCHAR(50) NOT NULL,
  `pub2_id` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`pub_id`, `pub2_id`),
  INDEX `fk_publication_cites_pub2_idx` (`pub2_id` ASC),
  INDEX `fk_publication_cites_pub_idx` (`pub_id` ASC),
  CONSTRAINT `fk_publication_cites_pub1`
    FOREIGN KEY (`pub_id`)
    REFERENCES `schenql-db`.`publication` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_publication_cites_pub2`
    FOREIGN KEY (`pub2_id`)
    REFERENCES `schenql-db`.`publication` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `schenql-db`.`publication_references`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`publication_references` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`publication_references` (
  `pub_id` VARCHAR(50) NOT NULL,
  `pub2_id` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`pub_id`, `pub2_id`),
  INDEX `fk_publication_references_pub2_idx` (`pub2_id` ASC),
  INDEX `fk_publication_references_pub_idx` (`pub_id` ASC),
  CONSTRAINT `fk_publication_pub1`
    FOREIGN KEY (`pub_id`)
    REFERENCES `schenql-db`.`publication` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_publication_pub2`
    FOREIGN KEY (`pub2_id`)
    REFERENCES `schenql-db`.`publication` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `schenql-db`.`person_works_for_instituion`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`person_works_for_instituion` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`person_works_for_instituion` (
  `person_dblpKey` VARCHAR(50) NOT NULL,
  `instituion_key` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`person_dblpKey`, `instituion_key`),
  INDEX `fk_person_works_for_instituion_instituion_idx` (`instituion_key` ASC),
  INDEX `fk_person_works_for_instituion_person_idx` (`person_dblpKey` ASC),
  CONSTRAINT `fk_person_has_instituion_person`
    FOREIGN KEY (`person_dblpKey`)
    REFERENCES `schenql-db`.`person` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_person_has_instituion_instituion`
    FOREIGN KEY (`instituion_key`)
    REFERENCES `schenql-db`.`instituion` (`key`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
