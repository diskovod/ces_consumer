
class ConsumerExtension:

    def get_from_file(self, filename):
        '''
        load list of hosts
        from file. If delete==true,
        then return list w/o dc, else
        return dict hostname and dc
        :param filename
        :return:list or dict with hosts
        '''
        with open(filename, 'r') as hosts:
                host_dict = {}
                for line in hosts:
                    host, dc = line.split("/")
                    host_dict[host] = dc

                return host_dict