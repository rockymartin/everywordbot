import tweepy
import os
from dotenv import load_dotenv
load_dotenv()

class EverywordBot(object):

    def __init__(self, consumer_key, consumer_secret,
                 access_token, token_secret,
                 source_file_name, index_file_name,
                 lat=None, long=None, place_id=None,
                 prefix=None, suffix=None, bbox=None,
                 dry_run=False):
        #file with line seperated words to be tweeted
        self.source_file_name = "wordlist.txt"
        #create a new .txt index file with just 0 inside 
        self.index_file_name = "index.txt"
        self.lat = lat
        self.long = long
        self.place_id = place_id
        #set words to appear before or after line from source_file_name, you'll probably want a space
        self.prefix = prefix
        self.suffix = " rocky"
        #bbox or "bounding box", aka the geo location that will appear under your tweet. 
        self.bbox = bbox
        #change line 12 or add --dry_run to args to do everything but send tweet
        self.dry_run = dry_run
        
        #variables hosted in .env file
        consumer_key = os.getenv("consumer_key")
        consumer_secret = os.getenv("consumer_secret")
        access_token = os.getenv("access_token")
        secret_token = os.getenv("secret_token")
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, secret_token)        
        self.twitter = tweepy.API(auth)
    
    def _get_current_index(self):
    #determine which line in source_file to tweet
        if not(os.path.isfile(self.index_file_name)):
            return 0
        with open(self.index_file_name) as index_fh:
            return int(index_fh.read().strip())

    def _increment_index(self, index):
    #add 1 to the index
        with open(self.index_file_name, "w") as index_fh:
            index_fh.truncate()
            index_fh.write("%d" % (index + 1))
            index_fh.close()

    def _get_current_line(self, index):
        with open(self.source_file_name) as source_fh:
            # read the desired line
            for i, status_str in enumerate(source_fh):
                if i == index:
                    break
            return status_str.strip()

    def _random_point_in(self, bbox):
        """Given a bounding box of (swlat, swlon, nelat, nelon),
         return random (lat, long)"""
        import random
        lat = random.uniform(bbox[0], bbox[2])
        long = random.uniform(bbox[1], bbox[3])
        return (lat, long)

    def post(self):
        index = self._get_current_index()
        status_str = self._get_current_line(index)
        if self.prefix:
            status_str = self.prefix + status_str
        if self.suffix:
            status_str = status_str + self.suffix
        if self.bbox:
            self.lat, self.long = self._random_point_in(self.bbox)

        if self.dry_run:
            print(status_str)
        else:
            self.twitter.update_status(status=status_str,
                                       lat=self.lat, long=self.long,
                                       place_id=self.place_id)
            self._increment_index(index)


def _csv_to_float_list(csv):
    return list(map(float, csv.split(',')))


if __name__ == '__main__':

    def _get_comma_separated_args(option, opt, value, parser):
        setattr(parser.values, option.dest, _csv_to_float_list(value))

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--consumer_key', dest='consumer_key',
                      help="twitter consumer key")
    parser.add_option('--consumer_secret', dest='consumer_secret',
                      help="twitter consumer secret")
    parser.add_option('--access_token', dest='access_token',
                      help="twitter token key")
    parser.add_option('--token_secret', dest='token_secret',
                      help="twitter token secret")
    parser.add_option('--source_file', dest='source_file',
                      default="tweet_list.txt",
                      help="source file (one line per tweet)")
    parser.add_option('--index_file', dest='index_file',
                      default="index",
                      help="index file (must be able to write to this file)")
    parser.add_option('--lat', dest='lat',
                      help="The latitude for tweets")
    parser.add_option('--long', dest='long',
                      help="The longitude for tweets")
    parser.add_option('--place_id', dest='place_id',
                      help="Twitter ID of location for tweets")
    parser.add_option('--bbox', dest='bbox',
                      type='string',
                      action='callback',
                      callback=_get_comma_separated_args,
                      help="Bounding box (swlat, swlon, nelat, nelon) "
                           "of random tweet location")
    parser.add_option('--prefix', dest='prefix',
                      help="string to add to the beginning of each post "
                           "(if you want a space, include a space)")
    parser.add_option('--suffix', dest='suffix',
                      help="string to add to the end of each post "
                           "(if you want a space, include a space)")
    parser.add_option('-n', '--dry_run', dest='dry_run', action='store_true',
                      help="Do everything except actually send the tweet or"
                           "update the index file")
    (options, args) = parser.parse_args()

    bot = EverywordBot(options.consumer_key, options.consumer_secret,
                       options.access_token, options.token_secret,
                       options.source_file, options.index_file,
                       options.lat, options.long, options.place_id,
                       options.prefix, options.suffix, options.bbox,
                       options.dry_run)

    bot.post()
