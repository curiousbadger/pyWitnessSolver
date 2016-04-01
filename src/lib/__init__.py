from os.path import dirname, abspath
import logging

# TODO: Cleaner way to do this?
absolute_file_path=str(dirname(abspath(__file__)))
print('absolute_file_path', absolute_file_path)

lib_log=logging.getLogger(__name__)
lib_log.setLevel(logging.INFO)
# create file handler which logs even debug messages
lib_dbg_filehandler = logging.FileHandler('debug.log', mode='w')
lib_dbg_filehandler.setLevel(logging.DEBUG)
lib_inf_filehandler = logging.FileHandler('info.log', mode='w')
lib_inf_filehandler.setLevel(logging.INFO)

# create console handler with a higher log level
lib_consolehandler = logging.StreamHandler()
lib_consolehandler.setLevel(logging.INFO)
# create formatter and add it to the handlers
long_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
short_format = logging.Formatter('%(name)s - %(message)s')
#lib_dbg_filehandler.setFormatter(long_format)
lib_dbg_filehandler.setFormatter(short_format)
lib_inf_filehandler.setFormatter(short_format)
lib_consolehandler.setFormatter(short_format)

# add the handlers to the logger
#lib_log.addHandler(fh)
#lib_log.addHandler(ch)
