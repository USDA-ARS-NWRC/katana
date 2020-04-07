import os

from katana import utils


class BaseData():
    """Base class for interacting with different data sourses
    """

    DATE_FORMAT = '%Y%m%d'

    def __init__(self, config, topo):

        self.config = config
        self.topo = topo

        self.start_date = self.config['time']['start_date']
        self.end_date = self.config['time']['end_date']
        self.out_dir = self.config['output']['out_location']

        # create an hourly time step between the start date and end date
        self.date_list = utils.daterange(self.start_date, self.end_date)

        # create a daily list between the start and end date
        self.day_list = utils.daylist(self.start_date, self.end_date)

    def initialize_data(self):
        """Initialize the data if needed
        """
        pass

    def output_day_folder(self, day):
        """Create a path to a folder for the given day

        Arguments:
            day {datetime} -- Datetime object for folder date
        """

        return os.path.join(self.out_dir,
                            'data{}'.format(
                                day.strftime(self.DATE_FORMAT)),
                            'wind_ninja_data')

    def make_output_day_folder(self, day):
        """Make the output day folder

        Arguments:
            day {datetime} -- Datetime object for folder date
        """

        out_dir_day = self.output_day_folder(day)

        # make output folder if it doesn't exist
        if not os.path.isdir(out_dir_day):
            os.makedirs(out_dir_day)

        return out_dir_day
