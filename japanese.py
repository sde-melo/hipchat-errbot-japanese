# -*- coding: utf-8 -*-

import calendar
import datetime
from collections import namedtuple
from errbot import BotPlugin, botcmd, arg_botcmd, webhook, ONLINE, AWAY

NOON_TIME = datetime.time(hour=12)


class Japanese(BotPlugin):
    """
    Tell when is (finally!) the next Japanese
    """

    '''def __init__(self, *args, **kwargs):
       BotPlugin.__init__(self, *args, **kwargs)
       self._online = True'''

    '''def get_configuration_template(self):
        """
        Defines the configuration structure this plugin supports

        You should delete it if your plugin doesn't use any configuration like this
        """
        return {'EXAMPLE_KEY_1': "Example value",
                'EXAMPLE_KEY_2': ["Example", "Value"]
               }'''

    '''def callback_message(self, message):
        """Triggered for every received message that isn't coming from the bot itself"""
        print('Body:', message.body)
        print('Ctx:', message.ctx)
        print('Delayed:', message.delayed)
        print('Extras:', message.extras)
        print('Flow:', message.flow)
        print('Frm:', message.frm)
        print('Direct:', message.is_direct)
        print('Group:', message.is_group)
        print('To: ', message.to)
        print('Type:', message.type)
        print(message)
        #  'body', 'clone', 'ctx', 'delayed', 'extras', 'flow', 'frm', 'is_direct', 'is_group', 'to', 'type'
        if self._online and 'carotide' in message.body:
            self.change_presence(AWAY, 'Tu m\'as saoulé !')
            self._online = False
        elif not self._online and 'pardon' in message.body:
            self.change_presence(ONLINE, 'C\'est bon pour cette fois')
            self._online = True'''

    '''def callback_presence(self, presence):
        print(presence)
        print(dir(presence))
        if presence.get_message() is not None:
            print(presence)'''

    @classmethod
    def delta_to_dhms(cls, delta):
        Delta = namedtuple('Delta', ('days', 'hours', 'minutes', 'seconds'))
        units = (
           60 * 60,  # hours
           60,  # minutes
           1  # seconds
        )
        l = [delta.days]
        seconds = delta.seconds
        for unit in units:
            l.append(seconds // unit)
            seconds = seconds % unit
        return Delta(*l)

    # Passing split_args_with=None will cause arguments to be split on any kind
    # of whitespace, just like Python's split() does
    @botcmd(split_args_with=None)
    def japonais(self, message, args):
        """Return the time delta of the next Japanese"""
        now = datetime.datetime.now()
        days_to_next_japanese = (calendar.FRIDAY - now.weekday()) % 7
        japanese_datetime = datetime.datetime.combine((now + datetime.timedelta(days_to_next_japanese)).date(), NOON_TIME)
        delta = japanese_datetime - now
        if days_to_next_japanese > 0:
            if days_to_next_japanese == 1:
                text = 'C\'est demain !'
            else:
                text = 'Le Japonais est encore dans {} jours. :('.format(days_to_next_japanese)
        else:
            text = 'C\'est aujourd\'hui le Japonais !\n'
            if delta.seconds > 3600:
                hours = int(round(delta.seconds / 3600.))
                minutes_text = ''
                if hours < 5:
                    minutes = int(round((delta.seconds % 3600) / 60.))
                    if minutes > 4:
                        minutes_text = ' et {} minutes'.format(minutes)
                text += 'Dans {} heure{}{}'.format(hours, 's' if hours > 1 else '', minutes_text)
            else:
                if delta.seconds > 60:
                    minutes = int(round(delta.seconds / 60.))
                    text += 'Dans {} minute{}'.format(minutes, 's' if minutes > 1 else '')
                    if minutes < 11:
                        text += ' !'
                elif delta.seconds > 30:
                    text += 'Dans {} secondes !'.format(delta.seconds)
                else:
                    text = 'C\'est maintenant !!! Dépêchez-vous ! Go go go !'
        return text

    @botcmd(split_args_with=None)
    def jap(self, message, args):
        return self.japonais(message, args)
