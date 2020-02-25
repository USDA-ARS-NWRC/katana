import logging
import os
from subprocess import PIPE, Popen


class WindNinja:
    """Class that wraps the `WindNinja_cli`. Meant to facilitate
    a single run of WindNinja
    """

    def __init__(self, config, wn_cfg_file):
        """[summary]

        Arguments:
            config {dict} -- dictionary of config options
                            from the `wind_ninja` section
            wn_cfg_file {str} -- name of the configuration
                                file that will be passed to
                                the `WindNinja_cli`
        """
        self._logger = logging.getLogger(__name__)

        self.config = config
        self.wn_cfg_file = wn_cfg_file

        self.make_wn_cfg()

    def make_wn_cfg(self):
        """
        Write the config file options for the WindNinja program

        Result:
            Writes WindNinja config file
        """

        # write each line to config
        self._logger.info('Creating file {}'.format(self.wn_cfg_file))
        with open(self.wn_cfg_file, 'w') as f:
            for k, v in self.config.items():
                f.write('{} = {}\n'.format(k, v))

    def run_wind_ninja(self):
        """
        Create the command line call to run the WindNinja_cli
        """

        # construct call
        action = 'WindNinja_cli {}'.format(self.wn_cfg_file)

        # run command line using Popen
        self._logger.info('Running {}'.format(action))
        s = Popen(action, shell=True, stdout=PIPE, stderr=PIPE)

        # read output from commands
        while True:
            line = s.stdout.readline().decode()
            eline = s.stderr.readline().decode()
            self._logger.debug(line)

            # if the process is done
            if s.poll() is not None:
                break

            # error if WindNinja errors
            if "Exception" in eline:
                self._logger.error("WindNinja has an error")
                raise Exception(eline)

        if s.poll() != 0:
            self._logger.error(
                'WindNinja has an error, last output was: {}'.format(line))
            raise Exception(line)
