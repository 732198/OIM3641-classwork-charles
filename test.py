from stock import Stock


aapl = Stock("AAPL", start="2026-09-29", end="2026-09-28")

nlfx = Stock("NLFX", start="2026-09-29", end="2026-09-28")

print(aapl.data)
fig = aapl.plot_performance()
fig.show()