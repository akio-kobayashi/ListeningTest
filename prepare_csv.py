import os, sys
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=str, default='output.csv')
args = parser.parse_args()

cwd=os.getcwd()

entries = {'key':[], 'path': []}
lines = sys.stdin.readlines()
for line in lines:
    key = os.path.splitext(os.path.basename(line.strip()))[0]
    entries['key'].append(key)
    entries['path'].append(os.path.join(cwd, line.strip()))

df = pd.DataFrame.from_dict(entries, orient='columns')
df.sort_values('key').to_csv(args.output, index=False)
