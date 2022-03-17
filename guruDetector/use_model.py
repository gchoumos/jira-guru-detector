import pickle
import numpy as np
from texttable import Texttable

## Reload the model
model = pickle.load(open('latest_model','rb'))

def detect_guru(text, n=-1):
    t = Texttable()
    test = np.dstack([
        text
    ])
    test = np.array([t[0] for t in test])
    y = model.predict_proba(test)
    y_pred = model.predict(test)
    test_labels = model.classes_
    test_probs = y
    ordered = [[test_labels[i],test_probs[0][i],test_probs[0][i]] for i in range(test_labels.shape[0])]
    ordered.sort(key=lambda x: x[1],reverse=True)
    for i in range(len(ordered)):
        if ordered[i][1]*100 >= 50:
            ordered[i][2] = "Absolute Guru"
        elif ordered[i][1]*100 >= 25:
            ordered[i][2] = "Guru"
        elif ordered[i][1]*100 >= 20:
            ordered[i][2] = "*****"
        elif ordered[i][1]*100 >= 15:
            ordered[i][2] = "****"
        elif ordered[i][1]*100 >= 10:
            ordered[i][2] = "***"
        elif ordered[i][1]*100 >= 4:
            ordered[i][2] = "**"
        elif ordered[i][1]*100 >= 2:
            ordered[i][2] = "*"
        else:
            ordered[i][2] = "Low probability compared to the rest"
    if n < 1:
        print("Top results:")
    else:
        print("Top {0} results:".format(n))
    t.header(['','Name','Guru Meter'])
    for i in range(len(ordered)):
        if (n < 1 and int(ordered[i][1]*100) >= 2) or i < n:
            t.add_row(['{0}.'.format(i+1),ordered[i][0],ordered[i][2]])
        else:
            break
        # print("{0}. {1} - {2}".format(i+1,ordered[i][0],ordered[i][2]))
        # print("{0}. {1} - {2:.2f}% - {3}".format(i+1,ordered[i][0],ordered[i][1]*100,ordered[i][2]))
    print(t.draw())

# regex for hexadecimal words to be removed \s([a-f]|[0-9]){5,}\s

