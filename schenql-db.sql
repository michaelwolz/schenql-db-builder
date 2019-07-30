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
CREATE SCHEMA IF NOT EXISTS `schenql-db` DEFAULT CHARACTER SET utf8mb4;
USE `schenql-db` ;


-- -----------------------------------------------------
-- Table `schenql-db`.`person`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`person` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`person` (
  `dblpKey` VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
  `primaryName` VARCHAR(200) NULL,
  `orcid` VARCHAR(20) NULL,
  `h-index` INT NULL,
  PRIMARY KEY (`dblpKey`))
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `schenql-db`.`person_names`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`person_names` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`person_names` (
  `name` VARCHAR(200) COLLATE utf8mb4_bin NOT NULL,
  `personKey` VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`name`),
  INDEX `fk_personKey_idx` (`personKey` ASC),
  CONSTRAINT `fk_personKey`
    FOREIGN KEY (`personKey`)
    REFERENCES `schenql-db`.`person` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `schenql-db`.`conference`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`conference` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`conference` (
  `dblpKey` VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
  `acronym` VARCHAR(50) NULL,
  `corerank` VARCHAR(3) NULL,
  PRIMARY KEY (`dblpKey`),
  INDEX `conference_acronym_idx` (`acronym` ASC))
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `schenql-db`.`journal`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`journal` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`journal` (
  `dblpKey` VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
  `acronym` VARCHAR(50) NULL,
  PRIMARY KEY (`dblpKey`),
  INDEX `journal_acronym_idx` (`acronym` ASC))
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `schenql-db`.`journal_name`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`journal_name` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`journal_name` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(200) NOT NULL,
  `journalKey` VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_journalKey_idx` (`journalKey` ASC),
  INDEX `journal_name_name_idx` (`name` ASC),
  CONSTRAINT `fk_journalKey`
    FOREIGN KEY (`journalKey`)
    REFERENCES `schenql-db`.`journal` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `schenql-db`.`publication`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`publication` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`publication` (
  `dblpKey` VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
  `title` VARCHAR(1000) NULL,
  `abstract` TEXT NULL,
  `ee` VARCHAR(500) NULL,
  `url` VARCHAR(500) NULL,
  `year` INT NULL,
  `volume` VARCHAR(50) NULL,
  `type` ENUM('article', 'masterthesis', 'inproceedings', 'phdthesis', 'book') NULL,
  `conference_dblpKey` VARCHAR(100) COLLATE utf8mb4_bin NULL,
  `journal_dblpKey` VARCHAR(100) COLLATE utf8mb4_bin NULL,
  PRIMARY KEY (`dblpKey`),
  INDEX `fk_publication_conference_idx` (`conference_dblpKey` ASC),
  INDEX `fk_publication_journal_idx` (`journal_dblpKey` ASC),
  INDEX `publication_year_idx` (`year`),
  INDEX `type_idx` (`type`),
  FULLTEXT `fulltext_title_idx` (`title`),
  FULLTEXT `fulltext_abstract_idx` (`abstract`),
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
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `schenql-db`.`keyword`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`keyword` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`keyword` (
  `keyword` VARCHAR(250) NOT NULL,
  PRIMARY KEY (`keyword`))
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `schenql-db`.`publication_has_keyword`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`publication_has_keyword` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`publication_has_keyword` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `dblpKey` VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
  `keyword` VARCHAR(250) NOT NULL,
  PRIMARY KEY (`id`),
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
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `schenql-db`.`person_authored_publication`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`person_authored_publication` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`person_authored_publication` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `personKey` VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
  `publicationKey` VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_person_authored_publication_person_idx` (`personKey` ASC),
  INDEX `fk_person_authored_publication_publication_idx` (`publicationKey` ASC),
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
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `schenql-db`.`person_edited_publication`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`person_edited_publication` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`person_edited_publication` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `personKey` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `publicationKey` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
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
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `schenql-db`.`person_reviewed_publication`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`person_reviewed_publication` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`person_reviewed_publication` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `personKey` VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
  `publicationKey` VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
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
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `schenql-db`.`institution`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`institution` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`institution` (
    `key` VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
    `primaryName` VARCHAR(300) NULL,
    `location` VARCHAR(100) NULL,
    `country` VARCHAR(100) NULL,
    `city` VARCHAR(100) NULL,
    `lat` FLOAT(10, 6) NULL ,
    `lon` FLOAT(10, 6) NULL ,
    PRIMARY KEY (`key`)
)
ENGINE = MyISAM;

-- -----------------------------------------------------
-- Table `schenql-db`.`institution_name`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`institution_name` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`institution_name` (
    `id` INT AUTO_INCREMENT NOT NULL,
    `name` VARCHAR(300) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
    `institutionKey` VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
    PRIMARY KEY (`id`),
    INDEX `fk_institutionKey_idx` (`institutionKey` ASC),
    CONSTRAINT `fk_institutionKey`
        FOREIGN KEY (`institutionKey`)
        REFERENCES `schenql-db`.`institution` (`key`)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
)
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `schenql-db`.`publication_references`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`publication_references` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`publication_references` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `pub_id` VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
  `pub2_id` VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
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
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `schenql-db`.`person_works_for_institution`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`person_works_for_institution` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`person_works_for_institution` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `personKey` VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
  `institutionKey` VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_person_works_for_institution_institution_idx` (`institutionKey` ASC),
  INDEX `fk_person_works_for_institution_person_idx` (`personKey` ASC),
  CONSTRAINT `fk_person_works_for_institution_person`
    FOREIGN KEY (`personKey`)
    REFERENCES `schenql-db`.`person` (`dblpKey`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_person_works_for_institution_institution`
    FOREIGN KEY (`institutionKey`)
    REFERENCES `schenql-db`.`institution` (`key`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `schenql-db`.`person_works_for_institution`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `schenql-db`.`conference_name` ;

CREATE TABLE IF NOT EXISTS `schenql-db`.`conference_name` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `acronym` VARCHAR(50) NOT NULL,
  `title` VARCHAR(500) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_acronym_idx` (`acronym` ASC)
ENGINE = MyISAM;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
