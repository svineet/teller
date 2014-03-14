import os
import pickle
import re

from twisted.internet import reactor, protocol
from twisted.words.protocols import irc
from names_bot import NamesIRCClient


ABOUT = """Hey! I'm a bot by svineet who delivers messages to\
 other people when they join this channel. tellerbot info for more :)"""
INFO = """You can tell me like this -
 tellerbot tell svineet your bot is awesome
 and I'll tell svineet when he comes online.
 Also you can do this -
 tellerbot tellme svineet
 and I'll ping you when svineet comes online. :)
"""

ADDRESS_SIGNALS = [',', ':', ' ']

COMMAND_RE = r"(?P<command>\w+) (?P<args>.+)"
NICK_RE = r"[^ ]+"

# list of tuples - [[sender, nick, message, sent], ...]
# Not a dict, because this allows multiple messages to same nick
tell_data = []
tellme_data = []


class TellerBot(NamesIRCClient):
    nickname = 'tellerbot'

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        print "Lost connection, saving to pickle file"
        self.save_to_pickle()

    def signedOn(self):
        self.join(self.factory.channel)

    def joined(self, channel):
        self.msg(channel, ABOUT)
        print "Joined channel"
        self.load_pickle_data()

    def privmsg(self, user, channel, msg):
        global tell_data
        global tellme_data

        user = user.split('!', 1)[0]
        for_me = reduce(
            lambda x, y: x or y,
            [msg.startswith(self.nickname+i) for i in ADDRESS_SIGNALS])
        cut_msg = msg[len(self.nickname)+1:].strip()

        if for_me and cut_msg == "ping":
            self.msg(channel, user+", pong")

        if for_me and cut_msg == "info":
            self.msg(channel, user+","+INFO)

        if for_me and cut_msg == "source":
            self.msg(channel,
                     user+", I live here: https://github.com/svineet/teller")

        matched = re.match(COMMAND_RE, cut_msg)
        if for_me and matched:
            cmd = matched.group('command')
            args = matched.group('args')
            if cmd == "tell":
                args_match = re.match(
                    r"(?P<nick>"+NICK_RE+") (?P<message>.+)",
                    args)
                if args_match:
                    nick = args_match.group('nick')
                    message = args_match.group('message')
                    tell_data.append([user, nick, message, False])
                    self.msg(channel,
                             user+", Yes I'll convey your message.")
                else:
                    self.invalid_command(user, channel)

            elif cmd == "tellme":
                args_match = re.match(
                    r"(?P<nick>"+NICK_RE+r")",
                    args)
                if args_match:
                    nick = args_match.group('nick')
                    if nick == user:
                        self.msg(channel,
                                 user+", lol I'm a bot, not a fool.")
                    else:
                        pass
                else:
                    self.invalid_command(user, channel)
            else:
                self.invalid_command(user, channel)

    def invalid_command(self, user, channel):
        self.msg(channel,
                 user+", that's not a command. tellerbot info will help")

    def userJoined(self, user, channel):
        global tell_data
        global tellme_data

        for i in range(len(tell_data)):
            sender, nick, message, sent = tell_data[i]
            if nick == user:
                self.msg(
                    channel,
                    user+", Hey! "+sender+" told me to tell you this:")
                self.msg(channel, message)
                tell_data[i][3] = True
        tell_data = [x for x in tell_data if x[3] is False]

    def userRenamed(self, oldname, newname):
        self.userJoined(self, newname, self.channel)

    def load_pickle_data(self):
        if os.path.isfile(self.pickle_file):
            with open(self.pickle_file) as f:
                data = pickle.load(f)
                global tell_data
                global tellme_data
                tellme_data = data['tellme_data']
                tell_data = data['tell_data']

    def save_to_pickle(self):
        global tell_data
        global tellme_data

        with open(self.pickle_file, "w") as f:
            data = {
                "tell_data": tell_data,
                "tellme_data": tellme_data
            }
            pickle.dump(data, f)

    def alterCollidedNick(self, nickname):
        return '_' + nickname + '_'


class BotFactory(protocol.ClientFactory):
    def __init__(self, channel, pickle_file):
        self.channel = channel
        self.pickle_file = pickle_file

    def buildProtocol(self, addr):
        p = TellerBot()
        p.factory = self
        p.channel = self.channel
        p.pickle_file = self.pickle_file
        return p

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    print "Channel Name:",
    channel = raw_input()

    print "Pickle file name:",
    pickle_file = raw_input()
    if pickle_file == "":
        pickle_file = "tellerbot_data.pickle"

    f = BotFactory(channel, pickle_file)
    reactor.connectTCP("irc.freenode.net", 6667, f)
    reactor.run()
