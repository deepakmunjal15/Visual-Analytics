from django.shortcuts import render
from django.http import HttpResponse
import json
import operator
from authorship_attribution.backend import get_author_score_clustering
from .backend import readFiles, pre_process, make_n_grams, find_author_live, make_force_backend, prepare_bar


def index(request):
    return render(request, 'index.html')


def live_processing(request):
    """
    Show live bar charts
    :param request: request string
    :return: response of bar
    """
    data = {}
    if request.method == 'POST':
        n = 3
        features = 500

        text = request.POST.get('text')
        counter = int(request.POST.get('counter'))
        counter += 1

        # del request.session['author_names']
        count, count_without_normalized, text_trigrams_matrix_unique, count_test, text_trigrams_matrix_unique_test, \
        author_names, count4, count_without_normalized4, count_test4, text_trigrams_matrix_unique4, \
        text_trigrams_matrix_unique_test4 = get_parameters(request, n)

        files_text_test = pre_process([text])
        count_test, text_trigrams_matrix_unique_test, count_denormalized_test = make_n_grams(n, files_text_test)

        di = find_author_live(count, text_trigrams_matrix_unique, count_test,
                              text_trigrams_matrix_unique_test, author_names, features)

        dic_sorted = dict(sorted(di.items(), key=operator.itemgetter(1))[:6])
        data['score'] = normalize(dic_sorted)
        data['counter'] = counter
        data['force'] = make_force_live(request)

        # get tri grams
        data['author'] = author_names
        data['train_ngrams_word'] = text_trigrams_matrix_unique
        data['train_ngrams_score'] = count_without_normalized
        data['test_ngrams_words'] = text_trigrams_matrix_unique_test
        data['test_ngrams_score'] = count_denormalized_test

    return HttpResponse(json.dumps(data), content_type='application/json')


def make_force_live(request):
    """
    Make Force Layout of live data
    :param request: request get
    :return: json data
    """
    data = {}
    if request.method == 'POST':
        n = 3
        features = 500

        text = request.POST.get('text')
        counter = int(request.POST.get('counter'))
        counter += 1

        count, count_without_normalized, text_trigrams_matrix_unique, count_test, text_trigrams_matrix_unique_test, \
        author_names, count4, count_without_normalized4, count_test4, text_trigrams_matrix_unique4, \
        text_trigrams_matrix_unique_test4 = get_parameters(request, n)

        files_text_test = pre_process([text])
        count_test, text_trigrams_matrix_unique_test, count_denormalized_test = make_n_grams(n, files_text_test)

        author_new = ["Test Author"] + author_names
        di = make_force_backend(count, text_trigrams_matrix_unique, count_test,
                                text_trigrams_matrix_unique_test, author_new, features, ["Test Author"])

        data = {'results': di, 'author': ["Test Author"]}

        # get clusters
        num_clusters = 7
        cluster_count = 3
        if 'clustering3' not in request.session:
            clustering = get_author_score_clustering(count, text_trigrams_matrix_unique, features, num_clusters)
            for c in clustering:
                request.session['clustering' + str(cluster_count)] = c
                cluster_count += 1

        cluster_count = 3
        for c in range(num_clusters):
            data['clustering' + str(cluster_count)] = request.session['clustering' + str(cluster_count)]
            cluster_count += 1

    return data


def make_force(request):
    """
    Make clusters
    :param request: request get
    :return: json data
    """
    data = {}
    if request.method == 'POST':
        n = 3
        features = 500

        type = request.POST.get('type')
        counter = int(request.POST.get('counter'))
        counter += 1

        #del_key(request, 'author_names')
        #del_key(request, 'di')

        print("Started")
        count, count_without_normalized, text_trigrams_matrix_unique, count_test, text_trigrams_matrix_unique_test, \
        author_names, count4, count_without_normalized4, count_test4, text_trigrams_matrix_unique4, \
        text_trigrams_matrix_unique_test4 = get_parameters(request, n)

        files_text_t, author_name_test = readFiles("authorship_attribution/C50test")
        if 'di' not in request.session:
            di = make_force_backend(count, text_trigrams_matrix_unique, count_test,
                                    text_trigrams_matrix_unique_test, author_names, features, author_name_test)
            request.session['di'] = di

    files_text_test, a_names_test = readFiles("authorship_attribution/C50test")

    data = {'results': request.session['di'], 'author': a_names_test}
    return HttpResponse(json.dumps(data), content_type='application/json')


