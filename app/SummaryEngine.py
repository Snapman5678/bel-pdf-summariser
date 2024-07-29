import re
import numpy as np
import warnings
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.tokenizers import Tokenizer
from transformers import BartTokenizer, BartForConditionalGeneration
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import torch
from transformers import logging

warnings.filterwarnings("ignore")
logging.set_verbosity_error()

class ImprovedPreprocessor:
    @staticmethod
    def preprocess_text(text):
        paragraphs = text.split('\n\n')
        vectorizer = TfidfVectorizer(max_df=0.95, min_df=1, stop_words='english')

        if len(paragraphs) > 5:
            vectorizer.fit_transform(paragraphs)

        sections = re.split(r'\n(?=[A-Z][A-Z\s]+:?|\d+\.?\s+[A-Z])', text)
        processed_sections = []
        for section in sections:
            match = re.match(r'([A-Z][A-Z\s]+:?|\d+\.?\s+[A-Z][^\n]+)(.*)', section, re.DOTALL)
            if match:
                heading, content = match.groups()
                processed_sections.append((heading.strip(), content.strip()))
            else:
                processed_sections.append(("", section.strip()))
        return processed_sections

class ImprovedExtractiveSummarizer:
    def __init__(self):
        self.summarizer = TextRankSummarizer()
        self.stop_words = set(stopwords.words('english'))

    def summarize(self, text, sentences_count):
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summary = self.summarizer(parser.document, sentences_count)
        return [str(sentence) for sentence in summary]

class ImprovedAbstractiveSummarizer:
    def __init__(self, device='cpu'):
        self.device = device
        self.model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn").to(self.device)
        self.tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")

    def summarize(self, text, max_length, min_length, tech_terms=None):
        inputs = self.tokenizer(text, return_tensors="pt", max_length=1024, truncation=True).to(self.device)

        if tech_terms:
            attention_mask = inputs['attention_mask'].clone()
            for term in tech_terms:
                term_ids = self.tokenizer.encode(term, add_special_tokens=False)
                for i in range(len(inputs['input_ids'][0]) - len(term_ids) + 1):
                    if inputs['input_ids'][0][i:i + len(term_ids)].tolist() == term_ids:
                        attention_mask[0][i:i + len(term_ids)] = 2
            inputs['attention_mask'] = attention_mask

        summary_ids = self.model.generate(
            inputs['input_ids'],
            attention_mask=inputs['attention_mask'],
            max_length=max_length,
            min_length=min_length,
            length_penalty=2.0,
            num_beams=4,
            early_stopping=True
        )
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary

class ImprovedTechnicalTermExtractor:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 3), max_df=1.0, min_df=1)

    def extract(self, text):
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text])
            feature_names = self.vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]

            tech_terms = sorted(zip(feature_names, tfidf_scores), key=lambda x: x[1], reverse=True)
            filtered_terms = self.filter_terms([term for term, score in tech_terms[:50]])

            return filtered_terms[:15]  # Return top 15 filtered terms
        except ValueError:
            return self.extract_fallback(text)

    def filter_terms(self, terms):
        filtered = []
        for term in terms:
            if len(term.split()) > 1:  # Multi-word term
                filtered.append(term)
            elif term.isupper():  # Acronym
                filtered.append(term)
            else:
                pos = pos_tag([term])[0][1]
                if pos.startswith('NN'):  # Noun
                    filtered.append(term)
        return filtered

    def extract_fallback(self, text):
        # Simple fallback implementation
        words = text.split()
        return [word for word in words if len(word) > 1][:15]

class ImprovedFactChecker:
    def __init__(self):
        self.sentence_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    def verify(self, summary, original_content):
        summary_sentences = sent_tokenize(summary)
        original_sentences = sent_tokenize(original_content)

        summary_embeddings = self.sentence_model.encode(summary_sentences)
        original_embeddings = self.sentence_model.encode(original_sentences)

        similarity_matrix = cosine_similarity(summary_embeddings, original_embeddings)

        verified_summary = summary_sentences.copy()
        for i, orig_sentence in enumerate(original_sentences):
            if not any(similarity_matrix[j][i] > 0.7 for j in range(len(summary_sentences))):
                verified_summary.append(orig_sentence)

        return ' '.join(verified_summary)

