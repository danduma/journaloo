class DayOneXMLConverter(BaseReader):
    """
    A class for reading Day One XML files to JSON
    """

    def read(self, path):
        return [load_dayone_xml(path)]
