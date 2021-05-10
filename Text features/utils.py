import re
import os
import logging

def process_dir_recur(input_dir, output_dir, allowed_pattern, 
                      f_func, create_dir = True, logger=logging.getLogger()):
    for root, subdirs, files in os.walk(input_dir):
        for fname in files:
            fpath = os.path.join(root, fname)

            if os.path.isfile(fpath) and re.match(allowed_pattern, fname):
                logger.info(os.path.join(root, fname))
                
                tail = root[len(input_dir):]
                output_dir_path = os.path.join(output_dir, tail)
                if create_dir:
                    if not os.path.exists(output_dir_path):
                        os.makedirs(output_dir_path)
                    
                f_func(fpath, output_dir_path)
                