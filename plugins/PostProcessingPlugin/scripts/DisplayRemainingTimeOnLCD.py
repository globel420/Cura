# Cura PostProcessingPlugin
# Author:   Mathias Lyngklip Kjeldgaard
# Date:     July 31, 2019
# Modified: ---

# Description:  This plugin displayes the remaining time on the LCD of the printer
#               using the estimated print-time generated by Cura.




from ..Script import Script

import re
import datetime


class DisplayRemainingTimeOnLCD(Script):

    def __init__(self):
        super().__init__()


    def getSettingDataString(self):
        return """{
            "name":"Disaplay Remaining Time on LCD",
            "key":"DisplayRemainingTimeOnLCD",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "TurnOn":
                {
                    "label": "Enable",
                    "description": "When enabled, It will write Time Left: HHMMSS on the display",
                    "type": "bool",
                    "default_value": false
                }
            }
        }"""

    def execute(self, data):
        if self.getSettingValueByKey("TurnOn"):
            total_time = 0
            total_time_string = ""
            for layer in data:
                layer_index = data.index(layer)
                lines = layer.split("\n")
                for line in lines:
                    if line.startswith(";TIME:"):
                        # At this point, we have found a line in the GCODE with ";TIME:"
                        # which is the indication of total_time. Looks like: ";TIME:1337", where
                        # 1337 is the total print time in seconds.
                        line_index = lines.index(line)          # We take a hold of that line
                        split_string = re.split(":", line)      # Then we split it, so we can get the number

                        string_with_numbers = "{}".format(split_string[1])      # Here we insert that number from the
                                                                                # list into a string.
                        total_time = int(string_with_numbers)                   # Only to contert it to a int.

                        m, s = divmod(total_time, 60)    # Math to calculate
                        h, m = divmod(m, 60)             # hours, minutes and seconds.
                        total_time_string = "{:d}h{:02d}m{:02d}s".format(h, m, s)           # Now we put it into the string
                        lines[line_index] = "M117 Time Left {}".format(total_time_string)   # And print that string instead of the original one




                    elif line.startswith(";TIME_ELAPSED:"):

                        # As we didnt find the total time (";TIME:"), we have found a elapsed time mark
                        # This time represents the time the printer have printed. So with some math;
                        # totalTime - printTime = RemainingTime.
                        line_index = lines.index(line)          # We get a hold of the line
                        list_split = re.split(":", line)        # Again, we split at ":" so we can get the number
                        string_with_numbers = "{}".format(list_split[1])   # Then we put that number from the list, into a string

                        current_time = float(string_with_numbers)       # This time we convert to a float, as the line looks something like:
                                                                        # ;TIME_ELAPSED:1234.6789
                                                                        # which is total time in seconds

                        time_left = total_time - current_time   # Here we calculate remaining time
                        m1, s1 = divmod(time_left, 60)          # And some math to get the total time in seconds into
                        h1, m1 = divmod(m1, 60)                 # the right format. (HH,MM,SS)
                        current_time_string = "{:d}h{:2d}m{:2d}s".format(int(h1), int(m1), int(s1))   # Here we create the string holding our time
                        lines[line_index] = "M117 Time Left {}".format(current_time_string)           # And now insert that into the GCODE


                # Here we are OUT of the second for-loop
                # Which means we have found and replaces all the occurences.
                # Which also means we are ready to join the lines for that section of the GCODE file.
                final_lines = "\n".join(lines)
                data[layer_index] = final_lines
        return data