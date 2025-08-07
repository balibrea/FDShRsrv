import os
from datetime import datetime, timedelta, date

# Paths to the directories for each FD
LL = "/Raid/data/Fd/FD-LosLeones/eyepc/"
LM = "/Raid/data/Fd/FD-LosMorados/eyepc/"
LA = "/Raid/data/Fd/FD-LomaAmarilla/eyepc/"
CO = "/Raid/data/Fd/FD-Coihueco/eyepc/"
HE = "/Raid/data/Fd/FD-Heat/eyepc/"


class Shift:
    def __init__(self, start_date, end_date):
        self.overview = ""
        self.shifters = []
        self.start_date = start_date
        self.end_date = end_date
        self.shift_data = {
            'LL':[],
            'LM':[],
            'LA':[],
            'CO':[],
            'HE':[]
        }

        self.plots_link = ""
        self.overleaf_link = ""
        self.report_link = ""
        self.log = []
        self.done = False

    def ShiftDays(self, start_date, end_date):
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        days = []

        now = start
        while now <= end:
            # Formatear la fecha y agregarla a la lista
            days.append(now.strftime("%m-%d"))
            # Avanzar un día
            now += timedelta(days=1)

            # Populate data (text, color)
            d = list(self.shift_data.keys())
            t = ["", "green"] # Placeholder for text, color, daq time, run files
            for i in range(5):
                self.shift_data[d[i]].append(t)

        return days
    
    def RunData(self, file_name):
        try:
            # Get the creation time  
            creation_time = os.path.getctime(file_name)
            # Convert to a readable format  
            creation_date = datetime.fromtimestamp(creation_time)
            return creation_date  
        except FileNotFoundError:
            return f"File '{file_name}' not found."
        except Exception as e:
            return str(e)
        
    def GetRunFiles(self, date, FD):
        
        day_path = os.path.join(
            FD,
            str(date.year),
            f"{date.month:02}",
            f"{date.day:02}",
            "data"
        )
    
        if not os.path.isdir(day_path):
            print("invalid!")
            return []  # No data for that day

        return [
            os.path.join(day_path, f)
            for f in os.listdir(day_path)
            if os.path.isfile(os.path.join(day_path, f))
        ]
        
        

class Shifter:
    def __intit__(self, name, mail, institution, country):
        self.name = name
        self.mail = mail
        self.institution = institution
        self.country = country


#test Shift class
if __name__ == "__main__":
    shift = Shift("2025-04-19", "2025-05-05")
    #print(shift.ShiftDays("2025-04-19", "2025-05-05"))
    #print(shift.shift_data)
    print(shift.GetRunFiles(date(2025,4,19), HE))

    print(shift.RunData(shift.GetRunFiles(date(2025,4,19), LL)[0]))
