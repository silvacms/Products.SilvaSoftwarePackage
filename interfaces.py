from Interface import Base

class ISilvaSoftwareFile(Base):
    """A Silva Software File is a mixin for File objects

        It makes the file object send a notification to a service
        somewhere so that can keep track of a logfile (and show some
        statistics etc.)
    """

    def index_html(view_path):
        """download the file

            will do logging before the file is forwarded
        """
