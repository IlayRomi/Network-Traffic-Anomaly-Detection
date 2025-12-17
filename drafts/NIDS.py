import pandas as pd


# Load dataset

train_path = "KDDTrain+.txt"
test_path = "KDDTest+.txt"

data_train = pd.read_csv(train_path)
data_train.head()
