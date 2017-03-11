"""
Utility for plotting results
"""

import matplotlib.pyplot as plt
import pandas as pd

fig1, ax1 = plt.subplots(figsize=(10,  10))
data=pd.read_csv('summary.csv')
data.boxplot(['win percentage'], 'function', ax1)
fig1.savefig("compare_heuristics.png")
print(data)

fig2, ax2 = plt.subplots(figsize=(10,  10))
data=pd.read_csv('summary.csv')
data.boxplot(['average depth'], 'function', ax2)
fig2.savefig("compare_searchdepth.png")
