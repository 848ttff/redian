"""
工作流调度器模块
负责协调整个热点信息收集和处理流程
"""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from ..crawlers import CrawlerManager, NewsItem
from ..analyzers import TextAnalyzer, KeywordExtractor
from ..summarizers import SummaryGenerator
from ..mailers import EmailSender

logger = logging.getLogger(__name__)


class WorkflowScheduler:
    """
    工作流调度器
    协调爬取、分析、总结和邮件发送的完整流程
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化工作流调度器
        
        Args:
            config: 完整的系统配置
        """
        self.config = config
        
        # 初始化各个模块
        self.crawler_manager = CrawlerManager({"sources": config.get("sources", {})})
        self.text_analyzer = TextAnalyzer(config.get("analyzer", {}))
        self.keyword_extractor = KeywordExtractor(config.get("analyzer", {}))
        self.summary_generator = SummaryGenerator(config.get("content", {}))
        self.email_sender = EmailSender(config.get("email", {}))
        
        # 调度器配置
        self.scheduler_config = config.get("scheduler", {})
        self.cron_expression = self.scheduler_config.get("cron_expression", "0 19 * * *")
        self.enabled = self.scheduler_config.get("enabled", True)
        
        # 初始化APScheduler
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
        
        # 运行状态
        self.is_running = False
        self.last_run_time = None
        self.last_run_status = None
        
        logger.info("工作流调度器初始化完成")
    
    def _job_listener(self, event):
        """
        任务事件监听器
        
        Args:
            event: 任务事件
        """
        if event.exception:
            logger.error(f"任务执行失败: {event.exception}")
            self.last_run_status = "failed"
        else:
            logger.info(f"任务执行成功: {event.job_id}")
            self.last_run_status = "success"
    
    def start(self):
        """
        启动调度器
        """
        if not self.enabled:
            logger.info("调度器已禁用")
            return
        
        try:
            # 添加定时任务
            self.scheduler.add_job(
                self.run_workflow,
                CronTrigger.from_crontab(self.cron_expression),
                id="daily_workflow",
                name="每日热点信息收集工作流",
                replace_existing=True
            )
            
            # 启动调度器
            self.scheduler.start()
            self.is_running = True
            
            logger.info(f"调度器已启动，定时任务: {self.cron_expression}")
            
        except Exception as e:
            logger.error(f"启动调度器失败: {e}", exc_info=True)
            raise
    
    def stop(self):
        """
        停止调度器
        """
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
            
            self.is_running = False
            logger.info("调度器已停止")
            
        except Exception as e:
            logger.error(f"停止调度器失败: {e}", exc_info=True)
    
    def run_workflow(self):
        """
        执行完整的工作流程
        """
        start_time = time.time()
        self.last_run_time = datetime.now()
        
        logger.info("=" * 50)
        logger.info("开始执行每日热点信息收集工作流")
        logger.info("=" * 50)
        
        try:
            # 步骤1: 收集信息
            logger.info("步骤1: 开始收集热点信息...")
            news_items = self._collect_news()
            
            if not news_items:
                logger.warning("未收集到任何新闻信息")
                return
            
            logger.info(f"收集到 {len(news_items)} 条新闻")
            
            # 步骤2: 分析和处理
            logger.info("步骤2: 开始分析和处理新闻...")
            processed_items = self._analyze_news(news_items)
            
            logger.info(f"处理完成，保留 {len(processed_items)} 条新闻")
            
            # 步骤3: 生成总结
            logger.info("步骤3: 开始生成总结...")
            html_content = self._generate_summary(processed_items)
            
            logger.info("总结生成完成")
            
            # 步骤4: 发送邮件
            logger.info("步骤4: 开始发送邮件...")
            success = self._send_email(html_content, processed_items)
            
            if success:
                logger.info("邮件发送成功")
            else:
                logger.error("邮件发送失败")
            
            # 记录执行结果
            elapsed_time = time.time() - start_time
            logger.info(f"工作流执行完成，耗时: {elapsed_time:.2f} 秒")
            
            self.last_run_status = "success" if success else "email_failed"
            
        except Exception as e:
            logger.error(f"工作流执行失败: {e}", exc_info=True)
            self.last_run_status = "failed"
    
    def _collect_news(self) -> List[NewsItem]:
        """
        收集新闻信息
        
        Returns:
            List[NewsItem]: 新闻列表
        """
        try:
            # 使用爬虫管理器收集新闻
            news_items = self.crawler_manager.run_all()
            
            # 记录统计信息
            stats = self.crawler_manager.get_statistics()
            logger.info(f"爬虫统计: {stats}")
            
            return news_items
            
        except Exception as e:
            logger.error(f"收集新闻失败: {e}", exc_info=True)
            return []
    
    def _analyze_news(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """
        分析和处理新闻
        
        Args:
            news_items: 原始新闻列表
            
        Returns:
            List[NewsItem]: 处理后的新闻列表
        """
        processed_items = []
        
        for item in news_items:
            try:
                # 分析文本
                analysis_result = self.text_analyzer.analyze_text(
                    item.title + " " + item.content
                )
                
                # 提取关键词
                keywords = self.keyword_extractor.extract_keywords_multi_method(
                    item.title + " " + item.content,
                    top_k=5
                )
                
                # 更新新闻条目
                item.keywords = [kw for kw, _ in keywords]
                item.popularity = int(analysis_result.get("hot_score", 0))
                
                # 重新分类（如果需要）
                if item.category == "综合":
                    item.category = self.text_analyzer.categorize_news(
                        item.title, item.content
                    )
                
                processed_items.append(item)
                
            except Exception as e:
                logger.warning(f"处理新闻失败: {e}")
                # 仍然保留这条新闻
                processed_items.append(item)
        
        # 按热度排序
        processed_items.sort(key=lambda x: x.popularity, reverse=True)
        
        # 限制总数量
        max_items = self.config.get("content", {}).get("max_total_items", 30)
        processed_items = processed_items[:max_items]
        
        return processed_items
    
    def _generate_summary(self, news_items: List[NewsItem]) -> str:
        """
        生成总结
        
        Args:
            news_items: 新闻列表
            
        Returns:
            str: HTML格式的总结
        """
        try:
            # 生成HTML总结
            html_content = self.summary_generator.generate(news_items)
            
            # 保存到文件（可选）
            self._save_summary_to_file(html_content)
            
            return html_content
            
        except Exception as e:
            logger.error(f"生成总结失败: {e}", exc_info=True)
            raise
    
    def _send_email(self, html_content: str, news_items: List[NewsItem]) -> bool:
        """
        发送邮件
        
        Args:
            html_content: HTML内容
            news_items: 新闻列表
            
        Returns:
            bool: 是否发送成功
        """
        try:
            # 生成邮件主题
            date_str = datetime.now().strftime("%Y年%m月%d日")
            subject = f"📰 今日热点资讯 - {date_str}"
            
            # 生成纯文本版本
            text_content = self.summary_generator.generate_text_summary(news_items)
            
            # 发送邮件
            success = self.email_sender.send(
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            return success
            
        except Exception as e:
            logger.error(f"发送邮件失败: {e}", exc_info=True)
            return False
    
    def _save_summary_to_file(self, html_content: str):
        """
        保存总结到文件
        
        Args:
            html_content: HTML内容
        """
        try:
            import os
            
            # 创建输出目录
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件名
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_{date_str}.html"
            filepath = os.path.join(output_dir, filename)
            
            # 保存文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"总结已保存到文件: {filepath}")
            
        except Exception as e:
            logger.warning(f"保存总结到文件失败: {e}")
    
    def run_once(self):
        """
        手动执行一次工作流
        """
        logger.info("手动触发工作流执行")
        self.run_workflow()
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取调度器状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        return {
            "is_running": self.is_running,
            "enabled": self.enabled,
            "cron_expression": self.cron_expression,
            "last_run_time": self.last_run_time.isoformat() if self.last_run_time else None,
            "last_run_status": self.last_run_status,
            "next_run_time": self._get_next_run_time(),
            "crawler_stats": self.crawler_manager.get_statistics(),
            "email_config": self.email_sender.get_config_info()
        }
    
    def _get_next_run_time(self) -> Optional[str]:
        """
        获取下次执行时间
        
        Returns:
            Optional[str]: 下次执行时间字符串
        """
        try:
            if self.scheduler.running:
                job = self.scheduler.get_job("daily_workflow")
                if job and job.next_run_time:
                    return job.next_run_time.isoformat()
        except:
            pass
        return None
    
    def update_schedule(self, cron_expression: str):
        """
        更新调度计划
        
        Args:
            cron_expression: cron表达式
        """
        try:
            self.cron_expression = cron_expression
            
            if self.scheduler.running:
                # 更新任务
                self.scheduler.reschedule_job(
                    "daily_workflow",
                    trigger=CronTrigger.from_crontab(cron_expression)
                )
            
            logger.info(f"调度计划已更新: {cron_expression}")
            
        except Exception as e:
            logger.error(f"更新调度计划失败: {e}", exc_info=True)
            raise
    
    def add_custom_crawler(self, crawler):
        """
        添加自定义爬虫
        
        Args:
            crawler: 爬虫实例
        """
        self.crawler_manager.add_crawler(crawler)
        logger.info(f"添加自定义爬虫: {crawler.name}")
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """
        获取工作流统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            "scheduler_status": self.get_status(),
            "total_runs": self._get_total_runs(),
            "success_rate": self._get_success_rate()
        }
    
    def _get_total_runs(self) -> int:
        """
        获取总运行次数
        
        Returns:
            int: 运行次数
        """
        # 这里可以扩展为从数据库或文件中读取历史记录
        return 1 if self.last_run_time else 0
    
    def _get_success_rate(self) -> float:
        """
        获取成功率
        
        Returns:
            float: 成功率百分比
        """
        # 这里可以扩展为计算历史成功率
        if self.last_run_status == "success":
            return 100.0
        elif self.last_run_status:
            return 0.0
        return 0.0