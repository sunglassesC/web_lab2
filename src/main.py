from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

train_data_path = '../dataset/train.txt'
test_data_path = '../dataset/test.txt'

output_file_path = '../output/result.txt'

relationship_list = [
    'Cause-Effect', 'Component-Whole', 'Entity-Destination', 'Product-Producer',
    'Entity-Origin', 'Member-Collection', 'Message-Topic', 'Content-Container',
    'Instrument-Agency', 'Other'
]


def classify(sentence, feature_vec):
    max_score = 0
    max_score_relationship = ''
    for relationship in relationship_list:
        # 分词
        word_tokens = word_tokenize(sentence)

        # 词根化
        ps = PorterStemmer()
        stemmed_tokens = [ps.stem(w) for w in word_tokens if w.isalpha()]

        # 去停用词
        stop_words = set(stopwords.words('english'))
        useful_stopwords_list = ['into', 'from', 'by']
        for ele in useful_stopwords_list:
            stop_words.remove(ele)
        filtered_tokens1 = [w for w in word_tokens if w.lower() not in stop_words]

        score = 0
        for token in set(filtered_tokens1):
            if token in feature_vec[relationship]:
                score += feature_vec[relationship][token]
        if score > max_score:
            max_score = score
            max_score_relationship = relationship
    if not max_score_relationship:
        return 'Other'
    return max_score_relationship


if __name__ == '__main__':
    train_data = []

    # 从train.txt读入训练数据
    with open(train_data_path, 'r') as f:
        while True:
            data = {}
            a = f.readline()

            if not a:
                break
            data['content'] = a

            b = f.readline()
            relationship = b[:b.find('(')]
            entity = []
            entity_1 = b[b.find('(') + 1: b.find(',')]
            entity_2 = b[b.find(',') + 1: -2]
            entity.append(entity_1)
            entity.append(entity_2)

            data['relationship'] = relationship
            data['entity'] = entity

            train_data.append(data)

    # 根据每种关系训练出反应该关系特征的向量
    feature_vec = {}
    for relationship in relationship_list:
        # 得到符合当前关系的数据
        current_data = []
        for data in train_data:
            if data['relationship'] == relationship:
                current_data.append(data)

        # 统计每条数据中各单词出现的次数
        posting_list = {}
        for data in current_data:
            content = data['content']

            # 分词
            word_tokens = word_tokenize(content)

            # 去停用词
            stop_words = set(stopwords.words('english'))
            # 'into', 'from', 'and', 'is', 'with', 'that'
            useful_stopwords_list = ['into', 'from', 'by']
            for ele in useful_stopwords_list:
                stop_words.remove(ele)
            filtered_tokens1 = [w for w in word_tokens if w.lower() not in stop_words]

            # 词根化
            ps = PorterStemmer()
            stemmed_tokens = [ps.stem(w) for w in word_tokens if w.isalpha()]

            # 去停用词
            filtered_tokens2 = [w for w in stemmed_tokens if w.lower() not in stop_words]

            for token in set(filtered_tokens2):  # 只考虑在该条数据中是否出现，不考虑数量
                if token not in posting_list:
                    posting_list[token] = 1
                else:
                    posting_list[token] += 1

        # print(relationship)
        # print(len(current_data))

        feature_vec[relationship] = {}
        for i in range(1650):
            if posting_list:
                a = max(posting_list.items(), key=lambda x: x[1])

                # print(a, a[1] / len(current_data))
                feature_vec[relationship][a[0]] = a[1]

                del posting_list[a[0]]
            else:
                print('list is already empty')
                break

    for relationship_1 in relationship_list:
        for token in feature_vec[relationship_1]:
            freq = 0
            for relationship_2 in relationship_list:
                if token in feature_vec[relationship_2]:
                    freq += 1
            feature_vec[relationship_1][token] *= (len(relationship_list) - freq)

    # print(feature_vec)

    # 读入测试集数据
    test_data = []
    with open(test_data_path, 'r') as f:
        while True:
            txt = f.readline()
            if not txt:
                break
            test_data.append(txt)

    # 得到分类结果
    result_list = []
    for data in test_data:
        result = classify(data, feature_vec)
        result_list.append(result)

    # 写入结果文件
    with open(output_file_path, 'w') as f:
        for ele in result_list:
            f.write(ele + '\n')
