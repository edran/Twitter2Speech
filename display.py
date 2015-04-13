import json
import os
import ConfigParser
import argparse

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


def read_config(path):
    cp = ConfigParser.ConfigParser()
    cp.read(path)
    ck = cp.get("CONSUMER", "key")
    cs = cp.get("CONSUMER", "secret")
    at = cp.get("ACCESS", "token")
    ase = cp.get("ACCESS", "secret")
    data = (ck, cs, at, ase)
    mode = cp.get("GENERAL", "mode")
    hash = cp.get("GENERAL", "hashtag")
    return data, mode, hash

if __name__ == "__main__":
    def parse_cmd():
        """
        Parses command line and returns path string.
        Expected `python -f input.txt`.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', '--file',
                            dest='file',
                            required=True,
                            help='Path of file to analyse')
        args = parser.parse_args()
        return (args.file)

    def main():
        path = parse_cmd()
        p, m, hash = read_config(path)
        consumer_key = p[0]
        consumer_secret = p[1]
        access_token = p[2]
        access_token_secret = p[3]
        l = Twitter2Speech(m)
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        print "Showing all new tweets for #" + hash + ":"
        stream = tweepy.Stream(auth, l)
        stream.filter(track=[hash])
    main()
