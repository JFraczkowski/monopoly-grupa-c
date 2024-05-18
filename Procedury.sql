Create procedure ZakupMiasta
    @nazwaPokoju VARCHAR(50),
	@gracz VARCHAR(50)
AS

BEGIN
declare @pole int
SET @pole = (SELECT AktualnePole from Gracze where nazwaPokoju = @nazwaPokoju and NickGracza = @gracz)
UPDATE  a
SET Wlasciciel = @gracz

from Miasta a  where a.NrPola = @pole and a.nazwaPokoju = @nazwaPokoju
UPDATE a
SET Saldo = (Saldo - 50)

FROM Gracze a
where nazwaPokoju = @nazwaPokoju and NickGracza = @gracz

END
GO
Create  procedure ZakupNieruchomosci
    @nazwaPokoju VARCHAR(50),
	@gracz VARCHAR(50)
AS

BEGIN
declare @pole int
SET @pole = (SELECT AktualnePole from Gracze where nazwaPokoju = @nazwaPokoju and NickGracza = @gracz)
UPDATE  a
SET Wlasciciel = @gracz

from nieruchomosci a  where a.NrPola = @pole and a.nazwaPokoju = @nazwaPokoju

UPDATE a
SET Saldo = (Saldo - 20)

FROM Gracze a
where nazwaPokoju = @nazwaPokoju and NickGracza = @gracz
END

GO
CREATE PROCEDURE RuchGracza
    @wynik int,
    @gracz nvarchar(50),
    @nazwapokoju NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @aktualnePole int;
    DECLARE @WlascicielPola nvarchar(50);
    DECLARE @WlascicielNieruchomosci nvarchar(50);
    DECLARE @odpowiedz nvarchar(50);
    DECLARE @komunikat nvarchar(50);
    DECLARE @saldo int;

    SET @komunikat = ''; -- Initialize @komunikat to an empty string

    BEGIN TRY
        SET @aktualnePole = (SELECT AktualnePole + @wynik FROM Gracze WHERE nazwaPokoju = @nazwaPokoju AND NickGracza = @gracz);

        -- Przejscie przez start
        IF @aktualnePole > 28 OR @aktualnePole = 1
        BEGIN
            SET @aktualnePole = @aktualnePole - 28;
            UPDATE a
            SET Saldo = Saldo + 200
            FROM Gracze a
            WHERE a.nazwaPokoju = @nazwapokoju AND a.NickGracza = @gracz;
            SET @komunikat = @komunikat + 'Przedles przez start, dostales 200$ |';
        END

        -- Aktualizacja pola po rzucie kostka
        UPDATE a
        SET AktualnePole = @aktualnePole
        FROM Gracze a
        WHERE a.nazwaPokoju = @nazwapokoju AND a.NickGracza = @gracz;

        -- Wygrana w totolotka
        IF @aktualnePole IN (3, 10, 20, 27)
        BEGIN
            UPDATE a
            SET Saldo = Saldo + 50
            FROM Gracze a
            WHERE a.nazwaPokoju = @nazwapokoju AND a.NickGracza = @gracz;
            SET @komunikat = @komunikat + 'Wygrales w totolotka, dostales 50$ |';
        END

        -- Domiar podatkowy
        IF @aktualnePole IN (5, 12, 17, 25)
        BEGIN
            UPDATE a
            SET Saldo = Saldo - 50
            FROM Gracze a
            WHERE a.nazwaPokoju = @nazwapokoju AND a.NickGracza = @gracz;
            SET @komunikat = @komunikat + 'Zaplaciles domiar podatkowy, straciles 50$ |';
        END

        IF @aktualnePole = 22
        BEGIN
            UPDATE a
            SET AktualnePole = 8
            FROM Gracze a
            WHERE a.nazwaPokoju = @nazwapokoju AND a.NickGracza = @gracz;
            SET @komunikat = @komunikat + 'Trafiles do wiezienia, koniec rundy. |';
            SET @odpowiedz = 'Wiezienie';
        END

        SET @WlascicielPola = (SELECT Wlasciciel FROM Miasta WHERE nazwaPokoju = @nazwapokoju AND NrPola = @aktualnePole);

        -- Mozliwosc zakupu miasta
        IF @WlascicielPola IS NULL AND @aktualnePole NOT IN (3, 10, 20, 27, 5, 12, 17, 25, 1, 8, 15, 22)
        BEGIN
            SET @komunikat = @komunikat + 'Trafiles na wolne miasto wpisz [1] zeby je kupic za [50$] lub [2] zeby zakonczyc runde |';
            SET @odpowiedz = 'WolneMiasto';
        END

        -- Oplata za przejscie przez miasto innego gracza
        SET @WlascicielNieruchomosci = (SELECT Wlasciciel FROM nieruchomosci WHERE nazwaPokoju = @nazwapokoju AND NrPola = @aktualnePole);
        IF @WlascicielPola IS NOT NULL AND @WlascicielPola != @gracz AND @WlascicielNieruchomosci IS NULL
        BEGIN
            UPDATE a
            SET Saldo = Saldo - 20
            FROM Gracze a
            WHERE a.nazwaPokoju = @nazwapokoju AND a.NickGracza = @gracz;

            UPDATE a
            SET Saldo = Saldo + 20
            FROM Gracze a
            WHERE a.nazwaPokoju = @nazwapokoju AND a.NickGracza = @WlascicielPola;
            SET @komunikat = @komunikat + 'Trafiles na miasto gracza: ' + @WlascicielPola + ' zaplaciles mu 20$ |';
            SET @odpowiedz = 'ZajeteMiasto';
        END

        -- Oplata za przejscie przez miasto z nieruchomoscia
        IF @WlascicielPola IS NOT NULL AND @WlascicielPola != @gracz AND @WlascicielNieruchomosci IS NOT NULL
        BEGIN
            UPDATE a
            SET Saldo = Saldo - 50
            FROM Gracze a
            WHERE a.nazwaPokoju = @nazwapokoju AND a.NickGracza = @gracz;

            UPDATE a
            SET Saldo = Saldo + 50
            FROM Gracze a
            WHERE a.nazwaPokoju = @nazwapokoju AND a.NickGracza = @WlascicielPola;
            SET @komunikat = @komunikat + 'Trafiles na miasto gracza: ' + @WlascicielPola + ' na ktorej ma nieruchomosc, zaplaciles mu 50$ |';
            SET @odpowiedz = 'ZajeteMiastoNieruchomosc';
        END
		--Zabudowa miasta
		IF @WlascicielPola = @gracz and @aktualnePole NOT IN (3,10,20,27,5,12, 17, 25, 1,8,15,22) and @WlascicielNieruchomosci is null
		BEGIN
			SET @komunikat = @komunikat +'Trafiles na swoje niezabudowane maisto wpisz [1] zeby je zabudowaæ za [20$] lub [2] zeby zakonczyc runde |'
			SET @odpowiedz = 'WolnaNieruchomosc'
		END
		--Wlasne miasto
		IF @WlascicielPola = @gracz and @aktualnePole NOT IN (3,10,20,27,5,12, 17, 25, 1,8,15,22) and @WlascicielNieruchomosci is not null
		BEGIN
			SET @komunikat = @komunikat +'Trafiles na swoje wlasne miasto |'
			SET @odpowiedz = 'WlasneMiasto'
		END

        -- BezpiecznePole
        IF @aktualnePole IN (8, 15)
        BEGIN
            SET @odpowiedz = 'BezpiecznePole';
            SET @komunikat = @komunikat + 'Trafiles na bezpieczne pole, koniec rundy. |';
        END

        SET @saldo = (SELECT Saldo FROM Gracze a WHERE a.nazwaPokoju = @nazwapokoju AND a.NickGracza = @gracz);
        IF @saldo < 0
        BEGIN
            SET @odpowiedz = 'Bankrut';
            SET @komunikat = @komunikat + 'Niestety, zbankrutowa³eœ. Game over :(';
        END

        DELETE FROM Komunikaty WHERE nazwapokoju = @nazwapokoju AND Gracz = @gracz;
        INSERT INTO Komunikaty (nazwaPokoju, Gracz, Odpowiedz, Komunikat) VALUES (@nazwapokoju, @gracz, @odpowiedz, @komunikat);
    END TRY
    BEGIN CATCH
        DECLARE @ErrorMessage NVARCHAR(4000);
        DECLARE @ErrorSeverity INT;
        DECLARE @ErrorState INT;

        SELECT 
            @ErrorMessage = ERROR_MESSAGE(),
            @ErrorSeverity = ERROR_SEVERITY(),
            @ErrorState = ERROR_STATE();

        RAISERROR (@ErrorMessage, @ErrorSeverity, @ErrorState);
    END CATCH
