import datetime

# Class containing the South West temperature information
class englandSW_walesS(object):

    mean = {1: 4.8, 2: 4.6, 3: 6.5, 4: 8.2, 5: 11.2, 6:	13.9, 7: 15.9, 8: 15.7, 9: 13.6, 10: 10.6, 11: 7.4, 12:	5.2}

    max = {1: 7.5, 2: 7.6, 3: 9.8, 4: 12.2, 5: 15.4, 6: 18.0, 7: 20.0, 8: 19.8, 9: 17.5, 10: 13.8, 11: 10.4, 12: 8.0}

    min = {1: 2.1, 2: 1.7, 3: 3.2, 4: 4.2, 5: 7.0, 6: 9.6, 7: 11.7, 8: 11.7, 9: 9.8, 10: 7.4, 11: 4.5, 12: 2.4}
    

    def gettemperature(self, date):

        # month_and_day = datetime.datetime.strptime(date, '%d/%m/%Y') - not needed as the date is converted to datetime in start script

        month = int(date.strftime('%m'))

        mean_temp = self.mean[month]

        max_temp = self.max[month]

        min_temp = self.min[month]

        return mean_temp, max_temp, min_temp

# Class containing the Scotland North temperature information    
class scotlandN(object):
   
    mean = {1: 2.6, 2: 2.6, 3: 3.9, 4: 5.9, 5: 8.5, 6: 10.8, 7: 12.8, 8: 12.6,	9: 10.6, 10: 7.7, 11: 4.8, 12: 2.7}

    max = {1: 5.2, 2: 5.3, 3: 6.8, 4: 9.3, 5: 12.4, 6: 14.3, 7: 16.1, 8: 15.8, 9: 13.7, 10: 10.5, 11: 7.5, 12: 5.4}

    min = {1: 0.0, 2: -0.2, 3: 0.9, 4: 2.3, 5: 4.5, 6: 7.2, 7: 9.4, 8: 9.3, 9: 7.3,	10: 4.8, 11: 2.2, 12: 0.1}
    
    def gettemperature(self, date):

        month = int(date.strftime('%m'))

        mean_temp = self.mean[month]

        max_temp = self.max[month]

        min_temp = self.min[month]

        return mean_temp, max_temp, min_temp

# Class containing the Scotland East temperature information 
class scotlandE(object):

    mean = {1: 5.0, 2:5.3, 3: 7.3, 4: 10.0,	5: 13.1, 6: 15.6, 7: 17.7,	8: 17.4, 9: 14.7, 10: 11.0, 11:	7.5, 12: 5.1}

    max = {1: 4.9, 2: 5.2, 3: 7.3, 4: 9.9, 5: 13.0, 6: 15.5, 7: 17.6, 8: 17.2, 9: 14.6, 10: 11.0, 11: 7.5, 12: 5.1}

    min = {1: -0.6, 2: -0.5, 3: 0.6, 4: 2.1, 5: 4.5, 6: 7.4, 7: 9.4, 8: 9.2, 9: 7.2, 10: 4.5, 11: 1.7, 12: -0.6}
    
    def gettemperature(self, date):

        month = int(date.strftime('%m'))

        mean_temp = self.mean[month]

        max_temp = self.max[month]

        min_temp = self.min[month]

        return mean_temp, max_temp, min_temp

# Class containing the Scotland West temperature information 
class scotlandW(object):

    mean = {1: 2.2, 2: 2.4, 3: 4.0, 4: 6.1, 5: 8.8, 6: 11.5, 7: 13.6, 8: 13.3, 9: 11.0, 10: 7.8, 11: 4.7, 12: 2.3}

    max = {1: 5.8, 2: 6.0, 3: 7.8, 4: 10.4, 5: 13.8, 6: 15.9, 7: 17.5, 8: 17.1, 9: 14.8, 10: 11.6, 11: 8.4, 12: 6.2}

    min = {1: 0.7, 2: 0.6, 3: 1.6, 4: 3.0, 5: 5.4, 6: 8.1, 7: 10.1, 8: 10.0, 9: 8.1, 10: 5.6, 11: 3.0, 12: 0.8}
    
    def gettemperature(self, date):

        month = int(date.strftime('%m'))

        mean_temp = self.mean[month]

        max_temp = self.max[month]

        min_temp = self.min[month]

        return mean_temp, max_temp, min_temp

