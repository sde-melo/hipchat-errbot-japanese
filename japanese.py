# -*- coding: utf-8 -*-

import datetime
import workalendar.core as cal
from collections import namedtuple
from errbot import BotPlugin, botcmd, arg_botcmd, webhook, ONLINE, AWAY
from workalendar.europe import France

CALENDAR = France()
NOON_TIME = datetime.time(hour=12)


class Japanese(BotPlugin):
    """
    Tell when is (finally!) the next Japanese
    """

    '''def get_configuration_template(self):
        """
        Defines the configuration structure this plugin supports

        You should delete it if your plugin doesn't use any configuration like this
        """
        return {'EXAMPLE_KEY_1': "Example value",
                'EXAMPLE_KEY_2': ["Example", "Value"]
               }'''
    
    @classmethod
    def find_following_working_weekday(cls, day, weekday):
        d = CALENDAR.get_first_weekday_after(day, weekday)
        while CALENDAR.is_holiday(d):
            d += datetime.timedelta(days=7)
        return d

    # Passing split_args_with=None will cause arguments to be split on any kind
    # of whitespace, just like Python's split() does
    @botcmd(split_args_with=None)
    def japonais(self, message, args):
        """Return the time delta of the next Japanese"""
        now = datetime.datetime.now()
        # now = datetime.datetime(2017, 4, 25, 13)
        WEEKDAY = cal.FRI
        japanese_datetime = datetime.datetime.combine(self.find_following_working_weekday(now, WEEKDAY), NOON_TIME)
        if japanese_datetime < now:
            japanese_datetime = datetime.datetime.combine(self.find_following_working_weekday(now + datetime.timedelta(days=1), WEEKDAY), NOON_TIME)
        delta = japanese_datetime - now
        delta_days = (japanese_datetime.date() - now.date()).days
        if delta_days > 0:
            if delta_days == 1:
                text = 'C\'est demain !'
            else:
                if delta_days > 7:
                    text = 'À cause des jours fériés, le prochain Japonais est encore dans {} jours. :( :( :('.format(delta_days)
                else:
                    text = 'Le Japonais est encore dans {} jours. :('.format(delta_days)
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
