import pyodbc
from random import randint
from PIL import Image
from tkinter import Tk, Label
from PIL import Image, ImageTk
import os
from tabulate import tabulate
import time

PoUtworzeniu = 0

#v.01
#Utworzono polaczenie do bazy danych i tworzenie pokoju gier

#v.02
#Utworzono uruchamianie gry, wyswietlanie planszy i informacji o grze, dodano mozliwosc wykonania rzutu kostka
#v.03
#Utworzono mechanike gry po stronie bazy danych oraz mozliwosc pelnego ruchu gracza,dodano multiplayer
def display_image(image_path):
   
    image = Image.open(image_path)
    
    
    image.show()
def print_tables(cursor,gameroom_name):
    
    cursor.execute("SELECT NickGracza, AktualnePole, Saldo FROM Gracze where nazwaPokoju  = ?", gameroom_name)
    gracze = cursor.fetchall()
    
    cursor.execute("SELECT NrPola, Miasto, Wlasciciel FROM Miasta WHERE Wlasciciel IS NOT NULL and nazwaPokoju  = ?", gameroom_name)
    miasta = cursor.fetchall()
    
    cursor.execute("SELECT b.Miasto, a.Wlasciciel FROM nieruchomosci a JOIN Miasta b ON a.NrPola = b.NrPola and a.nazwaPokoju = b.nazwaPokoju WHERE a.Wlasciciel IS NOT NULL and a.nazwaPokoju  = ?", gameroom_name)
    nieruchomosci = cursor.fetchall()

  
    gracze_table = [[row.NickGracza, row.AktualnePole, row.Saldo] for row in gracze]
    miasta_table = [[row.Wlasciciel, row.Miasto] for row in miasta]
    nieruchomosci_table = [[row.Wlasciciel, row.Miasto] for row in nieruchomosci]

   
    gracze_table.insert(0, ["NickGracza", "AktualnePole", "Saldo"])
    miasta_table.insert(0, ["Wlasciciel", "Miasto"])
    nieruchomosci_table.insert(0, ["Wlasciciel", "Miasto"])

   
    combined_table = []
    max_len = max(len(gracze_table), len(miasta_table), len(nieruchomosci_table))
    
    for i in range(max_len):
        row = []
        if i < len(gracze_table):
            row.extend(gracze_table[i])
        else:
            row.extend([""] * len(gracze_table[0]))
        
        row.append("|")
        
        if i < len(miasta_table):
            row.extend(miasta_table[i])
        else:
            row.extend([""] * len(miasta_table[0]))
        
        row.append("|")
        
        if i < len(nieruchomosci_table):
            row.extend(nieruchomosci_table[i])
        else:
            row.extend([""] * len(nieruchomosci_table[0]))
        
        combined_table.append(row)
    print(tabulate(combined_table, tablefmt="plain"))
