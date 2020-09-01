"""
Class to run Demeter model for all defined steps.

Copyright (c) 2017, Battelle Memorial Institute

Open source under license BSD 2-Clause - see LICENSE and DISCLAIMER

@author:  Chris R. Vernon (chris.vernon@pnnl.gov)
"""

import os.path as op
import sys
import time
import traceback

from demeter.config_reader import ReadConfig
from demeter.logger import Logger
from demeter.process import ProcessStep
from demeter.staging import Stage


class ValidationException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class Demeter(Logger):

    def __init__(self, config=None, root_dir=None):

        self.dir = root_dir
        self.ini = config
        self.c = None
        self.s = None
        self.process_step = None
        self.rg = None
        self.f = None

    @staticmethod
    def log_config(c, log):
        """
        Log validated configuration options.
        """
        for i in dir(c):

            # create configuration object from string
            x = eval('c.{0}'.format(i))

            # ignore magic objects
            if type(x) == str and i[:2] != '__':

                # log result
                log.debug('CONFIG: [PARAMETER] {0} -- [VALUE] {1}'.format(i, x))

    def make_logfile(self):
        """
        Make log file.

        :return                               log file object
        """
        # create logfile path and name
        self.f = op.join(self.dir, '{0}/logfile_{1}_{2}.log'.format(self.c.log_dir, self.c.scenario, self.c.dt))

        # parameterize logger
        self.log = Logger(self.f, self.c.scenario).make_log()

    def setup(self):
        """
        Setup model.
        """
        # instantiate config
        self.c = ReadConfig(config_file=self.ini, root_dir=self.dir)

        # instantiate log file
        self.make_logfile()

        # create log header
        self.log.info('START')

        # log validated configuration
        self.log_config(self.c, self.log)

        # prepare data for processing
        self.s = Stage(self.c, self.log)

    def execute(self):
        """
        Execute main downscaling routine.
        """
        # set start time
        t0 = time.time()

        try:

            # set up pre time step
            self.setup()

            # run for each time step
            for idx, step in enumerate(self.s.user_years):

                ProcessStep(self.c, self.log, self.s, idx, step)

        except:

            # catch all exceptions and their traceback
            e = sys.exc_info()[0]
            t = traceback.format_exc()

            # log exception and traceback as error
            try:
                self.log.error(e)
                self.log.error(t)

                # close all open log handlers
                Logger(self.f, self.c.scenario).close_logger(self.log)

            except AttributeError:
                print(e)
                print(t)

        finally:

            try:
                self.log.info('PERFORMANCE:  Model completed in {0} minutes'.format((time.time() - t0) / 60))
                self.log.info('END')
                self.log = None

            except AttributeError:
                pass


if __name__ == '__main__':

    # terminal option for running without installing demeter
    args = sys.argv[1:]

    if len(args) != 2:
        print("""USAGE:  Two arguments should be passed.
                        1) Full path file name with extension for config file and
                        2) the type of run you wish to conduct "standard" or "ensemble"
                    """)
        print('Exiting...')
        raise ValidationException

    # explode args
    ini = args[0]

    # run mode
    mode = args[1]

    if op.isfile is False:
        print('ERROR:  Config file not found.')
        print('You entered:  {0}'.format(ini))
        print('Please enter a full path file name with extension to config file and retry.')
        raise ValidationException

    if mode.lower() not in ('standard', 'ensemble'):
        print("""ERROR:  Run mode passed '{0}' not a valid option.  Either select 'standard' or 'ensemble' """.format(mode))
        print('Exiting...')
        raise ValidationException

    # instantiate and run demeter
    dm = Demeter(config=ini)
    dm.execute()

    # clean up
    del dm
