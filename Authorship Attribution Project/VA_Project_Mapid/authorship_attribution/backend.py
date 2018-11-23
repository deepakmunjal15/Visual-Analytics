import os
from nltk.stem import PorterStemmer
import re
from nltk.corpus import stopwords
import math
from sklearn.cluster import AgglomerativeClustering


# Training Data

def readFiles(path):
    """
    Read text files
    :param path: path files
    :return: return text and author names
    """
    files_text = []
    author_names = []
    for root, dirs, files in os.walk(path):
        directory = os.path.basename(root)
        author_names.append(directory)
        concat_data = ""
        for file in files:
            concat_data = concat_data + " " + open(root + "/" + file, 'r').read() + " "
        files_text.append(concat_data)
    author_names.pop(0)
    files_text.pop(0)
    return files_text, author_names


def pre_process(files_text):
    """
    Pre-process the text by removing stop words, punctuation, convert the text lowercase and stemming
    :param files_text: text to pre process
    :return: pre-processed text
    """
    cachedStopWords = stopwords.words("english")
    porter = PorterStemmer()
    for i in range(len(files_text)):
        f = files_text[i]
        f = re.sub(r'[?|$|.|!|,|\'|"|+|-|_|\(|\)|*|\^|#|@|~|`|/|;|:|<|>|-|\d+]', r'', f)
        f = f.lower()
        files_text[i] = ' '.join([porter.stem(word) for word in f.split() if word not in cachedStopWords])
    return files_text


def make_n_grams(n, files_text):
    """
    Make n grams
    :param n: integer signifying n in n grams
    :param files_text: text
    :return: count, text_trigrams_matrix_unique, count_without_normalized
    """
    n_gram_counter = []
    for e in range(len(files_text)):
        b = files_text[e]
        n_gram_counter.append(len(b) - n + 1)

    col_length = max(n_gram_counter)

    text_trigrams_matrix = [["" for x in range(col_length)] for y in range(len(files_text))]
    text_trigrams_matrix1 = []
    count1 = []
    for e in range(len(files_text)):
        b = files_text[e]
        count_dic = {}
        text_trigrams_matrix1.append([])
        count1.append([])
        for i in range(len(b) - n + 1):
            s = b[i:i + n]
            text_trigrams_matrix1[e].append(s)
            if s in count_dic:
                count_dic[s] += 1
            else:
                count_dic[s] = 1
        count1[e].append(count_dic)

    text_trigrams_matrix = text_trigrams_matrix1

    text_trigrams_matrix_unique = [["" for x in range(col_length)] for y in range(len(files_text))]
    count = [[0 for x in range(col_length)] for y in range(len(files_text))]

    for x in range(len(text_trigrams_matrix)):
        text_trigrams_matrix_unique[x] = list(sorted(set(text_trigrams_matrix[x])))
        count.append([])
        for y in range(len(text_trigrams_matrix_unique[x])):
            count[x][y] = count1[x][0][text_trigrams_matrix_unique[x][y]]

    for m in range(len(count)):
        count[m] = [p for p in count[m] if p != 0]

    count_without_normalized = []
    for x in count:
        count_without_normalized.append(x[:])

    for a in range(len(count)):
        for b in range(len(count[a])):
            if count[a][b] == 0:
                break
            count[a][b] = float(count[a][b]) / float(sum(count[a]))

    return count, text_trigrams_matrix_unique, count_without_normalized