class ImprovedPostprocessor:
    def format_summary(self, sections):
        formatted_summary = ["Document Summary\n"]
        grouped_sections = self.group_sections(sections)

        for group_name, group_sections in grouped_sections.items():
            formatted_summary.append(f"## {group_name}\n")
            for i, (heading, content) in enumerate(group_sections, 1):
                formatted_summary.append(f"### {heading.capitalize()}\n")
                formatted_summary.append(self.format_content(content))
                if i < len(group_sections):
                    formatted_summary.append("\n")

        formatted_summary.append("\nKey Takeaways\n")
        takeaways = self.extract_key_takeaways(sections)
        formatted_summary.extend(f"- {takeaway}\n" for takeaway in takeaways)

        return "\n".join(formatted_summary)

    def group_sections(self, sections):
        return {"Overview": sections}

    def format_content(self, content):
        sentences = sent_tokenize(content)
        formatted = []
        for i, sentence in enumerate(sentences):
            if i % 3 == 0 and i > 0:
                formatted.append("\n")
            formatted.append(sentence)
        return " ".join(formatted)

    def extract_key_takeaways(self, sections):
        all_content = " ".join(content for _, content in sections)
        sentences = sent_tokenize(all_content)
        sentence_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

        embeddings = sentence_model.encode(sentences)
        centroid = np.mean(embeddings, axis=0)

        similarities = cosine_similarity([centroid], embeddings)[0]
        top_indices = similarities.argsort()[-5:][::-1]

        return [sentences[i] for i in top_indices]

