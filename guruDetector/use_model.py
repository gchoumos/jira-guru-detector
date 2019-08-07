import pickle
import numpy as np

## Reload the model
model = pickle.load(open('model_1_5310.save','rb'))

def detect_guru(text):
    test = np.dstack([
        text
    ])
    test = np.array([t[0] for t in test])
    y = model.predict_proba(test)
    y_pred = model.predict(test)
    test_labels = model.classes_
    test_probs = y
    ordered = [[test_labels[i],test_probs[0][i]] for i in range(test_labels.shape[0])]
    ordered.sort(key=lambda x: x[1],reverse=True)
    n = 10
    print("Top {0} results:".format(n))
    for i in range(n):
        print("{0}. {1} - {2:.2f}%".format(i+1,ordered[i][0],ordered[i][1]*100))

# regex for hexadecimal words to be removed \s([a-f]|[0-9]){5,}\s