def make_force_backend(count, text_trigrams_matrix_unique, count_test,
                       text_trigrams_matrix_unique_test, author_names, features, author_name_test):
    """
     Make force layout
    :param count: total count
    :param text_trigrams_matrix_unique: unique n grams
    :param count_test: test count
    :param text_trigrams_matrix_unique_test: total test grams
    :param author_names: author names
    :param features: number of features
    :param author_name_test: test author names
    :return: force layout data
    """
    print("Author finding")
    print(len(text_trigrams_matrix_unique_test[0]))
    print(len(text_trigrams_matrix_unique[0]))
    print(len(list(sorted(set(text_trigrams_matrix_unique_test[0] + text_trigrams_matrix_unique[0])))))

    author_score = get_author_score(count, text_trigrams_matrix_unique, count_test, text_trigrams_matrix_unique_test,
                                    author_names, features)

    confusion_matrix = [[0 for x in range(len(author_score[0]))] for y in range(len(author_score))]

    for p in range(len(author_score)):
        confusion_matrix[p][author_score[p].index(min(author_score[p]))] = 1

    print('confusion_matrix is :\n')
    print(confusion_matrix)

    add = 0
    for q in range(len(confusion_matrix)):
        if confusion_matrix[q][q] == 1:
            add = add + 1

    accuracy = float(add) / float(len(confusion_matrix))
    print('accuracy is : %.2f' % (accuracy))

    ind = []
    print("Count Test" + str(len(count_test)))
    element_count = int(len(count_test) / 2)
    for q in range(element_count):
        ind.append("D" + str(q + 1))

    force_data = {}
    nodes = []

    i = 1
    for a in author_names:
        nodes_item = {'name': a, 'group': i}
        nodes.append(nodes_item)
        i += 1

    force_data['nodes'] = nodes

    if author_names[0] == "Test Author":
        author_score[0].insert(0, min(author_score[0]))

    links = []
    i = 0
    for a_s in author_score:
        j = 0
        print(author_names[i])
        if author_names[i] in author_name_test:
            factor, min_val = get_factor_and_max(a_s)
            for item_score in a_s:
                n_s = (item_score - min_val) * factor
                print("Item score " + str(item_score) + " Normalize score " + str(n_s))
                if n_s >= .6:
                    links_item = {'source': i, 'target': j, 'value': n_s}
                    links.append(links_item)
                j += 1
        i += 1

    force_data['links'] = links

    common = [[0 for x in range(len(text_trigrams_matrix_unique))] for y in
              range(len(text_trigrams_matrix_unique_test))]
    for x in range(len(text_trigrams_matrix_unique_test)):
        for y in range(len(text_trigrams_matrix_unique)):
            set_2 = frozenset(text_trigrams_matrix_unique[y])
            array = [p for p in text_trigrams_matrix_unique_test[x][0:features] if
                     p in text_trigrams_matrix_unique[y][0:features]]
            top10 = array[:10]
            common[x][y] = top10

    return force_data


def prepare_bar(count, text_trigrams_matrix_unique, count_test,
                text_trigrams_matrix_unique_test, author_names, features):
    """
    Make bar graph
    :param count: total count
    :param text_trigrams_matrix_unique: unique n grams
    :param count_test: test count
    :param text_trigrams_matrix_unique_test: total test grams
    :param author_names: author names
    :param features: number of features
    :return: bar graph data
    """
    print("Author finding")
    author_score = get_author_score(count, text_trigrams_matrix_unique, count_test, text_trigrams_matrix_unique_test,
                                    author_names, features)

    ind = []
    print("Count Test" + str(len(count_test)))
    element_count = int(len(count_test) / 2)
    for q in range(element_count):
        ind.append("D" + str(q + 1))

    bar_data = {}
    i = 0
    for aut in ind:
        bar_data[aut] = [1 - ((float(k) - max(author_score[i])) / (min(author_score[i]) - max(author_score[i])))
                         for k in author_score[i]]
        i += 1
    return bar_data


def find_author_live(count, text_trigrams_matrix_unique, count_test,
                     text_trigrams_matrix_unique_test, author_names, features):
    """
    Find author live
    :param count:  count of ngrams
    :param text_trigrams_matrix_unique: unique n grams
    :param count_test: count of test data n grams
    :param text_trigrams_matrix_unique_test:  unique n grams of test
    :param author_names: name of known authors
    :param features: features to be taken
    :return: dictionary of author names and score
    """
    author_score = get_author_score(count, text_trigrams_matrix_unique, count_test, text_trigrams_matrix_unique_test,
                                    author_names, features)

    return dict(zip(author_names, author_score[0]))


