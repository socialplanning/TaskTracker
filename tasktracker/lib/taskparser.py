import re, time, datetime

class TaskParser:
    @classmethod
    def parse(cls, stuff):
        """
        Determine the format of the input to parse and
        pass it on to the appropriate parser to be parsed
        """
        import os
        format = os.popen("file %s" % stuff)
        format_output = format.read()        
        format.close()
        print "FORMAT: ", format_output
        if "vCalendar" in format_output:
            stuff = open(stuff, 'rb')
            data = stuff.read()
            stuff.close()
            return ICalParser()._parse(data)
    
        elif len([x in format_output for x in ("Microsoft Office", "OpenDocument Text", "Rich Text Format")]):
            conversion = os.popen("abiword --to txt %s" % stuff)
            conversion.close()
            converted_file = open("%s.txt" % stuff.split('.')[0], 'rb')
            stuff = converted_file.read()
            converted_file.close()
            return PlainTextParser()._parse(stuff) 
                        
        else:
            return PlainTextParser()._parse(stuff)

    def _parse(self, stuff):
        """
        Parse the input
        """
        pass

class ICalParser:
    def _parse(self, stuff):
        tasks = list()
        task = dict()
        for line in stuff.split('\n'):
            if "BEGIN:VTODO" in line.upper():
                task = dict()
            elif "SUMMARY" in line.upper():
                task['title'] = line.strip("SUMMARY:")
#            elif "STATUS" in line.upper():
#                task['status'] = line.strip("STATUS:")
            elif "DUE" in line.upper():
                deadline = line[line.find(":")+1:].split("T")[0]
                task['deadline'] = datetime.datetime(*time.strptime(deadline, "%Y%m%d")[0:3])
            elif "END:VTODO" in line.upper():
                if 'title' in task.keys():
                    tasks.append(task)
        return tasks

def smarter_strptime(date, *date_formats):
    if not date_formats:
        date_formats = ["%m/%d", "%m/%d/%y", "%m/%d/%Y",
                        "%m-%d", "%m-%d-%y", "%m-%d-%Y",
                        "%d/%m", "%d/%m/%y", "%d/%m/%Y",
                        "%d-%m", "%d/%m-%y", "%d-%m-%Y"]
    for format in date_formats:
        try:
            return datetime.datetime(*time.strptime(date, format)[0:3])
        except ValueError:
            pass
    raise ValueError("time data did not match any of the provided formats")

class PlainTextParser:
    date_extractor = re.compile(r'[\d]+(-|/)[\d]+(((-|/)[\d]+)*)')            
    
    def __init__(self, task_splitter='\n'):
        #self.field_splitter = re.compile("((:|-) *)+")
        self.task_splitter = task_splitter
        self.ordered_params = ('title')

    def _parse(self, stuff):
        tasks = list()
        for line in stuff.split(self.task_splitter):
            if line:
                datematch = self.date_extractor.search(line)
                if datematch:
                    date = datematch.group()
                    line = line.replace(date, "").strip()
                    date = smarter_strptime(date)
                else:
                    date = None                    
                
                tasks.append({'deadline': date, 'title': line})
        return tasks