class SummarizationPipeline:
    def __init__(self, device='cpu'):
        self.preprocessor = ImprovedPreprocessor()
        self.extractive_summarizer = ImprovedExtractiveSummarizer()
        self.abstractive_summarizer = ImprovedAbstractiveSummarizer(device=device)
        self.technical_term_extractor = ImprovedTechnicalTermExtractor()
        self.fact_checker = ImprovedFactChecker()
        self.postprocessor = ImprovedPostprocessor()

    def summarize(self, text, target_length='medium', device='cpu'):
        sections = self.preprocessor.preprocess_text(text)
        total_words = sum(len(word_tokenize(content)) for _, content in sections)

        target_word_counts = {
            'short': min(500, max(250, total_words // 10)),
            'medium': min(1000, max(500, total_words // 5)),
            'long': min(2000, max(1000, total_words // 3))
        }

        target_words = target_word_counts[target_length]
        words_per_section = max(50, target_words // len(sections)) if sections else target_words

        summarized_sections = []
        for section_name, section_content in sections:
            if not section_content.strip():
                continue
            importance_score = self.calculate_importance(section_content)
            section_word_count = int(words_per_section * importance_score)

            summarized_section = self.summarize_section(section_content, section_word_count)
            summarized_sections.append((section_name, summarized_section))

        if not summarized_sections:
            return "The input text does not contain any content to summarize."

        summarized_sections = self.adjust_section_lengths(summarized_sections, target_words, device)

        return self.postprocessor.format_summary(summarized_sections)

    def calculate_importance(self, content):
        sentences = sent_tokenize(content)
        words = word_tokenize(content.lower())
        unique_words = set(words)

        if not words:
            return 1.0

        word_diversity = len(unique_words) / len(words)
        sentence_complexity = min(len(sentences) / 10, 1)

        importance = word_diversity * sentence_complexity
        return min(max(importance, 0.5), 2.0)

    def summarize_section(self, content, target_words):
        tech_terms = self.technical_term_extractor.extract(content)
        key_sentences = self.extractive_summarizer.summarize(content,
                                                             sentences_count=min(5, len(sent_tokenize(content))))
        key_sentences = self.ensure_tech_terms_included(key_sentences, tech_terms, content)

        combined_content = " ".join(key_sentences)
        abstract_summary = self.abstractive_summarizer.summarize(combined_content, max_length=target_words,
                                                                 min_length=target_words // 2, tech_terms=tech_terms)

        verified_summary = self.fact_checker.verify(abstract_summary, content)
        return verified_summary

    def ensure_tech_terms_included(self, sentences, tech_terms, original_content):
        included_terms = set()
        for sentence in sentences:
            included_terms.update(term for term in tech_terms if term.lower() in sentence.lower())

        missing_terms = set(tech_terms) - included_terms
        if missing_terms:
            additional_sentences = self.find_sentences_with_terms(missing_terms, original_content)
            sentences.extend(additional_sentences)

        return sentences

    def find_sentences_with_terms(self, terms, content):
        sentences = sent_tokenize(content)
        additional_sentences = []
        for term in terms:
            for sentence in sentences:
                if term.lower() in sentence.lower():
                    additional_sentences.append(sentence)
                    break
        return additional_sentences

    def adjust_section_lengths(self, sections, target_words, device):
        current_words = sum(len(word_tokenize(content)) for _, content in sections)
        scale_factor = target_words / current_words if current_words > target_words else 1

        adjusted_sections = []
        for name, content in sections:
            target_section_words = int(len(word_tokenize(content)) * scale_factor)
            adjusted_content = self.abstractive_summarizer.summarize(
                content,
                max_length=target_section_words,
                min_length=max(30, target_section_words // 2),
                tech_terms=self.technical_term_extractor.extract(content)
            )
            adjusted_sections.append((name, adjusted_content))

        return adjusted_sections

# Example usage
if __name__ == "__main__":
    pipeline = SummarizationPipeline()

    sample_text = """Your code implements a sophisticated pipeline for summarizing documents, combining both extractive and abstractive methods. It includes a preprocessor for text segmentation, extractive summarization using TextRank, abstractive summarization using BART, and a fact-checking module using sentence embeddings. Here are some points to consider regarding its effectiveness and possible improvements:

Strengths
Hybrid Approach: The combination of extractive and abstractive summarization leverages the strengths of both techniques, potentially improving summary quality.

Technical Term Extraction: The ImprovedTechnicalTermExtractor uses TF-IDF to identify important terms, ensuring that technical content is emphasized in the summaries.

Fact-Checking: The use of sentence transformers for verifying the factual consistency of summaries adds robustness to the output.

Customization: The pipeline allows for adjustable summary lengths and supports different model configurations, providing flexibility.

Post-Processing: The ImprovedPostprocessor formats summaries neatly, ensuring that key takeaways are highlighted and content is organized.

Considerations for a 50-Page Document
Scalability: Processing a 50-page document can be resource-intensive. Ensure that your environment has sufficient memory and computational power to handle large inputs, especially when using transformer models like BART.

Abstractive Model Limitations: The BART model's input size is limited to 1024 tokens. Consider segmenting the text into smaller parts before summarizing if it exceeds this limit, which your ImprovedPreprocessor already partially addresses.

Performance: Summarizing large texts with neural models can be time-consuming. Profiling the code to identify bottlenecks and optimizing them (e.g., using batch processing where possible) could improve performance.

Quality of Extractive Summarization: The extractive summarizer is limited to a fixed number of sentences (sentences_count parameter). Fine-tuning this number based on input size and section importance may yield better summaries.

Accuracy of Technical Term Highlighting: The highlight_term method attempts to increase the attention on technical terms, but doubling token IDs may not effectively impact model behavior. Consider directly manipulating attention weights if supported by your framework.

Recommendations for Improvement
Parallel Processing: Consider parallelizing parts of the code, such as summarizing different sections concurrently, to speed up processing time.

Model Selection: BART is a strong choice, but experimenting with other models (like T5 or Pegasus) might yield better results for specific types of content.

Dynamic Sentence Selection: In ImprovedExtractiveSummarizer, dynamically adjusting the number of sentences based on section length or content importance could improve extractive summaries.

Refinement of Importance Scores: Enhancing the calculate_importance method to include more sophisticated measures (e.g., topic modeling or entity recognition) could improve section weighting.

Validation: Regularly test the summarization pipeline on diverse documents to ensure it performs well across different types of content and document structures.

Overall, your code is well-structured and has potential for effective summarization, but scaling it for large documents requires careful attention to resource management and performance tuning. Testing with actual 50-page documents will provide further insights into its efficiency and areas for further refinement.
    """

    for length in ['short', 'medium', 'long']:
        try:
            summary = pipeline.summarize(sample_text, length)
            print(f"\n{length.capitalize()} Summary:")
            print(summary)
            print(f"Word count: {len(word_tokenize(summary))}")
        except Exception as e:
            print(f"An error occurred while generating the {length} summary: {str(e)}")

# To change the summary length:

# 1. Locate the `summarize` method in the SummarizationPipeline class
# 2. Find the `target_word_counts` dictionary
# 3. Adjust the values for 'short', 'medium', and 'long' as needed

# Example:
# target_word_counts = {
#     'short': min(200, max(100, total_words // 6)),  # Decreased from 300
#     'medium': min(400, max(200, total_words // 4)),  # Decreased from 500
#     'long': min(600, max(300, total_words // 3))  # Decreased from 800
# }

# To change the LLM model:
# 1. Locate the AbstractiveSummarizer class
# 2. In the __init__ method, change the model and tokenizer initialization
# 3. You may need to adjust the `summarize` method based on the new model's requirements

# Example for switching to a different BART model:

# self.model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-xsum")
# self.tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-xsum")

# Example for switching to a T5 model:

# from transformers import T5Tokenizer, T5ForConditionalGeneration
# self.model = T5ForConditionalGeneration.from_pretrained("t5-small")
# self.tokenizer = T5Tokenizer.from_pretrained("t5-small")
