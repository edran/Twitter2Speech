import json
import os
import tweepy
import festival
import pyglet
from gtts import gTTS
import pygame
pygame.init()
pygame.mixer.init()


class Twitter2Speech(tweepy.StreamListener):

    def __init__(self, mode="festival"):
        self.mode = mode

    def on_data(self, data):
        # Twitter returns data in JSON format - we need to decode it first
        decoded = json.loads(data)

        # Also, we convert UTF-8 to ASCII ignoring all bad characters
        # sent by users
        user = decoded['user']['screen_name']
        text = decoded['text'].encode('ascii', 'ignore')
        print '@%s: %s' % (user,
                           text)
        self.speak(text)
        print "#######"
        return True

    def on_error(self, status):
        print status

    def speak(self, s):
        """
        TODO: refactor
        """
        if self.mode == "festival":
            festival.sayText(s)
            return
        tts = gTTS(text=s, lang='en')
        tts.save("speech.mp3")
        if self.mode == "pyglet":
            song = pyglet.media.load('speech.mp3')
            song.play()
            # TODO fix for multiple files
        elif self.mode == "pygame":
            clock = pygame.time.Clock()
            pygame.mixer.music.load("speech.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                clock.tick(1000)
                continue
        else:
            raise Exception("Mode not found!")
            os.remove("speech.mp3")
        os.remove("speech.mp3")
        return True


def main():
    consumer_key = ""
    consumer_secret = ""
    access_token = ""
    access_token_secret = ""
    l = Twitter2Speech("pyglet")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    hash = "programming"
    print "Showing all new tweets for #" + hash + ":"
    stream = tweepy.Stream(auth, l)
    stream.filter(track=[hash])


if __name__ == "__main__":
    main()
