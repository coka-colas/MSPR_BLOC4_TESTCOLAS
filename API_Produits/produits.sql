--Requêtes de création de la table Produits
--Création de la table Produits
    CREATE TABLE Produits (
        id INT AUTO_INCREMENT PRIMARY KEY,
        createdAt DATETIME,
        name VARCHAR(100),
        price FLOAT,
        description VARCHAR(500),
        color VARCHAR(30),
        stock INT,
    );