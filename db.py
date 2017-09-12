import psycopg2
import os
import sys

if len(sys.argv) < 2:
    print "No config file provided! Aborting"
    sys.exit()

cfg_path=sys.argv[1]

cfg = ConfigObj(cfg_path)

# set defaults if not defined
if 'dbhost' not in cfg.keys():
    cfg['dbhost']='dbserver'
if 'database' not in cfg.keys():
    cfg['database']='fields'
if 'dbtable' not in cfg.keys():
    cfg['dbtable']='testtable'


conn = psycopg2.connect('postgres://{}:{}@{}/{}'.format(os.environ['POSTGIS_USER'],os.environ['POSTGIS_PASSWORD'],cfg['dbserver'],cfg['database']))

cur = conn.cursor()
