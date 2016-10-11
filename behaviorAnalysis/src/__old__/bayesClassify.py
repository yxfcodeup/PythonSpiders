
class Bayes() :
    def __init__(self , classification_list , words) :
        self.data_set = classification_list
        self.input_set = words

    def loadDataSet(self) :
        class_vec = []

    def createVocabList(self) :
        vocab_set = set([])
        for document in self.data_set :
            vocab_set = vocab_set | set(document)
        return list(vocab_set)

    def setOfWords2Vec(self , vocab_list , input_set) :
        return_vec = [0] * len(vocab_list)
        for word in input_set :
            if word in vocab_list :
                return_vec[vocab_list.index(word)] = 1
            #else :
                #print("the word: %s is not in my Vocabulary." % word)
        return return_vec

    def trainNB(self , train_matrix , train_category) :
        num_train_docs = len(train_matrix)
        num_words = len(train_matrix[0])
        p_abusive = sum(train_category) / float(num_train_docs)
        p0_num = np.ones(num_words) 
        p1_num = np.ones(num_words) 
        p0_denom = 2.0
        p1_denom = 2.0
        for i in range(num_train_docs) :
            if 1 == train_category[i] :
                p1_num += train_matrix[i]
                p1_denom += sum(train_matrix[i])
            else :
                p0_num += train_matrix[i]
                po_denom += sum(train_matrix[i])
        p1_vect = np.log(p1_num / p1_denom)
        p0_vect = np.log(p0_num / p0_denom)
        return p0_vect , p1_vect , p_abusive

    def run(self) :
        a = self.setOfWords2Vec(self.data_set , self.input_set)
        p0v,p1v,pa = self.trainNB(self.input_set , list(np.zeros(40)))
        print(pa)
