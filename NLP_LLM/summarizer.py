import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

class SummarizationEngine:
    def __init__(self, model_name="facebook/bart-large-cnn"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.stop_words = set(stopwords.words('english'))

    def sentence_similarity(self, sent1, sent2):
        words1 = [word.lower() for word in nltk.word_tokenize(sent1) if word.isalnum()]
        words2 = [word.lower() for word in nltk.word_tokenize(sent2) if word.isalnum()]
        
        all_words = list(set(words1 + words2))
        
        vector1 = [0] * len(all_words)
        vector2 = [0] * len(all_words)
        
        for w in words1:
            if w not in self.stop_words:
                vector1[all_words.index(w)] += 1
        
        for w in words2:
            if w not in self.stop_words:
                vector2[all_words.index(w)] += 1
        
        return 1 - cosine_distance(vector1, vector2)

    def build_similarity_matrix(self, sentences):
        similarity_matrix = np.zeros((len(sentences), len(sentences)))
        for idx1 in range(len(sentences)):
            for idx2 in range(len(sentences)):
                if idx1 != idx2:
                    similarity_matrix[idx1][idx2] = self.sentence_similarity(sentences[idx1], sentences[idx2])
        return similarity_matrix

    def extractive_summarize(self, text, num_sentences):
        sentences = sent_tokenize(text)
        similarity_matrix = self.build_similarity_matrix(sentences)
        nx_graph = nx.from_numpy_array(similarity_matrix)
        scores = nx.pagerank(nx_graph)
        ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
        return " ".join([ranked_sentences[i][1] for i in range(min(num_sentences, len(ranked_sentences)))])

    def abstractive_summarize(self, text, max_length, min_length):
        inputs = self.tokenizer([text], max_length=1024, return_tensors="pt", truncation=True)
        inputs = inputs.to(self.device)

        summary_ids = self.model.generate(
            inputs.input_ids, 
            num_beams=4,
            max_length=max_length,
            min_length=min_length,
            length_penalty=2.0,
            early_stopping=True
        )

        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary

    def get_summary(self, text, level):
        total_words = len(text.split())
        
        extractive_sentences = {
            'low': 3,
            'medium': 5,
            'high': 7
        }.get(level.lower(), 5)

        max_length = {
            'low': min(150, total_words),
            'medium': min(300, total_words),
            'high': min(500, total_words)
        }.get(level.lower(), 300)

        min_length = max(50, max_length // 2)

        # extractive summarization
        extractive_summary = self.extractive_summarize(text, extractive_sentences)
        
        # abstractive summarization on the extractive summary
        final_summary = self.abstractive_summarize(extractive_summary, max_length, min_length)
        
        # Ensure the summary ends with a complete sentence
        sentences = sent_tokenize(final_summary)
        if len(sentences) > 1:
            last_period = final_summary.rfind('.')
            if last_period != -1:
                final_summary = final_summary[:last_period + 1]

        return final_summary