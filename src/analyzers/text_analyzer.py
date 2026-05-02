"""
文本分析器模块
提供文本内容分析、关键词提取、热度计算等功能
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
from datetime import datetime

import jieba
import jieba.analyse
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)


class TextAnalyzer:
    """
    文本分析器
    提供文本分析、关键词提取、内容摘要等功能
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化文本分析器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # 停用词列表
        self.stop_words = self._load_stop_words()
        
        # 热点关键词权重
        self.hot_keyword_weights = {
            "突发": 2.0, "重磅": 2.0, "最新": 1.5, "热议": 1.5,
            "热搜": 1.5, "震惊": 1.8, "速看": 1.3, "首次": 1.5,
            "宣布": 1.3, "发布": 1.2, "上市": 1.4, "融资": 1.3,
            "收购": 1.4, "政策": 1.3, "改革": 1.3, "实施": 1.2,
            "影响": 1.2, "突破": 1.4, "创新": 1.3, "领先": 1.2
        }
        
        # 情感关键词
        self.positive_keywords = [
            "突破", "创新", "领先", "成功", "增长", "提升", "优化",
            "利好", "上涨", "涨停", "大涨", "飙升", "暴涨"
        ]
        
        self.negative_keywords = [
            "下跌", "跌停", "暴跌", "崩盘", "危机", "风险", "警告",
            "处罚", "违规", "造假", "亏损", "下滑", "减少"
        ]
        
        # 初始化jieba
        jieba.initialize()
        
        logger.info("文本分析器初始化完成")
    
    def _load_stop_words(self) -> set:
        """
        加载停用词表
        
        Returns:
            set: 停用词集合
        """
        # 常用中文停用词
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
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        分析文本内容
        
        Args:
            text: 待分析的文本
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        if not text:
            return {}
        
        try:
            # 分词
            words = self._tokenize(text)
            
            # 提取关键词
            keywords = self.extract_keywords(text, top_k=10)
            
            # 计算文本统计信息
            stats = self._calculate_stats(text, words)
            
            # 分析情感倾向
            sentiment = self._analyze_sentiment(text)
            
            # 计算热度分数
            hot_score = self._calculate_hot_score(text, keywords)
            
            return {
                "keywords": keywords,
                "stats": stats,
                "sentiment": sentiment,
                "hot_score": hot_score,
                "word_count": len(words),
                "char_count": len(text)
            }
            
        except Exception as e:
            logger.error(f"文本分析失败: {e}", exc_info=True)
            return {}
    
    def _tokenize(self, text: str) -> List[str]:
        """
        中文分词
        
        Args:
            text: 待分词的文本
            
        Returns:
            List[str]: 分词结果
        """
        # 使用jieba分词
        words = jieba.cut(text)
        
        # 过滤停用词和单字词
        filtered_words = [
            word.strip() for word in words 
            if word.strip() 
            and word.strip() not in self.stop_words
            and len(word.strip()) > 1
            and not re.match(r'^[\d\s\W]+$', word.strip())  # 过滤纯数字和符号
        ]
        
        return filtered_words
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        提取文本关键词
        
        Args:
            text: 待分析的文本
            top_k: 返回前K个关键词
            
        Returns:
            List[Tuple[str, float]]: 关键词及其权重列表
        """
        if not text:
            return []
        
        try:
            # 使用jieba的TF-IDF算法提取关键词
            keywords_tfidf = jieba.analyse.extract_tags(
                text, 
                topK=top_k * 2,  # 多提取一些，后面会过滤
                withWeight=True,
                allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'v', 'vn', 'a', 'ad')
            )
            
            # 使用jieba的TextRank算法提取关键词
            keywords_textrank = jieba.analyse.textrank(
                text,
                topK=top_k * 2,
                withWeight=True,
                allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'v', 'vn', 'a', 'ad')
            )
            
            # 合并两种算法的结果
            keyword_scores = {}
            
            for word, weight in keywords_tfidf:
                if word not in keyword_scores:
                    keyword_scores[word] = 0
                keyword_scores[word] += weight
            
            for word, weight in keywords_textrank:
                if word not in keyword_scores:
                    keyword_scores[word] = 0
                keyword_scores[word] += weight * 0.8  # TextRank权重略低
            
            # 应用热点关键词权重
            for word in keyword_scores:
                if word in self.hot_keyword_weights:
                    keyword_scores[word] *= self.hot_keyword_weights[word]
            
            # 排序并返回前K个
            sorted_keywords = sorted(
                keyword_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return sorted_keywords[:top_k]
            
        except Exception as e:
            logger.warning(f"关键词提取失败: {e}")
            return []
    
    def _calculate_stats(self, text: str, words: List[str]) -> Dict[str, Any]:
        """
        计算文本统计信息
        
        Args:
            text: 原始文本
            words: 分词结果
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        # 词频统计
        word_freq = Counter(words)
        
        # 句子统计
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 段落统计
        paragraphs = text.split('\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return {
            "total_chars": len(text),
            "total_words": len(words),
            "unique_words": len(set(words)),
            "total_sentences": len(sentences),
            "total_paragraphs": len(paragraphs),
            "avg_sentence_length": len(words) / max(len(sentences), 1),
            "top_words": word_freq.most_common(10)
        }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        分析文本情感倾向
        
        Args:
            text: 待分析的文本
            
        Returns:
            Dict[str, Any]: 情感分析结果
        """
        text_lower = text.lower()
        
        positive_count = 0
        negative_count = 0
        
        # 统计正面关键词
        for keyword in self.positive_keywords:
            if keyword in text_lower:
                positive_count += 1
        
        # 统计负面关键词
        for keyword in self.negative_keywords:
            if keyword in text_lower:
                negative_count += 1
        
        # 计算情感分数
        total = positive_count + negative_count
        if total == 0:
            sentiment_score = 0.5  # 中性
            sentiment_label = "中性"
        else:
            sentiment_score = positive_count / total
            if sentiment_score > 0.6:
                sentiment_label = "正面"
            elif sentiment_score < 0.4:
                sentiment_label = "负面"
            else:
                sentiment_label = "中性"
        
        return {
            "score": sentiment_score,
            "label": sentiment_label,
            "positive_count": positive_count,
            "negative_count": negative_count
        }
    
    def _calculate_hot_score(self, text: str, keywords: List[Tuple[str, float]]) -> float:
        """
        计算文本热度分数
        
        Args:
            text: 文本内容
            keywords: 关键词列表
            
        Returns:
            float: 热度分数
        """
        score = 0.0
        
        # 基于关键词权重
        for word, weight in keywords:
            if word in self.hot_keyword_weights:
                score += weight * self.hot_keyword_weights[word]
            else:
                score += weight
        
        # 基于文本长度（适中长度得分高）
        text_length = len(text)
        if 100 < text_length < 1000:
            score += 10
        elif text_length >= 1000:
            score += 5
        
        # 基于特殊符号（感叹号、问号等表示强烈情感）
        exclamation_count = text.count('！') + text.count('!')
        question_count = text.count('？') + text.count('?')
        score += min(exclamation_count * 2, 10)  # 最多加10分
        score += min(question_count * 1, 5)  # 最多加5分
        
        # 基于数字（数据驱动的新闻通常更有价值）
        numbers = re.findall(r'\d+', text)
        if len(numbers) > 3:
            score += 5
        
        return score
    
    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """
        生成文本摘要
        
        Args:
            text: 原始文本
            max_length: 摘要最大长度
            
        Returns:
            str: 生成的摘要
        """
        if not text:
            return ""
        
        # 如果文本已经很短，直接返回
        if len(text) <= max_length:
            return text
        
        try:
            # 分句
            sentences = re.split(r'[。！？.!?]', text)
            sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]
            
            if not sentences:
                return text[:max_length]
            
            # 计算每个句子的重要性
            sentence_scores = []
            
            for i, sentence in enumerate(sentences):
                score = 0
                
                # 位置权重（开头和结尾的句子更重要）
                if i == 0:
                    score += 3
                elif i == len(sentences) - 1:
                    score += 2
                elif i < len(sentences) * 0.3:  # 前30%
                    score += 1
                
                # 长度权重（适中长度的句子更重要）
                length = len(sentence)
                if 10 < length < 100:
                    score += 2
                elif length >= 100:
                    score += 1
                
                # 包含关键词的句子更重要
                for keyword in self.hot_keyword_weights:
                    if keyword in sentence:
                        score += 2
                
                # 包含数字的句子可能包含重要数据
                if re.search(r'\d+', sentence):
                    score += 1
                
                sentence_scores.append((sentence, score))
            
            # 按分数排序
            sentence_scores.sort(key=lambda x: x[1], reverse=True)
            
            # 选择重要句子
            selected_sentences = []
            current_length = 0
            
            for sentence, score in sentence_scores:
                if current_length + len(sentence) + 1 <= max_length:
                    selected_sentences.append(sentence)
                    current_length += len(sentence) + 1
                else:
                    break
            
            # 按原始顺序排列
            selected_sentences.sort(key=lambda x: sentences.index(x))
            
            # 组合成摘要
            summary = '。'.join(selected_sentences)
            if not summary.endswith(('。', '！', '！', '!', '?', '？')):
                summary += '。'
            
            return summary
            
        except Exception as e:
            logger.warning(f"生成摘要失败: {e}")
            # 简单截断
            return text[:max_length] + "..."
    
    def categorize_news(self, title: str, content: str = "") -> str:
        """
        对新闻进行分类
        
        Args:
            title: 新闻标题
            content: 新闻内容
            
        Returns:
            str: 新闻分类
        """
        text = (title + " " + content).lower()
        
        # 分类关键词映射
        categories = {
            "科技": ["科技", "技术", "互联网", "人工智能", "AI", "区块链", "5G", "芯片", "算法", "数据"],
            "财经": ["财经", "股票", "基金", "投资", "金融", "经济", "GDP", "通胀", "利率", "汇率"],
            "社会": ["社会", "民生", "教育", "医疗", "就业", "住房", "交通", "环保", "安全"],
            "娱乐": ["娱乐", "明星", "电影", "音乐", "综艺", "电视剧", "演员", "导演"],
            "体育": ["体育", "足球", "篮球", "网球", "奥运会", "世界杯", "冠军", "比赛"],
            "国际": ["国际", "美国", "欧洲", "日本", "韩国", "外交", "贸易", "战争"],
            "政治": ["政治", "政府", "政策", "法律", "法规", "改革", "选举", "会议"],
            "健康": ["健康", "医疗", "疾病", "疫苗", "药物", "医院", "患者", "治疗"]
        }
        
        # 计算每个分类的匹配分数
        category_scores = {}
        for category, keywords in categories.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            if score > 0:
                category_scores[category] = score
        
        # 返回得分最高的分类
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        else:
            return "综合"