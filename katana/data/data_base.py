import os


class BaseData():
    """Base class for interacting with different data sourses
    """

    fmt_date = '%Y%m%d'

    def output_day_folder(self, day):
        """Create a path to a folder for the given day

        Arguments:
            day {datetime} -- Datetime object for folder date
        """

        return os.path.join(self.out_dir,
                            'data{}'.format(
                                day.strftime(self.fmt_date)),
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
