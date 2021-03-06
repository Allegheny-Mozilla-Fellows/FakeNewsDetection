"""Class to train machine learning model to return classification report based
on subjectivity using user-specified model."""

import sklearn
from sklearn import svm
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pandas as pd
from . import preparedata as prep


# pylint: disable=C0103, C0301, E1101


class TrainingML():
    """Class for handling of both supervised learning models"""

    def __init__(self):
        """Class constructor for initialization"""

        train_df = pd.read_csv("./data/train.csv")

        test_df = pd.read_csv("./data/test.csv")

        train_df = train_df.drop(['id'], axis=1)
        test_df = test_df.drop(['id'], axis=1)

        # label = train_df["label"].values
        train_df = train_df.drop(['label'], axis=1)

        combined_tweets = pd.concat([train_df, test_df], axis=0)

        combined_tweets.text = combined_tweets.text.fillna('no data')
        combined_tweets['author'] = combined_tweets['author'].fillna('unknown')
        combined_tweets['title'] = combined_tweets['title'].fillna(combined_tweets['text'])
        # import datasets, call training

        # Vectorize textual data
        combined_tweets['author'] = prep.prepare_data(combined_tweets, 'author')
        combined_tweets['title'] = prep.prepare_data(combined_tweets, 'title')
        combined_tweets['text'] = prep.prepare_data(combined_tweets, 'text')
        self.tfidf = TfidfVectorizer(sublinear_tf=True, min_df=3, norm='l2', encoding='latin-1', ngram_range=(1, 2), stop_words='english')

        self.clf_NB = self.trainingNB(combined_tweets)
        self.clf_SVM = self.trainingSVM(combined_tweets)

    def trainingNB(self, data):
        """Utility function for training Multinomial NB based on combined dataset"""

        # Features = tweet
        x = data["tweet"]
        # Target = subject
        y = data["subject"]
        # Split into training and testing sets, and fit model
        X_train, self.X_test, y_train, self.y_test = sklearn.model_selection.train_test_split(x, y, test_size = 0.2)
        X_train_tfidf = self.tfidf.fit_transform(X_train)
        # Multinomial Naive Bayes
        self.clf = MultinomialNB().fit(X_train_tfidf, y_train)

        # get_classification_report(clf)

        return self.clf

    def trainingSVM(self, data):
        """Utility function for training linear SVM based on combined dataset"""

        # Features = tweet
        x = data["tweet"]
        # Target = subject
        y = data["subject"]
        # Split into training and testing sets, and fit model
        X_train, self.X_test, y_train, self.y_test = sklearn.model_selection.train_test_split(x, y, test_size = 0.2)
        X_train_tfidf = self.tfidf.fit_transform(X_train)
        # Linear SVM with regulization parameter
        self.clf = svm.SVC(kernel="linear", C=2)
        self.clf.fit(X_train_tfidf, y_train)

        return self.clf

    def predict_and_label(self, tweet, option):
        """Iteratively predict political subjectivity of each tweet through both models depending on option"""

        # labels tweet as political or not, returns subject for both models
        # tweet returned with label, option 0 = NB, option 1 = SVM

        if option == 0:
            tweet['label'] = self.clf_NB.predict(self.tfidf.transform([tweet['text']]))
        else:
            tweet['label'] = self.clf_SVM.predict(self.tfidf.transform([tweet['text']]))

        return tweet

    def get_classification_report_NB(self):
        """Utility function for generating a classification report for specified model"""

        print(classification_report(self.y_test, self.clf_NB.predict(self.tfidf.transform(self.X_test))))

    def get_classification_report_SVM(self):
        """Utility function for generating a classification report for specified model"""

        print(classification_report(self.y_test, self.clf_SVM.predict(self.tfidf.transform(self.X_test))))


# y_predict = clf.predict(count_vect.transform(X_test))
# y_predict2 = clf2.predict(count_vect.transform(X_test))
#
# print(classification_report(y_test, clf2.predict(count_vect.transform(X_test))))
#
# accNB = metrics.accuracy_score(y_test, y_predict)
# accSVM = metrics.accuracy_score(y_test, y_predict2)
# print("Accuracy NB : ", accNB, "\nAccuracy SVM : ", accSVM)

# Adapted from Zach Leonardo's senior comp project.
# Linked here: https://github.com/leonardoz15/Polarized
