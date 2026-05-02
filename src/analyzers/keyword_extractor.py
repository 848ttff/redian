"""
关键词提取器模块
提供多种关键词提取算法
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

import jieba
import jieba.analyse
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

logger = logging.getLogger(__name__)


class KeywordExtractor:
    """
    关键词提取器
    支持多种关键词提取算法
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化关键词提取器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # 停用词
        self.stop_words = self._load_stop_words()
        
        # 初始化jieba
        jieba.initialize()
        
        logger.info("关键词提取器初始化完成")
    
    def _load_stop_words(self) -> set:
        """
        加载停用词表
        
        Returns:
            set: 停用词集合
        """
        stop_words = {
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
            "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
            "你", "会", "着", "没有", "看", "好", "自己", "这", "他", "她",
            "它", "们", "那", "里", "为", "什么", "怎么", "如何", "为什么",
            "可以", "可能", "应该", "需要", "必须", "已经", "正在", "将要",
            "因为", "所以", "但是", "然而", "虽然", "尽管", "如果", "除非",
            "或者", "还是", "不是", "就是", "而是", "以及", "而且", "并且",
            "这个", "那个", "这些", "那些", "这里", "那里", "这时", "那时",
            "今天", "昨天", "明天", "现在", "过去", "未来", "目前", "当前",
            "根据", "按照", "通过", "经过", "对于", "关于", "由于", "因此",
            "显示", "表示", "认为", "觉得", "知道", "了解", "发现", "看到",
            "听到", "感到", "感觉", "认为", "以为", "推测", "猜测", "估计"
        }
        
        return stop_words
    
    def extract_tfidf(self, texts: List[str], top_k: int = 20) -> List[Tuple[str, float]]:
        """
        使用TF-IDF算法提取关键词
        
        Args:
            texts: 文本列表
            top_k: 返回前K个关键词
            
        Returns:
            List[Tuple[str, float]]: 关键词及其权重列表
        """
        if not texts:
            return []
        
        try:
            # 分词处理
            tokenized_texts = []
            for text in texts:
                words = jieba.cut(text)
                filtered_words = [
                    word.strip() for word in words
                    if word.strip()
                    and word.strip() not in self.stop_words
                    and len(word.strip()) > 1
                ]
                tokenized_texts.append(" ".join(filtered_words))
            
            # 使用TF-IDF向量化
            vectorizer = TfidfVectorizer(
                max_features=1000,
                max_df=0.95,
                min_df=2,
                ngram_range=(1, 2)
            )
            
            tfidf_matrix = vectorizer.fit_transform(tokenized_texts)
            
            # 获取特征词
            feature_names = vectorizer.get_feature_names_out()
            
            # 计算平均TF-IDF值
            avg_tfidf = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # 创建关键词-权重字典
            keyword_weights = dict(zip(feature_names, avg_tfidf))
            
            # 排序并返回前K个
            sorted_keywords = sorted(
                keyword_weights.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return sorted_keywords[:top_k]
            
        except Exception as e:
            logger.error(f"TF-IDF关键词提取失败: {e}", exc_info=True)
            return []
    
    def extract_textrank(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        使用TextRank算法提取关键词
        
        Args:
            text: 待分析的文本
            top_k: 返回前K个关键词
            
        Returns:
            List[Tuple[str, float]]: 关键词及其权重列表
        """
        if not text:
            return []
        
        try:
            # 使用jieba的TextRank算法
            keywords = jieba.analyse.textrank(
                text,
                topK=top_k,
                withWeight=True,
                allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'v', 'vn')
            )
            
            return keywords
            
        except Exception as e:
            logger.error(f"TextRank关键词提取失败: {e}", exc_info=True)
            return []
    
    def extract_lda_topics(self, texts: List[str], n_topics: int = 5, n_words: int = 10) -> List[Dict[str, Any]]:
        """
        使用LDA主题模型提取主题词
        
        Args:
            texts: 文本列表
            n_topics: 主题数量
            n_words: 每个主题的词数
            
        Returns:
            List[Dict[str, Any]]: 主题列表，每个主题包含主题词和权重
        """
        if not texts:
            return []
        
        try:
            # 分词处理
            tokenized_texts = []
            for text in texts:
                words = jieba.cut(text)
                filtered_words = [
                    word.strip() for word in words
                    if word.strip()
                    and word.strip() not in self.stop_words
                    and len(word.strip()) > 1
                ]
                tokenized_texts.append(" ".join(filtered_words))
            
            # 使用CountVectorizer
            vectorizer = CountVectorizer(
                max_features=1000,
                max_df=0.95,
                min_df=2
            )
            
            count_matrix = vectorizer.fit_transform(tokenized_texts)
            
            # 训练LDA模型
            lda = LatentDirichletAllocation(
                n_components=n_topics,
                random_state=42,
                max_iter=20
            )
            
            lda.fit(count_matrix)
            
            # 获取特征词
            feature_names = vectorizer.get_feature_names_out()
            
            # 提取主题词
            topics = []
            for topic_idx, topic in enumerate(lda.components_):
                top_word_indices = topic.argsort()[:-n_words-1:-1]
                top_words = [(feature_names[i], topic[i]) for i in top_word_indices]
                
                topics.append({
                    "topic_id": topic_idx,
                    "words": top_words,
                    "word_list": [word for word, _ in top_words]
                })
            
            return topics
            
        except Exception as e:
            logger.error(f"LDA主题提取失败: {e}", exc_info=True)
            return []
    
    def extract_named_entities(self, text: str) -> Dict[str, List[str]]:
        """
        提取命名实体
        
        Args:
            text: 待分析的文本
            
        Returns:
            Dict[str, List[str]]: 实体类型到实体列表的映射
        """
        if not text:
            return {}
        
        try:
            # 使用jieba进行词性标注
            import jieba.posseg as pseg
            
            words = pseg.cut(text)
            
            entities = {
                "person": [],      # 人名
                "location": [],    # 地名
                "organization": [], # 机构名
                "time": [],        # 时间
                "number": []       # 数字
            }
            
            for word, flag in words:
                word = word.strip()
                if not word:
                    continue
                
                # 人名
                if flag == 'nr':
                    entities["person"].append(word)
                # 地名
                elif flag == 'ns':
                    entities["location"].append(word)
                # 机构名
                elif flag == 'nt':
                    entities["organization"].append(word)
                # 时间
                elif flag == 't':
                    entities["time"].append(word)
                # 数字
                elif flag == 'm':
                    entities["number"].append(word)
            
            # 去重
            for key in entities:
                entities[key] = list(set(entities[key]))
            
            return entities
            
        except Exception as e:
            logger.error(f"命名实体提取失败: {e}", exc_info=True)
            return {}
    
    def extract_key_phrases(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        提取关键短语
        
        Args:
            text: 待分析的文本
            top_k: 返回前K个关键短语
            
        Returns:
            List[Tuple[str, float]]: 关键短语及其权重列表
        """
        if not text:
            return []
        
        try:
            # 使用jieba分词
            words = list(jieba.cut(text))
            
            # 过滤停用词
            filtered_words = [
                word.strip() for word in words
                if word.strip()
                and word.strip() not in self.stop_words
                and len(word.strip()) > 1
            ]
            
            # 提取2-gram和3-gram短语
            phrases = []
            
            # 2-gram
            for i in range(len(filtered_words) - 1):
                phrase = filtered_words[i] + filtered_words[i + 1]
                phrases.append(phrase)
            
            # 3-gram
            for i in range(len(filtered_words) - 2):
                phrase = filtered_words[i] + filtered_words[i + 1] + filtered_words[i + 2]
                phrases.append(phrase)
            
            # 统计短语频率
            phrase_freq = Counter(phrases)
            
            # 计算短语权重（结合频率和长度）
            phrase_weights = {}
            for phrase, freq in phrase_freq.items():
                # 长度权重
                length_weight = len(phrase) / 10
                # 频率权重
                freq_weight = freq / len(phrases)
                
                phrase_weights[phrase] = length_weight * freq_weight
            
            # 排序并返回前K个
            sorted_phrases = sorted(
                phrase_weights.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return sorted_phrases[:top_k]
            
        except Exception as e:
            logger.error(f"关键短语提取失败: {e}", exc_info=True)
            return []
    
    def extract_keywords_multi_method(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        使用多种方法提取关键词并合并结果
        
        Args:
            text: 待分析的文本
            top_k: 返回前K个关键词
            
        Returns:
            List[Tuple[str, float]]: 关键词及其权重列表
        """
        if not text:
            return []
        
        try:
            # 使用TF-IDF方法
            tfidf_keywords = self.extract_tfidf([text], top_k=top_k * 2)
            
            # 使用TextRank方法
            textrank_keywords = self.extract_textrank(text, top_k=top_k * 2)
            
            # 合并结果
            keyword_scores = {}
            
            # TF-IDF权重
            for word, weight in tfidf_keywords:
                if word not in keyword_scores:
                    keyword_scores[word] = 0
                keyword_scores[word] += weight
            
            # TextRank权重
            for word, weight in textrank_keywords:
                if word not in keyword_scores:
                    keyword_scores[word] = 0
                keyword_scores[word] += weight * 0.8
            
            # 排序并返回前K个
            sorted_keywords = sorted(
                keyword_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return sorted_keywords[:top_k]
            
        except Exception as e:
            logger.error(f"多方法关键词提取失败: {e}", exc_info=True)
            return []