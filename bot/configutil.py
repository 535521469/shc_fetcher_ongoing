# -*- coding: utf-8 -*-
'''
Created on 2013-3-3
@author: Administrator

'''
from string import Formatter
from UserDict import UserDict

class ConfigFile(UserDict):
    '''
        _filepath : the config file path
        _configblock_vos:block vo
        _configblockkey__configblock_dict:{block name : block vo}
        _define_blockkey__rowkey_list_dict:{blockkey:[rowkey,..]}
        fileconten_list:filecontent list , split by '\n'
        parsed_config : {blockkey:{rowkey:rowvalue}}
    '''

    def __init__(self, filepath):
        self._filepath = filepath
        self._configblock_vos = [] 
        self._configblockkey__configblock_dict = {}
        self._define_blockkey__rowkey_list_dict = {} 
        self.parsed_config = {} 
        self.fileconten_list = []
        
    @staticmethod
    def readconfig(filepath):
        '''
        @summary: read config file and return the config dict
        @rtype:  {section:{key:value}}
        '''
        #=======================================================================
        # init an instance , and read the contents 
        #=======================================================================
        cf = ConfigFile(filepath)
        with open(filepath, u"r") as f:
            for line in f:
                cf.fileconten_list.append(line)
                
        cf.generate_configblocks()
        cf.build_define_blockkey__rowkey_list_dict()
        cf.parse()
        
        cf.data = cf.parsed_config
        
        return cf
        
    def generate_configblocks(self):
        '''
        @summary: set _configblock_vos and _configblockkey__configblock_dict
        '''
        blockkey__block_dict = {}
        blockkey = None
        for line in self.fileconten_list:
            line = unicode(line.strip()).replace(u'\ufeff', u'')
            if line.startswith(u"#"):
                continue
            if line.startswith(u"[") and line.endswith(u"]"):
                blockkey = line[1:-1].strip()
                blockkey__block_dict[blockkey] = []
            elif line:
                blockkey__block_dict[blockkey].append(line)
                
        else:
            for blockkey, configrow_list in blockkey__block_dict.iteritems():
                cb = ConfigBlock(self, blockkey, configrow_list)
                self._configblock_vos.append(cb)
                self._configblockkey__configblock_dict[blockkey] = cb
    
    def build_define_blockkey__rowkey_list_dict(self):
        '''
        @summary: set _define_blockkey__rowkey_list_dict
        '''
        d = {}
        for (k, v) in self._configblockkey__configblock_dict.iteritems():
            d[k] = v._configblockrow_dict.keys()
        self._define_blockkey__rowkey_list_dict = d 
    
    def parse(self):
        for bv in self._configblockkey__configblock_dict.itervalues():
            for rv in bv._configblockrow_dict.itervalues():
                rv.parse_row(self.parsed_config)
                
            
    def __str__(self):
#        return self._filecontent
        s = [u"file:{self._filepath}".format(**locals()), u"*"*50, ]
        for block in self.parsed_config.iterkeys():
            s.append(u"".join([u"[", block, u"]"]))
            for k, v in self.parsed_config[block].iteritems():
                s.append(u"".join([k, u"=", v, u""]))
        return u'\n'.join(s)
    
class ConfigBlock(object):
    
    def __init__(self, configfile, blockkey, configrow_list):
        self._configfile = configfile
        self._blockkey = blockkey
        self._configrow_list = configrow_list
        self._configrow_vos = []
        self._configblockrow_dict = {}
        self.generate_configblockrow()
        self.generate_configblockrow_dict()
        
    def generate_configblockrow_dict(self):
        self._configblockrow_dict = dict([(cr._rowkey.strip(), cr) 
                                          for cr in self._configrow_vos])
            
            
    def generate_configblockrow(self):
        for i in self._configrow_list:
            cbr = ConfigBlockRow(self, i)
            self._configrow_vos.append(cbr)
    
    def __str__(self):
        s = [u"blockvo : ***************** start \n"
                "blockkey : {self._blockkey}\n".format(**locals()), ]
        for cr in self._configrow_list:
            s.append(cr + u"\n")
        s.append(u"blockvo : ***************** end\n")
        return u"".join(s)
    
class ConfigBlockRow(object):
    
    def __init__(self, configblock, row):
        self._configblock = configblock
        self._row = row
        self._rowkey = u""
        self._configblockrowvalue = None
        self.generate_configblockvalue()
        
    def generate_configblockvalue(self):
        row = self._row.strip()
        k_eq_v_list = row.partition(u"=")
        if k_eq_v_list[1] == u"=":
            k, v = k_eq_v_list[0], k_eq_v_list[2]
            self._rowkey = k.strip()
            self._configblockrowvalue = ConfigBlockRowValue(self, v.strip())
    
    def __str__(self):
        s = [(u"BlockRowVO : ****************"
             u"*****start\n row:{self._row}".format(**locals()))]
        return u"".join(s)
    
    def parse_row(self, parsed_config):
        blockkey, rowkey = self._configblock._blockkey, self._rowkey
        if blockkey in parsed_config and rowkey in parsed_config[blockkey]:
            pass
        else:
            code = self._configblockrowvalue.get_plain_code()
            if blockkey in parsed_config:
                parsed_config[blockkey][rowkey] = code
            else :
                parsed_config[blockkey] = {rowkey:code}
            
