CREATE TABLE ListaGier 
(
id int IDENTITY (1,1),
nazwa varchar(50) not null,
gracze varchar(50) not null,
CzyAktywna int not null,
CzyTrwa int not null,
RuchGracza int null
)

CREATE table Gracze 
(
id int IDENTITY (1,1),
nazwaPokoju varchar(50) not null,
NickGracza varchar(50) not null,
Saldo int not null default(200),
AktualnePole int not null default(1)

)

CREATE TABLE Miasta(
nazwaPokoju varchar(50) not null,
NrPola int not null,
Miasto varchar(50) not null,
Wlasciciel varchar(50)
)

CREATE TABLE nieruchomosci (
nazwaPokoju varchar(50) not null,
NrPola int not null,
Wlasciciel varchar(50) not null
)