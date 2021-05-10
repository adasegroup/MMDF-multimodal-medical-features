from annotation import *
import re
import io
import os
import itertools
from utils import process_dir_recur


class BratBase(object):
    def __init__(self, cat):
        self.bid = u''
        self.tp = u''
        self.cat = cat
    
    def __str__(self):
        return u"{}{}\t{}".format(self.cat, self.bid, self.tp)

#    def __str__(self):
#        return self.__unicode__().encode('utf8')
        

class BratEntity(BratBase, annotation.Span):
    def __init__(self):
        #super(BratEntity, self).__init__('T')
        super().__init__('T')
        self.form = u''
        self.spans = list()

    def __str__(self):
        return u"{} {}\t{}".format(super().__str__(), 
                                      u';'.join([u'{} {}'.format(span[0], span[1]) for span in self.spans]),
                                      #self.begin, 
                                      #self.end, 
                                      self.form)

#    def __str__(self):
#        return self.__unicode__().encode('utf8')
        
#    def __str__(self):
#        return "{} {} {}\t{}".format(super(BratEntity, self).__str__(), 
#                                    self.begin, 
#                                    self.end, 
#                                   self.form)

class BratRelation(BratBase):
    def __init__(self):
        #super(BratRelation, self).__init__('R')
        super().__init__('R')
        self.head = ""
        self.dep = ""
        
    def __str__(self):
        return "{} Arg1:T{} Arg2:T{}".format(super().__str__(),
                                           self.head,
                                           self.dep)
    

"""Loads brat annotations from file. Returns entities, relations."""
def load_brat_annotation_file(file_path):
    fl = open(file_path, 'r', encoding = 'utf8')
    
    annots_entities = list()
    annots_relations = list()
    
    for line in fl:
        cols = line.strip().split(u'\t')
        
        annot_id = cols[0]
        annot_type = annot_id[0]
        
        if annot_type == 'R':
            annot = BratRelation()
            annot.bid = annot_id[1:]
            
            annot_props = re.split(' ', cols[1])
            annot.tp = annot_props[0]
            
            arg_str = annot_props[1:]
            args = {e.split(':')[0] : e.split(':')[1] for e in arg_str}
            
            annot.head = args[u'Arg1'][1:]
            annot.dep = args[u'Arg2'][1:]
            
            annots_relations.append(annot)
            
        elif annot_type == u'T':
            annot = BratEntity() 
            annot.bid = annot_id[1:]
            
            annotProps = re.split(u";| ", cols[1])
            annot.tp = annotProps[0]
            annot.begin = int(annotProps[1])
            annot.end = int(annotProps[-1])
            annot.form = cols[2] if len(cols) > 2 else ''
            annot.spans = [(int(annotProps[i]), int(annotProps[i + 1])) for i in range(1, len(annotProps[1:]), 2)]
            
            annots_entities.append(annot)
            
        else:
            continue
    
    fl.close()
         
    return annots_entities, annots_relations


def load_brat_annotation_dir(dir_path, recur = False):
    annotations = dict()
    
    def load_one_file(file_path, annotations):
        more_ent, more_rel = load_brat_annotation_file(file_path)
        annotations[os.path.abspath(file_path)] = {'entities' : more_ent, 'relations' : more_rel}
        #annotations[os.path.splitext(file_path)[0][dirname(dir_path): ]] = {'entities' : more_ent, 
        #                                                                'relations' : more_rel}
    
    if not recur:
        for file_name in os.listdir(dir_path):
            if not file_name.endswith(".ann"):
                continue

            file_path = os.path.join(dir_path, file_name)
            load_one_file(file_path, annotations)
            
        return annotations
    else:
        process_dir_recur(dir_path, output_dir ='', allowed_pattern = '.+\.ann', 
                          f_func = lambda inf, outf: load_one_file(inf, annotations), 
                          create_dir = False)
        return annotations


def save_list_of_brat_objects(lst, output_file_path):
    with open(output_file_path, 'w', encoding = 'utf8') as f:
        for obj in lst:
            print(str(obj), file = f)
            #print >>f, unicode(obj)

            
get_next_id = itertools.count().__next__
class IdGenerator:
    def __init__(self, start = 0):
        self._iter = itertools.count(start)
    
    def get_next_id(self):
        return self._iter.__next__()
