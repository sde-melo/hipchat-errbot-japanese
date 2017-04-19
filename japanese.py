# -*- coding: utf-8 -*-

import collections
import datetime
import itertools
import workalendar.core as cal
from errbot import BotPlugin, botcmd, arg_botcmd, utils
from workalendar.europe import France


class Japanese(BotPlugin):
    """
    Tell when is (finally!) the next Japanese
    """

    CALENDAR = France()
    CONFIG_TEMPLATE = {
        'WEEKDAY': 'FRI',
        'TIME': '12:00'
    }
    FRENCH_DAYS = collections.OrderedDict((
        ('LUN', 'MON'),
        ('MAR', 'TUE'),
        ('MER', 'WED'),
        ('JEU', 'THU'),
        ('VEN', 'FRI'),
        ('SAM', 'SAT'),
        ('DIM', 'SUN'),
    ))

    def get_configuration_template(self):
        return self.CONFIG_TEMPLATE

    def check_weekday(self, weekday):
        valid_weekdays = list(self.FRENCH_DAYS.values()) + list(self.FRENCH_DAYS.keys())
        if weekday[:3] not in valid_weekdays:
            raise ValueError('"{}" is an invalid weekday. It should be amongst {}.'.format(weekday, ', '.join(valid_weekdays)))

    def check_time(self, time_):
        try:
            datetime.datetime.strptime(time_, '%H:%M')
        except ValueError:
            raise ValueError('"{}" is an invalid time.'.format(time_))

    def check_configuration(self, configuration=None):
        if not configuration:
            configuration = dict()
        invalid_keys = list()
        invalid_values = dict()
        for key, value in configuration.items():
            if key in self.CONFIG_TEMPLATE:
                validator = getattr(self, 'check_{}'.format(key.lower()))
                try:
                    validator(value)
                except ValueError as e:
                    invalid_values[key] = str(e)
            else:
                invalid_keys.append(key)
        invalid_keys.sort()
        if invalid_keys or invalid_values:
            error_msg = ''
            if invalid_keys:
                error_msg += 'invalid keys: ' + ', '.join(invalid_keys)
                if invalid_values:
                    error_msg += '; '
            if invalid_values:
                error_msg += '; '.join('invalid value for key "{}": {}'.format(key, value) for key, value in invalid_values.items())
            raise utils.ValidationException(error_msg)

    def configure(self, configuration=None):
        if not configuration:
            configuration = dict()
        config = dict(itertools.chain(self.CONFIG_TEMPLATE.items(), configuration.items()))
        super(Japanese, self).configure(config)
    
    @classmethod
    def find_following_working_weekday(cls, day, weekday):
        d = cls.CALENDAR.get_first_weekday_after(day, weekday)
        while cls.CALENDAR.is_holiday(d):
            d += datetime.timedelta(days=7)
        return d

    def get_weekday(self):
        weekday = self.config['WEEKDAY'][:3]
        weekday = getattr(cal, self.FRENCH_DAYS.get(weekday, weekday))
        return weekday

    def get_time(self):
        return datetime.datetime.strptime(self.config['TIME'], '%H:%M').time()

    def japanese(self):
        try:
            now = datetime.datetime.now()
            weekday = self.get_weekday()
            time_ = self.get_time()
            japanese_datetime = datetime.datetime.combine(self.find_following_working_weekday(now, weekday), time_)
            if japanese_datetime < now:
                japanese_datetime = datetime.datetime.combine(self.find_following_working_weekday(now + datetime.timedelta(days=1), weekday), time_)
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
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.log.exception('Error when trying to display when is the next Japanese: {}'.format(e))
            print('Error when trying to display when is the next Japanese: {}'.format(e))
            return 'Oups. J\'ai fait dans mon pantalon.'

    # Passing split_args_with=None will cause arguments to be split on any kind
    # of whitespace, just like Python's split() does
    @botcmd(split_args_with=None)
    def japonais(self, message, args):
        return self.japanese()

    @botcmd(split_args_with=None)
    def jap(self, message, args):

        return self.japanese()
