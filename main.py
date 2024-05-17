import os
import pyodbc
import random
from PIL import Image
from tkinter import Tk, Label
from PIL import Image, ImageTk
from tabulate import tabulate
PoUtworzeniu = 0

#v.01
#Utworzono polaczenie do bazy danych i tworzenie pokoju gier

#v.02
#Utworzono uruchamianie gry, wyswietlanie planszy i informacji o grze, dodano mozliwosc wykonania rzutu kostka
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
    print("#################Gracze###############|####Miasta####|")
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
    else:

        print("Tworze nowy Pokoj:", gameroom_name)
        cursor.execute("INSERT INTO ListaGier (nazwa, gracze, CzyAktywna,CzyTrwa ) values(?, ?, 1, 0)", (gameroom_name, player))
        connection.commit() 
        while PoUtworzeniu != '2':
            cursor.execute("SELECT gracze FROM ListaGier WHERE Nazwa = ?", gameroom_name)
            players = cursor.fetchone()
            print("Aktualny pokoj:", existing_room)
            print("Gracze: ", players)
            print('[1] Odswiez liste graczy')
            print('[2] Zacznij gre')
            PoUtworzeniu = input('Wybierz opcje: ')
        if PoUtworzeniu == '2':
            ruch = 0
            cursor.execute("INSERT INTO Gracze (nazwaPokoju, NickGracza) values(?, ?)", (gameroom_name, player))
            cursor.execute('EXEC InsertMiasta @nazwapokoju = ? ', gameroom_name)
            connection.commit() 
            os.system('cls')
            display_image(image_path)
            print('Rozpoczynam gre')
            print_tables(cursor,gameroom_name)
            CzyBankrut = 0
            CzyRuch = 0
            while CzyBankrut == 0 and CzyRuch == 1:
                ruch = input('Wcisknij dowolny guzik zeby rzucic kostka ')
                wynik = random(1,6)
                print('Wyrzuciles: ' + wynik)
                cursor.execute("SELECT AktualnePole FROM Gracze WHERE nazwaPokoju = ? and NickGracza = ?", (gameroom_name, player))
                pole = cursor.fetchone()
                pole = pole + wynik
                cursor.execute("EXEC RuchGracza @wynik = ?, @gracz = ?, @nazwaPokoju = ?", (wynik,player,gameroom_name))
            

    connection.close()

if __name__ == "__main__":
    
    player = input("Podaj swoj Nick: ")
    gameroom_name = input("Podaj nazwe pokoju: ")
    image_path = "C:/Users/user/Desktop/Monopoly/plansza1.png"  
    
    start_or_join_game(gameroom_name, player)