def make_bars(request):
    """
    Make grouped bar chart from test data
    :param request: request object
    :return: response of bar data
    """
    data = {}
    if request.method == 'POST':
        n = 3
        features = 500

        type = request.POST.get('type')
        counter = int(request.POST.get('counter'))
        counter += 1

        count, count_without_normalized, text_trigrams_matrix_unique, count_test, text_trigrams_matrix_unique_test, \
        author_names, count4, count_without_normalized4, count_test4, text_trigrams_matrix_unique4, \
        text_trigrams_matrix_unique_test4 = get_parameters(request, n)

        if 'bar' not in request.session:
            di = prepare_bar(count, text_trigrams_matrix_unique, count_test,
                             text_trigrams_matrix_unique_test, author_names, features)
            di4 = prepare_bar(count4, text_trigrams_matrix_unique4, count_test4,
                              text_trigrams_matrix_unique_test4, author_names, features)
            request.session['bar'] = di
            request.session['bar4'] = di4

    data = {'results': request.session['bar'], 'author': request.session['author_names'],
            'results4': request.session['bar4']}
    return HttpResponse(json.dumps(data), content_type='application/json')


def normalize(d):
    """
    Normalize the value in such a way that minimum scoring author will have a value of 1 where 1 is maximum matched
    and 0 is least matched
    :param d: dictionary to normalize
    :return: normalized dictionary
    """
    maxi = max(d.values())
    mini = min(d.values())
    factor = 1 / (mini - maxi)
    return {key: (value - maxi) * factor for key, value in d.items()}


def del_key(request, key):
    """
    Delet a key
    :param request: session request
    :param key: key to change value
    """
    if key in request.session:
        del request.session[key]


def get_parameters(request, optimal_features):
    """
    Get parameters to draw components
    :param request: current request
    :param optimal_features: optimal features in this case 3
    :return: drawing parameters
    """
    if 'author_names' in request.session and 'text_trigrams_matrix_unique_test' in request.session:
        print("Old Session")
        count = request.session['count']
        count_without_normalized = request.session['count_without_normalized']
        text_trigrams_matrix_unique = request.session['text_trigrams_matrix_unique']
        count_test = request.session['count_test']
        text_trigrams_matrix_unique_test = request.session['text_trigrams_matrix_unique_test']
        author_names = request.session['author_names']
        count4 = request.session['count4']
        count_without_normalized4 = request.session['count_without_normalized4']
        count_test4 = request.session['count_test4']
        text_trigrams_matrix_unique4 = request.session['text_trigrams_matrix_unique4']
        text_trigrams_matrix_unique_test4 = request.session['text_trigrams_matrix_unique_test4']
    else:
        print("New Session")
        files_text, author_names = readFiles("authorship_attribution/C50train")
        files_text_test, a_names_test = readFiles("authorship_attribution/C50test")
        files_text = pre_process(files_text)
        count, text_trigrams_matrix_unique, count_without_normalized = make_n_grams(optimal_features, files_text)
        count4, text_trigrams_matrix_unique4, count_without_normalized4 = make_n_grams(optimal_features + 1, files_text)
        count_test, text_trigrams_matrix_unique_test, count_without_normalized_test = \
            make_n_grams(optimal_features, files_text_test)
        count_test4, text_trigrams_matrix_unique_test4, count_without_normalized_test4 = \
            make_n_grams(optimal_features + 1, files_text_test)
        save_session(request, author_names, count, count_without_normalized, count4, count_without_normalized4,
                     text_trigrams_matrix_unique, text_trigrams_matrix_unique4,
                     count_test, count_test4, text_trigrams_matrix_unique_test, text_trigrams_matrix_unique_test4)
    return count, count_without_normalized, text_trigrams_matrix_unique, count_test, text_trigrams_matrix_unique_test, \
           author_names, count4, count_without_normalized4, count_test4, \
           text_trigrams_matrix_unique4, text_trigrams_matrix_unique_test4


def save_session(request, author_names, count, count_without_normalized, count4, count_without_normalized4,
                 text_trigrams_matrix_unique, text_trigrams_matrix_unique4, count_test, count_test4,
                 text_trigrams_matrix_unique_test, text_trigrams_matrix_unique_test4):
    """
    Save parameters to session for faster response
    :param request: current session request
    :param author_names: train author names
    :param count: count train
    :param count_without_normalized: count train without normalization
    :param count4: count train in terms of 4 features
    :param count_without_normalized4: count train in terms of 4 features without normalization
    :param text_trigrams_matrix_unique:  unique matrix for 3 features
    :param text_trigrams_matrix_unique4: unique matrix for 4 features
    :param count_test: count of test
    :param count_test4: count of test for 4 features
    :param text_trigrams_matrix_unique_test: unique matrix test for 3 features
    :param text_trigrams_matrix_unique_test4: unique matrix test for 4 features
    """
    request.session['author_names'] = author_names
    request.session['count'] = count
    request.session['count_without_normalized'] = count_without_normalized
    request.session['count4'] = count4
    request.session['count_without_normalized4'] = count_without_normalized4
    request.session['text_trigrams_matrix_unique'] = text_trigrams_matrix_unique
    request.session['text_trigrams_matrix_unique4'] = text_trigrams_matrix_unique4
    request.session['count_test'] = count_test
    request.session['count_test4'] = count_test4
    request.session['text_trigrams_matrix_unique_test'] = text_trigrams_matrix_unique_test
    request.session['text_trigrams_matrix_unique_test4'] = text_trigrams_matrix_unique_test4
