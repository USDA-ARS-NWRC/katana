import logging
import subprocess


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
        self._logger.info('Running "{}"'.format(action))

        with subprocess.Popen(
            action,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        ) as s:

            # WindNinja may not push errors to stderr so it's
            # hard to capture them properly and stream the results
            # Here, we will stream to the debug and store all the
            # output. Then write to error if WindNinja exits without
            # a 0 code.
            output = []
            for line in iter(s.stdout.readline, ""):
                self._logger.debug(line.rstrip())
                output.append(line.rstrip())

            # if errors then create an exception
            return_code = s.wait()
            if return_code:
                for line in output:
                    self._logger.error(line)
                raise Exception('WindNinja has an error')
                return False

            return True
