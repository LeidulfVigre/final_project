-- Code for creating the LSMDb (Leidulf Simon Movie Database)

create database LSMDb;

use LSMDB;

create table Movie(
    Movie_ID INT NOT NULL PRIMARY KEY,
    Movie_Title VARCHAR(150) NOT NULL,
    Duration TIME,
    Genre VARCHAR(50),
    Age_Limit INT CHECK (Age_Limit in (0, 6, 9, 12, 15, 18)),
    Release_Date DATE,
    Synopsis VARCHAR(300),
    Country_Of_Origin VARCHAR(50),
    Movie_Language VARCHAR(50)
);

create table Actor(
    Actor_ID INT NOT NULL PRIMARY KEY,
    Actor_First_Name VARCHAR(50) NOT NULL,
    Actor_Last_Name VARCHAR(50) NOT NULL,
    Date_Of_Birth DATE,
    Height INT
);

create table Director(
    Director_ID INT NOT NULL PRIMARY KEY,
    Director_First_Name VARCHAR(50) NOT NULL,
    Director_Last_Name VARCHAR(50) NOT NULL,
    Date_Of_Birth DATE,
    Height INT
);

create table User(
    User_ID INT NOT NULL PRIMARY KEY,
    Username VARCHAR(50) NOT NULL UNIQUE,
    First_Name VARCHAR(50) NOT NULL,
    Last_Name VARCHAR(50) NOT NULL,
    User_Type CHAR(1) NOT NULL CHECK (User_Type IN ('N', 'A')),
    Reviewer_Score INT,
    Password_Hash VARCHAR(1000) NOT NULL,
);

create table Rating(
    Rating_ID INT NOT NULL PRIMARY KEY,
    Rating_Score INT CHECK (Rating_Score BETWEEN 1 AND 6), 
    Rating_Date DATETIME NOT NULL,
    User_ID INT NOT NULL,
    Movie_ID INT NOT NULL,
    foreign key (User_ID) references User(User_ID),
    foreign key (Movie_ID) references Movie(Movie_ID)
);

create table Review(
    Review_ID INT NOT NULL PRIMARY KEY,
    Likes INT,
    Dislikes INT,
    Review_Text VARCHAR(1000) NOT NULL,
    Review_Date DATETIME NOT NULL, 
    User_ID INT NOT NULL,
    Movie_ID INT NOT NULL,
    Rating_ID INT NOT NULL,
    Review_Title VARCHAR(50) NOT NULL,
    foreign key (User_ID) references User(User_ID), 
    foreign key (Movie_ID) references Movie(Movie_ID),
    foreign key (Rating_ID) references Rating(Rating_ID)
);

create table Director_And_Movie(
    Director_ID INT NOT NULL,
    Movie_ID INT NOT NULL,
    primary key(Director_ID, Movie_ID),
    foreign key (Director_ID) references Director(Director_ID),
    foreign key (Movie_ID) references Movie(Movie_ID)
);

create table Actor_And_Movie(
    Actor_ID INT NOT NULL,
    Movie_ID INT NOT NULL,
    Character_Name VARCHAR(50),
    primary key(Actor_ID, Movie_ID),
    foreign key (Actor_ID) references Actor(Actor_ID),
    foreign key (Movie_ID) references Movie(Movie_ID)
);