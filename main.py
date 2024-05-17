from turtle import clearscreen
from PIL import Image
import pyodbc
PoUtworzeniu = 0

#v.01
#Utworzono polaczenie do bazy danych i tworzenie pokoju gier
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
            clearscreen()
            print('Rozpoczynam gre')

    connection.close()

if __name__ == "__main__":
    
    player = input("Podaj swoj Nick: ")
    gameroom_name = input("Podaj nazwe pokoju: ")
    start_or_join_game(gameroom_name, player)