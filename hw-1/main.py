import pandas as pd


YEAR = 2021

df = pd.read_csv('fns_for_model.csv', sep=';')
income = df[df['year'] == YEAR]['income']

print("Mean:", income.mean())
print("Deviation:", income.std())