def start_or_join_game(gameroom_name,player):
    PoUtworzeniu = 0

    connection = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};'
                                'SERVER=localhost;'
                                'DATABASE=Monopoly;'
                                'UID=Monopoly_Auth;'
                                'PWD=Monopoly#2')

    cursor = connection.cursor()
    

    cursor.execute("SELECT Nazwa FROM ListaGier WHERE Nazwa = ?", gameroom_name)
    existing_room = cursor.fetchone()
    
    if existing_room:

        print("Dolaczam do pokoju:", gameroom_name)
        print(existing_room)
        connection.commit() 
        image_path = "C:/Users/user/Desktop/Monopoly/plansza1.png"  
        display_image(image_path)
        print('Rozpoczynam gre')
        os.system('cls')
        print_tables(cursor,gameroom_name)
        CzyBankrut = 0
        CzyRuch = 1
        while CzyBankrut == 0 and CzyRuch == 1:
            ruch = input('Wcisknij dowolny guzik zeby rzucic kostka ')
            wynik = randint(1,6)

                
  
            cursor.execute("EXEC RuchGracza @wynik = ?, @gracz = ?, @nazwaPokoju = ?", (wynik,player,gameroom_name))
            cursor.execute("SELECT AktualnePole FROM Gracze WHERE nazwaPokoju = ? and NickGracza = ?", (gameroom_name, player))
            pole = cursor.fetchone().AktualnePole
            os.system('cls')
            print_tables(cursor,gameroom_name)
            print('Wyrzuciles: ' + str(wynik))
            print('Aktualnie znajdujesz się na polu: ' + str(pole))
            cursor.execute("SELECT odpowiedz, komunikat FROM Komunikaty where nazwaPokoju = ? and Gracz = ?", (gameroom_name, player))
            result = cursor.fetchone()
            odpowiedz = result.odpowiedz
            komunikat = result.komunikat
                
            print(komunikat)
            if odpowiedz == 'Bankrut':
                image_path1 = "C:/Users/user/Desktop/Monopoly/bankrut.jpg"  
                display_image(image_path1)
                exit()
                CzyBankrut = 1
            if odpowiedz == "WolneMiasto":
                wybor = input('Wybierz: ')
                if wybor == '1':
                    cursor.execute("EXEC ZakupMiasta @nazwaPokoju = ?", (player, gameroom_name))
                    print('Zakupiono miasto.')
                else:
                    cursor.execute("EXEC ZmianaKolejki @nazwaPokoju = ?", (gameroom_name))
                    CzyRuch = 0
            if odpowiedz == "WolnaNieruchomosc":
                wybor = input('Wybierz: ')
                if wybor == '1':
                    cursor.execute("EXEC ZakupNieruchomosci @nazwaPokoju = ?", (player, gameroom_name))
                    print('Zakupiono nieruchomosc.')
                else:
                    cursor.execute("EXEC ZmianaKolejki @nazwaPokoju =?", (gameroom_name))
                    CzyRuch = 0
            else:
                    cursor.execute("EXEC ZmianaKolejki @nazwaPokoju = ?", (gameroom_name))
                    CzyRuch = 0 
        while CzyBankrut == 0 and CzyRuch == 0:
            time.sleep(5)
            os.system('cls')
            print_tables(cursor,gameroom_name)
            print('Koniec twojej rundy')
            cursor.execute("SELECT NickGracza from Gracze a join ListaGier b on a.id  = b.RuchGracza and a.nazwaPokoju = b.nazwa where b.nazwa = ?", (gameroom_name))
            CheckRuchu = cursor.fetchone()
            if CheckRuchu == str(player):
                CzyRuch = 1
    else:

        print("Tworze nowy Pokoj:", gameroom_name)
        cursor.execute("INSERT INTO ListaGier (nazwa, gracze, CzyAktywna,CzyTrwa ) values(?, ?, 1, 0)", (gameroom_name, player))
        connection.commit() 
        while PoUtworzeniu != '2':
            cursor.execute("SELECT gracze FROM ListaGier WHERE Nazwa = ?", gameroom_name)
            players = cursor.fetchone()
            os.system('cls')
            print("Aktualny pokoj:", existing_room)
            print("Gracze: ", players)
            print('[1] Odswiez liste graczy')
            print('[2] Zacznij gre')
            PoUtworzeniu = input('Wybierz opcje: ')
        if PoUtworzeniu == '2':
            ruch = 0
            cursor.execute("INSERT INTO Gracze (nazwaPokoju, NickGracza) values(?, ?)", (gameroom_name, player))
            cursor.execute('EXEC InsertMiasta @nazwapokoju = ? ', gameroom_name)
            cursor.execute('UPDATE a  SET a.RuchGracza = b.id  FROM ListaGier a JOIN (SELECT id, nazwaPokoju from Gracze where Nickgracza  = ? and nazwaPokoju = ? ) b on a.nazwa = b.nazwaPokoju', (player, gameroom_name))
            connection.commit() 
            image_path = "C:/Users/user/Desktop/Monopoly/plansza1.png"  
            display_image(image_path)
            print('Rozpoczynam gre')
            os.system('cls')
            print_tables(cursor,gameroom_name)
            CzyBankrut = 0
            CzyRuch = 1
            while CzyBankrut == 0 and CzyRuch == 1:
                ruch = input('Wcisknij dowolny guzik zeby rzucic kostka ')
                wynik = randint(1,6)

                
  
                cursor.execute("EXEC RuchGracza @wynik = ?, @gracz = ?, @nazwaPokoju = ?", (wynik,player,gameroom_name))
                cursor.execute("SELECT AktualnePole FROM Gracze WHERE nazwaPokoju = ? and NickGracza = ?", (gameroom_name, player))
                pole = cursor.fetchone().AktualnePole
                os.system('cls')
                print_tables(cursor,gameroom_name)
                print('Wyrzuciles: ' + str(wynik))
                print('Aktualnie znajdujesz się na polu: ' + str(pole))
                cursor.execute("SELECT odpowiedz, komunikat FROM Komunikaty where nazwaPokoju = ? and Gracz = ?", (gameroom_name, player))
                result = cursor.fetchone()
                odpowiedz = result.odpowiedz
                komunikat = result.komunikat
                
                print(komunikat)
                if odpowiedz == 'Bankrut':
                    image_path1 = "C:/Users/user/Desktop/Monopoly/bankrut.jpg"  
                    display_image(image_path1)
                    exit()
                    CzyBankrut = 1
                if odpowiedz == "WolneMiasto":
                    wybor = input('Wybierz: ')
                    if wybor == '1':
                        cursor.execute("EXEC ZakupMiasta @nazwaPokoju = ?", (player, gameroom_name))
                        print('Zakupiono miasto.')
                    else:
                        cursor.execute("EXEC ZmianaKolejki @nazwaPokoju = ?", (gameroom_name))
                        CzyRuch = 0
                if odpowiedz == "WolnaNieruchomosc":
                    wybor = input('Wybierz: ')
                    if wybor == '1':
                        cursor.execute("EXEC ZakupNieruchomosci @nazwaPokoju = ?", (player, gameroom_name))
                        print('Zakupiono nieruchomosc.')
                    else:
                        cursor.execute("EXEC ZmianaKolejki @nazwaPokoju =?", (gameroom_name))
                        CzyRuch = 0
                else:
                        cursor.execute("EXEC ZmianaKolejki @nazwaPokoju = ?", (gameroom_name))
                        CzyRuch = 0 
            while CzyBankrut == 0 and CzyRuch == 0:
                time.sleep(5)
                os.system('cls')
                print_tables(cursor,gameroom_name)
                print('Koniec twojej rundy')
                cursor.execute("SELECT NickGracza from Gracze a join ListaGier b on a.id  = b.RuchGracza and a.nazwaPokoju = b.nazwa where b.nazwa = ?", (gameroom_name))
                CheckRuchu = cursor.fetchone()
                if CheckRuchu == str(player):
                    CzyRuch = 1

                
                

    connection.close()

if __name__ == "__main__":
    
    player = input("Podaj swoj Nick: ")
    gameroom_name = input("Podaj nazwe pokoju: ")
    
    
    start_or_join_game(gameroom_name, player)