def get_author_score(count, text_trigrams_matrix_unique, count_test,
                     text_trigrams_matrix_unique_test, author_names, features):
    """
    Find author score
    :param count:  count of ngrams
    :param text_trigrams_matrix_unique: unique n grams
    :param count_test: count of test data n grams
    :param text_trigrams_matrix_unique_test:  unique n grams of test
    :param author_names: name of known authors
    :param features: features to be taken
    :return: dictionary of author names and score
    """
    author_score = [[0 for x in range(len(text_trigrams_matrix_unique))] for y in
                    range(len(text_trigrams_matrix_unique_test))]

    for x in range(len(text_trigrams_matrix_unique_test)):
        for y in range(len(text_trigrams_matrix_unique)):
            temp = list(sorted(
                set(text_trigrams_matrix_unique_test[x][0:features] + text_trigrams_matrix_unique[y][0:features])))
            tot = 0
            for z in range(len(temp)):
                if temp[z] in text_trigrams_matrix_unique_test[x]:
                    f1 = count_test[x][text_trigrams_matrix_unique_test[x].index(temp[z])]
                else:
                    f1 = 0
                if temp[z] in text_trigrams_matrix_unique[y]:
                    f2 = count[y][text_trigrams_matrix_unique[y].index(temp[z])]
                else:
                    f2 = 0
                tot = math.pow((float(2 * (f1 - f2)) / float(f1 + f2)), 2) + float(tot)
            author_score[x][y] = float("{0:.2f}".format(tot))
    print('Author Score')
    return author_score


def get_common_ngrams(text_trigrams_matrix_unique, text_trigrams_matrix_unique_test, features):
    """
    Get common n grams
    :param text_trigrams_matrix_unique: unique trigrams
    :param text_trigrams_matrix_unique_test:  unique test trigrams
    :param features: number of features
    """
    common = [[0 for x in range(len(text_trigrams_matrix_unique))] for y in
              range(len(text_trigrams_matrix_unique_test))]

    for x in range(len(text_trigrams_matrix_unique_test)):
        for y in range(len(text_trigrams_matrix_unique)):
            set_2 = frozenset(text_trigrams_matrix_unique[y])
            array = [p for p in text_trigrams_matrix_unique_test[x][0:features] if
                     p in text_trigrams_matrix_unique[y][0:features]]
            common[x][y] = array[:20]
    return text_trigrams_matrix_unique


def get_author_score_clustering(count, text_trigrams_matrix_unique, features, num_clusters):
    """
    Find author score for clustering
    :param count:  count of ngrams
    :param text_trigrams_matrix_unique: unique n grams
    :param features: features to be taken
    :param num_clusters: Number of clusters to do
    :return: dictionary of author names and score
    """
    author_score = [[0 for x in range(len(text_trigrams_matrix_unique))] for y in
                    range(len(text_trigrams_matrix_unique))]

    for x in range(len(text_trigrams_matrix_unique)):
        for y in range(len(text_trigrams_matrix_unique)):
            temp = list(sorted(
                set(text_trigrams_matrix_unique[x][0:features] + text_trigrams_matrix_unique[y][0:features])))
            tot = 0
            for z in range(len(temp)):
                if temp[z] in text_trigrams_matrix_unique[x]:
                    f1 = count[x][text_trigrams_matrix_unique[x].index(temp[z])]
                else:
                    f1 = 0
                if temp[z] in text_trigrams_matrix_unique[y]:
                    f2 = count[y][text_trigrams_matrix_unique[y].index(temp[z])]
                else:
                    f2 = 0
                tot = math.pow((float(2 * (f1 - f2)) / float(f1 + f2)), 2) + float(tot)
            author_score[x][y] = float("{0:.2f}".format(tot))
    print('Author Score clustering')
    clustering_scores = []
    for i in range(3, num_clusters + 3, 1):
        model = AgglomerativeClustering(linkage="ward", affinity="euclidean", n_clusters=i)
        model.fit(author_score)
        clustering_scores.append(model.labels_.tolist())

    return clustering_scores


def get_factor_and_max(d):
    """
    Find normalize factor and max value in an array
    :param d: array
    :return: factor and max value
    """
    max_val = max(d)
    min_val = min(d)
    print(max_val)
    print(min_val)
    factor = 1 / (min_val - max_val)
    return factor, max_val


def normalize_dic(d):
    """
    Normalize a dictionary
    :param d:
    :return:
    """
    maxi = max(d.values())
    mini = min(d.values())
    factor = 1 / (mini - maxi)
    return {key: (value - maxi) * factor for key, value in d.items()}
