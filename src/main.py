"""
主程序入口
提供命令行接口和系统启动功能
"""

import sys
import argparse
import signal
import logging
from typing import Optional

from .config import ConfigLoader, Settings
from .schedulers import WorkflowScheduler
from .utils import setup_logger

logger = logging.getLogger(__name__)


def parse_args():
    """
    解析命令行参数
    
    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(
        description="热点信息自动收集与处理系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --run-once           # 手动执行一次收集任务
  %(prog)s --start-scheduler    # 启动定时任务调度器
  %(prog)s --test-email         # 测试邮件发送
  %(prog)s --create-config      # 创建示例配置文件
        """
    )
    
    # 操作模式
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--run-once",
        action="store_true",
        help="手动执行一次收集任务"
    )
    mode_group.add_argument(
        "--start-scheduler",
        action="store_true",
        help="启动定时任务调度器"
    )
    mode_group.add_argument(
        "--test-email",
        action="store_true",
        help="测试邮件发送"
    )
    mode_group.add_argument(
        "--test-connection",
        action="store_true",
        help="测试SMTP连接"
    )
    mode_group.add_argument(
        "--create-config",
        action="store_true",
        help="创建示例配置文件"
    )
    mode_group.add_argument(
        "--show-config",
        action="store_true",
        help="显示当前配置"
    )
    mode_group.add_argument(
        "--list-crawlers",
        action="store_true",
        help="列出所有可用的爬虫"
    )
    
    # 配置选项
    parser.add_argument(
        "--config-dir",
        type=str,
        default="config",
        help="配置文件目录 (默认: config)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=None,
        help="日志级别"
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs",
        help="日志目录 (默认: logs)"
    )
    
    return parser.parse_args()


def load_config(config_dir: str) -> Optional[Settings]:
    """
    加载配置
    
    Args:
        config_dir: 配置目录
        
    Returns:
        Optional[Settings]: 配置对象，失败返回None
    """
    try:
        loader = ConfigLoader(config_dir)
        config_dict = loader.load_config()
        
        # 创建Settings对象
        settings = Settings.from_dict(config_dict)
        
        # 验证配置
        validation = settings.validate()
        
        if validation["errors"]:
            for error in validation["errors"]:
                logger.error(f"配置错误: {error}")
            return None
        
        if validation["warnings"]:
            for warning in validation["warnings"]:
                logger.warning(f"配置警告: {warning}")
        
        return settings
        
    except Exception as e:
        logger.error(f"加载配置失败: {e}", exc_info=True)
        return None


def run_once(settings: Settings):
    """
    手动执行一次收集任务
    
    Args:
        settings: 配置对象
    """
    logger.info("手动执行收集任务...")
    
    try:
        # 创建调度器
        scheduler = WorkflowScheduler(settings.to_dict())
        
        # 执行一次
        scheduler.run_once()
        
        logger.info("手动执行完成")
        
    except Exception as e:
        logger.error(f"手动执行失败: {e}", exc_info=True)
        sys.exit(1)


def start_scheduler(settings: Settings):
    """
    启动定时任务调度器
    
    Args:
        settings: 配置对象
    """
    logger.info("启动定时任务调度器...")
    
    try:
        # 创建调度器
        scheduler = WorkflowScheduler(settings.to_dict())
        
        # 启动调度器
        scheduler.start()
        
        logger.info("调度器已启动，按 Ctrl+C 停止")
        
        # 保持主线程运行
        def signal_handler(signum, frame):
            logger.info("收到停止信号，正在关闭...")
            scheduler.stop()
            sys.exit(0)
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 保持运行
        while True:
            import time
            time.sleep(1)
        
    except KeyboardInterrupt:
        logger.info("收到键盘中断，正在关闭...")
        if 'scheduler' in locals():
            scheduler.stop()
    except Exception as e:
        logger.error(f"启动调度器失败: {e}", exc_info=True)
        sys.exit(1)


def test_email(settings: Settings):
    """
    测试邮件发送
    
    Args:
        settings: 配置对象
    """
    logger.info("测试邮件发送...")
    
    try:
        from .mailers import EmailSender
        from .summarizers import SummaryGenerator
        
        # 创建邮件发送器
        email_sender = EmailSender(settings.get_email_config())
        
        # 创建测试内容
        summary_generator = SummaryGenerator(settings.get_content_config())
        
        # 生成测试邮件内容
        test_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>测试邮件</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>热点信息收集系统测试邮件</h1>
        </div>
        <div class="content">
            <p>这是一封测试邮件，用于验证邮件发送功能是否正常。</p>
            <p>如果您收到此邮件，说明邮件配置正确。</p>
            <p>系统将在每日19:00自动发送热点资讯汇总。</p>
        </div>
        <div class="footer">
            <p>发送时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
        
        # 发送测试邮件
        success = email_sender.send(
            subject="📰 热点信息收集系统 - 测试邮件",
            html_content=test_html,
            text_content="这是一封测试邮件，用于验证邮件发送功能是否正常。"
        )
        
        if success:
            logger.info("测试邮件发送成功！")
        else:
            logger.error("测试邮件发送失败！")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"测试邮件发送失败: {e}", exc_info=True)
        sys.exit(1)


