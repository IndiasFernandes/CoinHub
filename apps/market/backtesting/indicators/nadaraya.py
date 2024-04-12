import numpy as np

def nadaraya_watson_envelope(df, length=500, h=8, mult=3):
    n = np.arange(len(df))
    k = 2

    upper = np.zeros_like(df)
    lower = np.zeros_like(df)

    y = np.zeros(length)

    sum_e = 0

    for i in range(length):
        sum = 0
        sumw = 0

        for j in range(length):
            w = np.exp(-((i - j) ** 2) / (h ** 2 * 2))
            sum += df['close'][j] * w
            sumw += w

        y[i] = sum / sumw
        sum_e += abs(df['close'][i] - y[i])

    mae = sum_e / length * mult

    for i in range(1, length):
        y2 = y[i]
        y1 = y[i - 1]

        upper_level = y1 + mae
        lower_level = y1 - mae

    return y1 + mae, y1 - mae