# Class containing the England North-East temperature information 
class englandE_NE(object):

    mean = {1: 3.4, 2: 3.6, 3: 5.6,	4: 7.5,	5: 10.4, 6: 13.2, 7: 15.5, 8: 15.4,	9: 13.0, 10: 9.7, 11: 6.1, 12: 3.6}

    max = {1: 6.2, 2: 6.6, 3: 9.1, 4: 11.5, 5: 14.7, 6: 17.5, 7: 20.0, 8: 19.7, 9: 17.0, 10: 13.1, 11: 9.1, 12: 6.4}

    min = {1: 0.7, 2: 0.6, 3: 2.0, 4: 3.4, 5: 5.9, 6: 8.8, 7: 10.9, 8: 10.8, 9: 8.9, 10: 6.2, 11: 3.2, 12: 0.9}
    
    def gettemperature(self, date):

        month = int(date.strftime('%m'))

        mean_temp = self.mean[month]

        max_temp = self.max[month]

        min_temp = self.min[month]

        return mean_temp, max_temp, min_temp

# Class containing the England North-West and North Wales temperature information 
class englandNW_walesN(object):

    mean = {1: 3.8,	2: 3.8, 3: 5.6, 4: 7.5, 5: 10.6, 6:	13.1, 7: 15.1, 8: 14.9, 9: 12.7, 10: 9.6, 11: 6.4, 12: 4.0}

    max = {1: 6.4, 2: 6.6, 3: 8.7, 4: 11.4, 5: 14.8, 6: 17.1, 7: 19.1, 8: 18.7, 9: 16.3, 10: 12.7, 11: 9.2, 12: 6.7}

    min = {1: 1.1, 2: 0.9, 3: 2.4, 4: 3.6, 5: 6.3, 6: 9.1, 7: 11.2, 8: 11.0, 9: 9.1, 10: 6.4, 11: 3.6, 12: 1.3}
    
    def gettemperature(self, date):

        month = int(date.strftime('%m'))

        mean_temp = self.mean[month]

        max_temp = self.max[month]

        min_temp = self.min[month]

        return mean_temp, max_temp, min_temp

# Class containing the Midlands temperature information 
class midlands(object):

    mean = {1: 3.9, 2: 3.9, 3: 6.1, 4: 8.1, 5: 11.2, 6: 14.1, 7: 16.3, 8: 16.1, 9: 13.6, 10: 10.1, 11: 6.6, 12:	4.1}

    max = {1: 6.7, 2: 7.0, 3: 9.7, 4: 12.5, 5: 15.9, 6: 18.8, 7: 21.1, 8: 20.8, 9: 17.8, 10: 13.7, 11: 9.6, 12: 6.9}

    min = {1: 1.0, 2: 0.8, 3: 2.4, 4: 3.7, 5: 6.5, 6: 9.4, 7: 11.5, 8: 11.3, 9: 9.3, 10: 6.5, 11: 3.5, 12: 1.3}
    
    def gettemperature(self, date):

        month = int(date.strftime('%m'))

        mean_temp = self.mean[month]

        max_temp = self.max[month]

        min_temp = self.min[month]

        return mean_temp, max_temp, min_temp

# Class containing the East Anglia temperature information 
class east_anglia(object):

    mean = {1: 4.2, 2: 4.3, 3: 6.6, 4: 8.7, 5: 11.9, 6:	14.8, 7: 17.2, 8: 17.2, 9: 14.6, 10: 11.0, 11: 7.1, 12:	4.5}

    max = {1: 7.1, 2: 7.4, 3: 10.3, 4: 13.1, 5: 16.6, 6: 19.6, 7: 22.2, 8: 22.1, 9: 19.0, 10: 14.7, 11: 10.2, 12: 7.3}

    min = {1: 1.4, 2: 1.1, 3: 2.8, 4: 4.2, 5: 7.1, 6: 10.0, 7: 12.2, 8: 10.1, 9: 10.1,	10: 7.3, 11: 4.0, 12: 1.7}
    
    def gettemperature(self, date):

        month = int(date.strftime('%m'))

        mean_temp = self.mean[month]

        max_temp = self.max[month]

        min_temp = self.min[month]

        return mean_temp, max_temp, min_temp

# Class containing the England South East / Central temperature information 
class englandSE_centralS(object):

    mean = {1: 4.6, 2: 4.5, 3: 6.8, 4: 8.8, 5: 12.0, 6:	14.9, 7: 17.1, 8: 17.0, 9: 14.5, 10: 11.1, 11: 7.4, 12:	5.0}

    max = {1: 7.5, 2: 7.7, 3: 10.5, 4: 13.2, 5: 16.7, 6: 19.6, 7: 22.0, 8: 21.8, 9: 18.9, 10: 14.8, 11: 10.7, 12: 7.9}

    min = {1: 1.7, 2: 1.4, 3: 3.0, 4: 4.3, 5: 7.3, 6: 10.1, 7: 12.2, 8: 12.1, 9: 10.1,	10: 7.4, 11: 4.2, 12: 2.0}
    
    def gettemperature(self, date):

        month = int(date.strftime('%m'))

        mean_temp = self.mean[month]

        max_temp = self.max[month]

        min_temp = self.min[month]

        return mean_temp, max_temp, min_temp