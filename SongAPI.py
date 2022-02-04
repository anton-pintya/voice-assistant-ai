import re
import lyricsgenius

class SongFinder:
    def __init__(self, text_input, memory):
        self.text_input = text_input
        self.memory = memory
        token = '0iy6F02YIcODgGZjdo91DYR1q6A3FoRaVWn9fI2BPuwCeTLtl24IoVAVdqonb6-l'
        self.genius = lyricsgenius.Genius(token, verbose=False)
        self.artist = ''
        self.song = ''
        self.lyrics = ''
        self.song_info = self.genius.search(self.text_input, per_page=1)

    def find_song_name(self):
        full_title = self.song_info['hits'][0]['result']['full_title']

        for word in full_title.split(' '):
            if 'by' not in word:
                self.song += (word + ' ')
            else:
                break
        self.memory.find_lyrics['song'] = self.song
        return self.song

    def find_song_artist(self):
        self.artist = self.song_info['hits'][0]['result']['primary_artist']['name']
        self.memory.find_lyrics['artist'] = self.artist
        return self.artist

    def find_strings(self):
        if self.artist == '':
            self.artist = self.find_song_artist()
        if self.song == '':
            self.song = self.find_song_name()

        song = self.genius.search_song(self.song, self.artist).lyrics.lower().split('\n')
        old_song = list(song)

        for s in song:
            song[song.index(s)] = re.sub(r'\[.*\]', '', s)
            try:
                song[song.index(s)] = re.sub(r'-|,\s| — ', ' ', s)
            except:
                pass

        for s in song:
            if s == '':
                old_song.remove(old_song[song.index(s)])
                song.remove(s)

        for string in song:
            if self.text_input in string:
                for i in range(4):
                    try:
                        self.lyrics += old_song[song.index(string) + i].capitalize() + '\n'
                    except IndexError:
                        break
                break

        if self.lyrics == '':
            return 'Не удалось найти подходящие строчки в песне'
        else:
            self.memory.find_lyrics['lyrics'] = self.lyrics
            return self.lyrics