def test_connection(settings: Settings):
    """
    测试SMTP连接
    
    Args:
        settings: 配置对象
    """
    logger.info("测试SMTP连接...")
    
    try:
        from .mailers import EmailSender
        
        # 创建邮件发送器
        email_sender = EmailSender(settings.get_email_config())
        
        # 测试连接
        success = email_sender.test_connection()
        
        if success:
            logger.info("SMTP连接测试成功！")
        else:
            logger.error("SMTP连接测试失败！")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"SMTP连接测试失败: {e}", exc_info=True)
        sys.exit(1)


def create_config(config_dir: str):
    """
    创建示例配置文件
    
    Args:
        config_dir: 配置目录
    """
    logger.info("创建示例配置文件...")
    
    try:
        loader = ConfigLoader(config_dir)
        loader.create_example_config()
        
        logger.info("示例配置文件创建成功！")
        logger.info("请编辑以下文件进行配置:")
        logger.info(f"  - {config_dir}/settings.yaml  (主配置)")
        logger.info(f"  - {config_dir}/sources.yaml   (信息源配置)")
        logger.info(f"  - .env                    (环境变量)")
        
    except Exception as e:
        logger.error(f"创建配置文件失败: {e}", exc_info=True)
        sys.exit(1)


def show_config(settings: Settings):
    """
    显示当前配置
    
    Args:
        settings: 配置对象
    """
    import json
    
    config_dict = settings.to_dict()
    
    # 隐藏敏感信息
    if "email" in config_dict:
        email_config = config_dict["email"]
        if "sender_password" in email_config:
            email_config["sender_password"] = "***" if email_config["sender_password"] else ""
    
    print("\n当前配置:")
    print("=" * 60)
    print(json.dumps(config_dict, indent=2, ensure_ascii=False))
    print("=" * 60)


def list_crawlers(settings: Settings):
    """
    列出所有可用的爬虫
    
    Args:
        settings: 配置对象
    """
    from .crawlers import CrawlerManager
    
    logger.info("列出所有可用的爬虫...")
    
    try:
        # 创建爬虫管理器
        crawler_manager = CrawlerManager({"sources": settings.get_sources_config()})
        
        # 获取爬虫列表
        crawlers = crawler_manager.list_crawlers()
        
        print("\n可用的爬虫:")
        print("=" * 60)
        print(f"{'名称':<20} {'类型':<20} {'状态':<10} {'最大条目':<10}")
        print("-" * 60)
        
        for crawler in crawlers:
            status = "启用" if crawler["enabled"] else "禁用"
            print(f"{crawler['name']:<20} {crawler['type']:<20} {status:<10} {crawler['max_items']:<10}")
        
        print("=" * 60)
        print(f"总计: {len(crawlers)} 个爬虫")
        
    except Exception as e:
        logger.error(f"列出爬虫失败: {e}", exc_info=True)
        sys.exit(1)


def main():
    """
    主函数
    """
    # 解析命令行参数
    args = parse_args()
    
    # 设置日志
    log_level = args.log_level or "INFO"
    setup_logger(log_level=log_level, log_dir=args.log_dir)
    
    logger.info("=" * 60)
    logger.info("热点信息自动收集与处理系统")
    logger.info("=" * 60)
    
    # 处理创建配置命令（不需要加载配置）
    if args.create_config:
        create_config(args.config_dir)
        return
    
    # 加载配置
    settings = load_config(args.config_dir)
    
    if settings is None:
        logger.error("配置加载失败，请检查配置文件")
        sys.exit(1)
    
    # 覆盖日志级别
    if args.log_level:
        settings.system.log_level = args.log_level
    
    # 根据参数执行相应操作
    if args.run_once:
        run_once(settings)
    elif args.start_scheduler:
        start_scheduler(settings)
    elif args.test_email:
        test_email(settings)
    elif args.test_connection:
        test_connection(settings)
    elif args.show_config:
        show_config(settings)
    elif args.list_crawlers:
        list_crawlers(settings)
    else:
        # 默认显示帮助
        parse_args()


if __name__ == "__main__":
    main()