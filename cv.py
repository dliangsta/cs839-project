import json
import pickle
from sklearn.model_selection import KFold
from classify import *
import argparse

class CrossValidator:
    def __init__(self, n_splits):
        self.n_splits = n_splits
        self.clfs = []
        self.accuracies = []
        self.precisions = []
        self.recalls = []
        self.f1s = []

        # The same statistics (with the same order) as the output of Classifier.classify().
        self.statistics = [self.accuracies, self.precisions, self.recalls, self.f1s]
        self.statistics_names = ['accuracy', 'precision', 'recall', 'f1']

    def add_classifier(self, clf):
        self.clfs.append(clf)
        [statistic.append([]) for statistic in self.statistics]

    def cross_validate(self, instances, whitelist=None, blacklist=None):
        kf = KFold(n_splits=self.n_splits)
        kf.get_n_splits(instances)

        for i, (train_indices, test_indices) in enumerate(kf.split(instances)):
            print('fold: %d / %d' % (i, self.n_splits))
            for j, clf in enumerate(self.clfs):
                results = clf.classify(instances=instances, 
                                          whitelist=whitelist,
                                          train_indices=train_indices,
                                          test_indices=test_indices)
                output_string = clf.clf_name

                for k in range(len(results)):
                    self.statistics[k][j].append(results[k])
                    output_string += ' %s: %f' % (self.statistics_names[k], results[k])
                
        print('\n\nFinal results.')
        for i, clf in enumerate(self.clfs):
            output_string = clf.clf_name
            statistics_means = [np.mean(statistic[i]) for statistic in self.statistics]
            for j in range(len(self.statistics)):
                output_string += ' %s: %f' % (self.statistics_names[j], statistics_means[j])
            print(output_string)

        print('Best classifier: ' + 
            self.clfs[np.argmax([np.mean(statistic) for statistic in self.statistics[3]])].clf_name)
            


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--n_splits', type=int, default=5, help='number of splits for cross-validation')
    args = parser.parse_args()

    with open('data/I_instances.pkl','rb') as f:
        instances = np.asarray(pickle.load(f))
    with open('data/cryptocurrencies_list.json') as f:
        cryptocurrencies = json.load(f)
    with open('data/cryptocurrency_abbreviations_list.json') as f:
        cryptocurrency_abbreviations = json.load(f)

    whitelist = [word.lower() for word in cryptocurrencies[:25] + cryptocurrency_abbreviations[:25]]

    cross_validator = CrossValidator(n_splits=args.n_splits)
    cross_validator.add_classifier(Classifier('dt'))
    cross_validator.add_classifier(Classifier('rf'))
    cross_validator.add_classifier(Classifier('svm'))
    cross_validator.add_classifier(Classifier('lir'))
    cross_validator.add_classifier(Classifier('lor'))
    cross_validator.cross_validate(instances, whitelist)

if __name__ == '__main__':
    main()
    