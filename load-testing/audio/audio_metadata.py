import argparse
import os
import json
from tinytag import TinyTag

parser = argparse.ArgumentParser(description='Extract metadata from audio files')
parser.add_argument('-f', '--file', help='Audio file name', required=True)
args = parser.parse_args()


def extract_metadata(_file):
    try:
        f = _file
        fname, fext = os.path.splitext(_file)
        tag = TinyTag.get(f)
        json_to_export = {
            "FILE": f,
            "NAME": fname,
            "EXTENSION": fext,
            "DURATION": tag.duration
        }

        with open('{}.json'.format(fname), 'w') as outfile:
            outfile.write(json.dumps(json_to_export))

    except Exception as e:
        print(e)
        pass

if args.file not in os.listdir(os.getcwd()):
    for _file in os.listdir(os.getcwd()):
        extract_metadata(_file)
else:
    extract_metadata(args.file)