END
GO

CREATE PROCEDURE ZmianaKolejki
    @nazwaPokoju VARCHAR(50)
AS
BEGIN

    DECLARE @currentRuchGracza INT;
    

    DECLARE @nextRuchGracza INT;


    SELECT @currentRuchGracza = RuchGracza
    FROM ListaGier
    WHERE nazwa = @nazwaPokoju;


    SELECT @nextRuchGracza = MIN(id)
    FROM Gracze
    WHERE nazwaPokoju = @nazwaPokoju
      AND id > @currentRuchGracza;


    IF @nextRuchGracza IS NULL
    BEGIN
        SELECT @nextRuchGracza = MIN(id)
        FROM Gracze
        WHERE nazwaPokoju = @nazwaPokoju;
    END

    UPDATE ListaGier
    SET RuchGracza = @nextRuchGracza
    WHERE nazwa = @nazwaPokoju;
END;
GO
CREATE PROCEDURE [dbo].[InsertMiasta]
    @nazwapokoju NVARCHAR(50) 
AS
BEGIN
    BEGIN TRANSACTION;


    INSERT INTO Miasta (nazwaPokoju, NrPola, Miasto) VALUES
    (@nazwapokoju, 2, 'Warszawa'),
    (@nazwapokoju, 4, 'Katowice'),
    (@nazwapokoju, 6, 'Poznan'),
    (@nazwapokoju, 7, 'Krakow'),
    (@nazwapokoju, 9, 'Rzeszow'),
    (@nazwapokoju, 11, 'Gdansk'),
    (@nazwapokoju, 13, 'Bialystok'),
    (@nazwapokoju, 14, 'Lodz'),
    (@nazwapokoju, 16, 'Elblag'),
    (@nazwapokoju, 18, 'Olsztyn'),
    (@nazwapokoju, 19, 'Opole'),
    (@nazwapokoju, 21, 'Torun'),
    (@nazwapokoju, 23, 'Bydgoszcz'),
    (@nazwapokoju, 24, 'Turek'),
    (@nazwapokoju, 26, 'Szczecin'),
    (@nazwapokoju, 27, 'Chelmno');

   
    IF @@ERROR <> 0
    BEGIN
       
        ROLLBACK TRANSACTION;
        RETURN;
    END
    ELSE
    BEGIN
        
        COMMIT TRANSACTION;
    END
END;
GO