class ConfigBlockRowValue(object):
    
    def __init__(self, configblockrow, configblockrowvalue):
        self._configblockrow = configblockrow
        self._configblockrowvalue = configblockrowvalue
        self._configblockrowvalueparsedtuple_vos = []
        self.generate_configblockrowvalueparsedtuple()
        
    def generate_configblockrowvalueparsedtuple(self):
        for literal_text, field_name, format_spec, conversion \
                    in Formatter().parse(self._configblockrowvalue):
            if not (field_name is None or len(field_name.split(u".")) == 2):
                self_block_key = self._configblockrow._configblock._blockkey
                field_name = self_block_key + u"." + field_name
            cbvpt = ConfigBlockRowValueParsedTuple(self, literal_text
                                                   , field_name, format_spec
                                                   , conversion)
            self._configblockrowvalueparsedtuple_vos.append(cbvpt)
    
    def get_plain_code(self, blockkey=None, rowkey=None):
        return u"".join(map(lambda x:x.join_values(blockkey, rowkey)
                            , self._configblockrowvalueparsedtuple_vos))
    
    def __str__(self):
        s = [(u"ConfigBlockRowValueVO : *********************start\n "
             u"rowvalue : {self._configblockrowvalue}".format(**locals()))]
        return u"".join(s)
    
class ConfigBlockRowValueParsedTuple(object):
    
    def __init__(self, configblockrowvalue, literal_text, field_name
                 , format_spec, conversion):
        self._configblockrowvalue = configblockrowvalue
        self._literal_text = literal_text
        self._field_name = field_name
        self._format_spec = format_spec
        self._conversion = conversion
        
        self._parsedkeyformat = ParsedKeyFormat(self, field_name)
    
    def __str__(self):
        s = [u"ConfigBlockRowValueParsedTuple : *******************start\n ", ]
        s.append(u" literal_text:{self._literal_text} \n".format(**locals()))
        s.append(u" field_name:{self._field_name}\n".format(**locals()))
        s.append(u" format_spec:{self._format_spec}\n".format(**locals()))
        s.append(u" conversion:{self._conversion}\n".format(**locals()))
        return u"".join(s)
    
    def join_values(self, blockkey=None, rowkey=None):
        return u"".join([self._literal_text
             , self._parsedkeyformat.get_plain_code(blockkey, rowkey)
             , u"!{self._conversion}".format(**locals()) 
                    if self._conversion else u""
             , u":{self._format_spec}".format(**locals()) 
                    if self._format_spec else u"" 
             ])
    
class ParsedKeyFormat(object):
    '''
    '''
    
    def __init__(self, configblockrowvalueparsedtuple, field_name):
        self._configblockrowvalueparsedtuple = configblockrowvalueparsedtuple
        self._field_name = field_name
#        self.plain_code = self.get_plain_code()
        
    def get_plain_code(self, blockkey=None, rowkey=None):
        if not self._field_name:
            return u""
        
        cbr = self._configblockrowvalueparsedtuple\
                            ._configblockrowvalue._configblockrow
                            
        if blockkey is None and rowkey is None :
            blockkey, rowkey = cbr._configblock._blockkey, cbr._rowkey
            pass
        else:
            assert blockkey != cbr._configblock._blockkey \
                and rowkey != cbr._rowkey , \
                (u" circular reference , blockkey : "
                "{blockkey}, rowkey : {rowkey}") .format(**locals())
        
#        dot_idx = self._field_name.find(u".")
        k_dot_v = self._field_name.partition(u".")
        if k_dot_v[1] == u".":
            block_key = k_dot_v[0].strip()
            
            config_file = cbr._configblock._configfile
            blockkey_rowkeylist = config_file._define_blockkey__rowkey_list_dict
            
            assert block_key in blockkey_rowkeylist , (u" block "
                "key not exists {block_key} ,"
                "from {blockkey}.{rowkey} ").format(**locals())
            
            row_key = k_dot_v[2].strip()
            assert row_key in blockkey_rowkeylist[block_key] , (u" row key not "
                "exists {block_key}.{row_key} ,from "
                "{blockkey}.{rowkey} ").format(**locals())
            
            if config_file.parsed_config.get(block_key, {}).get(row_key) is None:
                return config_file._configblockkey__configblock_dict\
                    [block_key]._configblockrow_dict[row_key]\
                        ._configblockrowvalue.get_plain_code(blockkey, rowkey)
            else:
                return config_file.parsed_config.get(block_key, {}).get(row_key)

if __name__ == '__main__':
    
    cf = ConfigFile.readconfig(r"E:\corleone\corleone_GitHub\crawl_secondhandcar\fetch58.cfg")
    print cf

#    a = u"{b[c]}"
#    x = {u"b":{u"c":33}}
#    print a.format(**x)
    
#    for i in cf._configblock_vos:
#        for j in i._configrow_vos:
#            print j._row
    

