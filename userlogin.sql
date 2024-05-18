--Login i user

USE master
CREATE LOGIN Monopoly_AUTH  WITH password=',@vbEJ@n21>1>d{Y'


use VIZJOPOLY1
CREATE USER Monopoly_AUTH for login Monopoly_AUTH

EXEC sp_addrolemember N'db_datareader', N'Monopoly_AUTH'
GO
