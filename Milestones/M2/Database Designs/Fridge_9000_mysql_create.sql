CREATE TABLE `Users` (
	`UserID` INT NOT NULL AUTO_INCREMENT,
	`Email` varchar(255) NOT NULL UNIQUE,
	`Username` varchar(255) NOT NULL UNIQUE,
	`Password` varchar(255) NOT NULL,
	`Name` varchar(255) NOT NULL,
	`OwnedFridges` TEXT,
	`FriendedFridges` TEXT,
	`PersonalNotes` TEXT,
	`eff_bgn_ts` DATETIME NOT NULL,
	`eff_end_ts` DATETIME NOT NULL,
	PRIMARY KEY (`UserID`,`Email`)
);

CREATE TABLE `Fridge` (
	`FridgeID` INT NOT NULL AUTO_INCREMENT,
	`FridgeName` varchar(255) NOT NULL,
	`Owner` INT NOT NULL,
	`Friends` TEXT NOT NULL,
	`Auto_gen_grocery_list` TEXT,
	`Manually_added_list` TEXT,
	`creation_date` DATETIME NOT NULL,
	`modified_date` DATETIME NOT NULL,
	`eff_bgn_ts` DATETIME NOT NULL,
	`eff_end_ts` DATETIME NOT NULL,
	PRIMARY KEY (`FridgeID`)
);

CREATE TABLE `Items` (
	`ItemID` INT NOT NULL AUTO_INCREMENT,
	`ItemName` varchar(255) NOT NULL,
	`Age` TIME NOT NULL,
	`isPerishable` BOOLEAN NOT NULL,
	`Calories` INT,
	`creation_date` DATETIME NOT NULL,
	`modified_date` DATETIME NOT NULL,
	`eff_bgn_ts` DATETIME NOT NULL,
	`eff_end_ts` DATETIME NOT NULL,
	PRIMARY KEY (`ItemID`)
);

CREATE TABLE `Fridge_Contents` (
	`FridgeID` INT NOT NULL,
	`ItemID` INT NOT NULL,
	`AddedBy` INT NOT NULL,
	`ExpirationDate` DATETIME NOT NULL,
	`Size` INT,
	`creation_date` DATETIME NOT NULL,
	`modified_date` DATETIME NOT NULL,
	`eff_bgn_ts` DATETIME NOT NULL,
	`eff_end_ts` DATETIME NOT NULL
);

CREATE TABLE `Recipes` (
	`FridgeId` INT NOT NULL,
	`UserId` INT NOT NULL,
	`Title` TEXT NOT NULL,
	`SourceUrl` TEXT NOT NULL,
	`eff_bgn_ts` DATETIME NOT NULL,
	`eff_end_ts` DATETIME NOT NULL
);

ALTER TABLE `Fridge` ADD CONSTRAINT `Fridge_fk0` FOREIGN KEY (`Owner`) REFERENCES `Users`(`UserID`);

ALTER TABLE `Fridge_Contents` ADD CONSTRAINT `Fridge_Contents_fk0` FOREIGN KEY (`FridgeID`) REFERENCES `Fridge`(`FridgeID`);

ALTER TABLE `Fridge_Contents` ADD CONSTRAINT `Fridge_Contents_fk1` FOREIGN KEY (`ItemID`) REFERENCES `Items`(`ItemID`);

ALTER TABLE `Fridge_Contents` ADD CONSTRAINT `Fridge_Contents_fk2` FOREIGN KEY (`AddedBy`) REFERENCES `Users`(`UserID`);

ALTER TABLE `Recipes` ADD CONSTRAINT `Recipes_fk0` FOREIGN KEY (`FridgeId`) REFERENCES `Fridge`(`FridgeID`);

ALTER TABLE `Recipes` ADD CONSTRAINT `Recipes_fk1` FOREIGN KEY (`UserId`) REFERENCES `Users`(`UserID`);

