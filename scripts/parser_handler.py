"""extend argparse to allow extra elements in is add option


"""

import argparse
class ParserHandler(argparse.ArgumentParser):
    """extend argparse to allow extra elements in is add option
    
    """

    def __init__(self, parser, info_dic):
        """simple class to allow defining extra properties (booleans actually)
        when adding arguments to the parser
        these will be returned in the info_dic
        
        Arguments:
            oject {[type]} -- [description]
            parser {namespace} -- the namespace to which arguments will be added
            info_dic {dictionary} -- used to return the results
    
        """
        self.parser = parser
        self.info_dic = info_dic
        self.keys = list(info_dic.keys())

    def add_argument(self, *args, **kwargs):
        # collect the extra flags and remove them from 
        # key words
        for kwarg in list(kwargs.keys()):
            if kwarg in self.keys:
                k_vals = self.info_dic.get(kwarg, [])
                dest = kwargs.get('dest')
                if dest:
                    k_vals.append(dest)
                kwargs.pop(kwarg)
        #super().add_argument(*args, **kwargs)
        self.parser.add_argument(*args, **kwargs)
                

