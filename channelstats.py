# Importowanie niezbędnych bibliotek
import mysql.connector  
from mysql.connector import errorcode  
import requests  
import time  

# Konfiguracja połączenia z bazą danych MySQL, zastąp wartości swoimi
config = {
    'user': 'nazwa_uzytkownika',   
    'password': 'twoje_haslo',  
    'host': 'adres_serwera',  
    'port': numer_portu,  
    'database': 'nazwa_bazy_danych',  
}

# Nawiązywanie połączenia z bazą danych
connection = mysql.connector.connect(**config)

# Sprawdzanie, czy połączenie zostało nawiązane
if connection.is_connected():
    print("Pomyślnie połączono z bazą danych")

# Klucz API do korzystania z YouTube Data API
api_key = 'twoj_klucz_api'

# Identyfikator kanału YouTube, z którego chcemy pobierać filmy
channel_id = 'twoj_identyfikator_kanalu'

# Tworzenie URL do zapytania API, aby pobrać filmy z kanału
url = f'https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=11'

# Wykonywanie zapytania HTTP do YouTube Data API
response = requests.get(url)

# Sprawdzanie, czy odpowiedź z API była poprawna (status 200)
if response.status_code == 200:
    # Parsowanie danych JSON z odpowiedzi
    data = response.json()

    # Iterowanie po każdym filmie w odpowiedzi
    for item in data['items']:
        video_title = item['snippet']['title']  
        video_id = item['id']['videoId']  
        url2 = f'https://www.youtube.com/shorts/{video_id}'  # URL do krótkiego filmu na YouTube

        # Wykonywanie zapytania HTTP do URL krótkiego filmu
        response2 = requests.get(url2)
        time.sleep(2)  
        url3 = response2.url  

        # Sprawdzanie, czy ostateczny URL zawiera 'watch'
        if "watch" in url3:
            # Rozdzielanie tytułu na nazwisko artysty i nazwę utworu
            parts = video_title.split(" - ")
            artist_name = parts[0]  
            track_name = parts[1].split(" (")[0]  
            
            # Wyświetlanie informacji o artyście i utworze
            print(f"Artysta: {artist_name}")
            print(f"Utwór: {track_name}")

            # Tworzenie URL do zapytania o statystyki filmu
            url_stat = f'https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={api_key}'
            response_stat = requests.get(url_stat)  # Wykonywanie zapytania HTTP do YouTube Data API
            data_stat = response_stat.json()  # Parsowanie danych JSON z odpowiedzi

            # Pobieranie statystyk filmu
            view_count = data_stat['items'][0]['statistics']['viewCount']
            like_count = data_stat['items'][0]['statistics']['likeCount']
            fav_count = data_stat['items'][0]['statistics']['favoriteCount']
            comment_count = data_stat['items'][0]['statistics']['commentCount']

            # Wyświetlanie statystyk filmu
            print(f'Viewsy: {view_count}  Likey: {like_count}  Ulubione: {fav_count}  komentarze: {comment_count} \n')

            # Zapytanie SQL sprawdzające, czy film już istnieje w bazie danych
            query = f"SELECT id FROM jetwave WHERE youtubeid = '{video_id}'"
            dodaj = connection.cursor()
            dodaj.execute(query)
            result = dodaj.fetchone()

            if result is not None:
                # Jeśli film już istnieje, zaktualizuj rekord
                query = (f"UPDATE jetwave SET title = '{video_title}', artist_name = '{artist_name}', "
                         f"track_name = '{track_name}', views_count = '{view_count}', likes_count = '{like_count}', "
                         f"favourite_count = '{fav_count}', comments_count = '{comment_count}' WHERE id = {result[0]}")
            else:
                # Jeśli film nie istnieje, wstaw nowy rekord
                query = (f"INSERT INTO jetwave (youtubeid, title, artist_name, track_name, views_count, likes_count, "
                         f"favourite_count, comments_count) VALUES ('{video_id}', '{video_title}', '{artist_name}', "
                         f"'{track_name}', '{view_count}', '{like_count}', '{fav_count}', '{comment_count}')")

            dodaj.execute(query) 
            connection.commit()  
            dodaj.close()  

else:
    # Obsługa błędu, gdy odpowiedź z YouTube API jest niepoprawna
    print("Błąd podczas pobierania danych z YouTube API.")

# Zamknięcie połączenia z bazą danych
connection.close()
