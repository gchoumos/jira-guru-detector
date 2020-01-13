import pickle
import numpy as np
from texttable import Texttable

## Reload the model
model = pickle.load(open('latest_model','rb'))

def detect_guru(text, n=10):
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
    print("Top {0} results:".format(n))
    for i in range(n):
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
            # ordered[i][2] = "Not likely"
            break
    t.header(['','Name','Guru Meter'])
    for i in range(1000):
        if ordered[i][1]*100 >= 2:
            t.add_row(['{0}.'.format(i+1),ordered[i][0],ordered[i][2]])
        else:
            break
        # print("{0}. {1} - {2}".format(i+1,ordered[i][0],ordered[i][2]))
        # print("{0}. {1} - {2:.2f}% - {3}".format(i+1,ordered[i][0],ordered[i][1]*100,ordered[i][2]))
    print(t.draw())

# regex for hexadecimal words to be removed \s([a-f]|[0-9]){5,}\s

