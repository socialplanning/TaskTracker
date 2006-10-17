class TaskParser:
    @classmethod
    def parse(cls, stuff):
        """
        Determine the format of the input to parse and
        pass it on to the appropriate parser to be parsed
        """
        return PlainTextTaskParser()._parse(stuff)

    def _parse(self, stuff):
        """
        Parse the input
        """
        pass

class PlainTextTaskParser:
    def __init__(self, field_splitter=':', task_splitter='\n'):
        self.field_splitter = field_splitter
        self.task_splitter = task_splitter
        self.ordered_params = ('title', 'owner')

    def _parse(self, stuff):
        tasks = list()
        for line in stuff.split(self.task_splitter):
            tasks.append(dict(zip(self.ordered_params, [p.strip() for p in line.split(self.field_splitter)])))
        return tasks
