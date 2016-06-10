import pprint


class Stats(object):

    def __init__(self):
        self.stats = {}

    def add(self,key,value=None):
        if value is None:
            #meaning we are just doing a count
            self.stats[key] = self.stats.get(key,0) + 1
        else:
            #We are adding a value, we will keep a count, min, and max
            stat_data = self.stats.get(key,{'min':float('inf'),'max':0,'count':0,'total':0})
            stat_data['min'] = min(stat_data['min'],value)
            stat_data['max'] = max(stat_data['min'],value)
            stat_data['count'] = stat_data['count'] + 1
            stat_data['total'] += value
            self.stats[key] = stat_data

    def compute_mean(self):
        for key in self.stats:
            if type(self.stats[key]) is dict:
                stat_data = self.stats[key]
                if stat_data['count'] != 0:
                    stat_data['mean'] = stat_data['total'] / stat_data['count']
                    self.stats[key] = stat_data

    def print(self):
        """

        :rtype: None
        """
        self.compute_mean()
        pprint.pprint(self.stats)