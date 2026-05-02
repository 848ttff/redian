"""
邮件发送器模块
提供HTML邮件发送功能，支持重试机制
"""

import smtplib
import logging
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailSender:
    """
    邮件发送器
    支持HTML格式邮件发送和重试机制
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化邮件发送器
        
        Args:
            config: 配置字典，包含以下字段：
                - smtp_server: SMTP服务器地址
                - smtp_port: SMTP端口
                - use_tls: 是否使用TLS
                - sender_email: 发送者邮箱
                - sender_password: 发送者密码/授权码
                - sender_name: 发送者显示名称
                - recipients: 收件人列表
                - retry_count: 重试次数
                - retry_delay: 重试延迟（秒）
        """
        self.config = config
        
        # SMTP配置
        self.smtp_server = config.get("smtp_server", "")
        self.smtp_port = config.get("smtp_port", 587)
        self.use_tls = config.get("use_tls", True)
        
        # 发送者配置
        self.sender_email = config.get("sender_email", "")
        self.sender_password = config.get("sender_password", "")
        self.sender_name = config.get("sender_name", "热点资讯日报")
        
        # 收件人配置
        self.recipients = config.get("recipients", [])
        
        # 重试配置
        self.retry_count = config.get("retry_count", 3)
        self.retry_delay = config.get("retry_delay", 5)
        
        # 验证配置
        self._validate_config()
        
        logger.info(f"邮件发送器初始化完成，SMTP服务器: {self.smtp_server}:{self.smtp_port}")
    
    def _validate_config(self):
        """
        验证邮件配置
        """
        if not self.smtp_server:
            logger.warning("未配置SMTP服务器地址")
        
        if not self.sender_email:
            logger.warning("未配置发送者邮箱")
        
        if not self.sender_password:
            logger.warning("未配置发送者密码/授权码")
        
        if not self.recipients:
            logger.warning("未配置收件人")
    
    def send(self, subject: str, html_content: str, text_content: str = None) -> bool:
        """
        发送邮件
        
        Args:
            subject: 邮件主题
            html_content: HTML内容
            text_content: 纯文本内容（可选，作为备用）
            
        Returns:
            bool: 是否发送成功
        """
        if not self._can_send():
            logger.error("邮件配置不完整，无法发送")
            return False
        
        # 创建邮件消息
        message = self._create_message(subject, html_content, text_content)
        
        # 带重试的发送
        for attempt in range(1, self.retry_count + 1):
            try:
                logger.info(f"尝试发送邮件 (第 {attempt}/{self.retry_count} 次)")
                
                # 发送邮件
                success = self._send_email(message)
                
                if success:
                    logger.info(f"邮件发送成功，收件人: {', '.join(self.recipients)}")
                    return True
                else:
                    logger.warning(f"邮件发送失败 (第 {attempt} 次)")
                    
            except Exception as e:
                logger.error(f"邮件发送异常 (第 {attempt} 次): {e}")
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < self.retry_count:
                logger.info(f"等待 {self.retry_delay} 秒后重试...")
                time.sleep(self.retry_delay)
        
        logger.error(f"邮件发送失败，已重试 {self.retry_count} 次")
        return False
    
    def _can_send(self) -> bool:
        """
        检查是否可以发送邮件
        
        Returns:
            bool: 是否可以发送
        """
        return all([
            self.smtp_server,
            self.sender_email,
            self.sender_password,
            self.recipients
        ])
    
    def _create_message(self, subject: str, html_content: str, text_content: str = None) -> MIMEMultipart:
        """
        创建邮件消息
        
        Args:
            subject: 邮件主题
            html_content: HTML内容
            text_content: 纯文本内容
            
        Returns:
            MIMEMultipart: 邮件消息对象
        """
        # 创建多部分消息
        message = MIMEMultipart('alternative')
        
        # 设置邮件头
        message['Subject'] = subject
        message['From'] = f"{self.sender_name} <{self.sender_email}>"
        message['To'] = ', '.join(self.recipients)
        message['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # 添加纯文本部分
        if text_content:
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            message.attach(text_part)
        
        # 添加HTML部分
        html_part = MIMEText(html_content, 'html', 'utf-8')
        message.attach(html_part)
        
        return message
    
    def _send_email(self, message: MIMEMultipart) -> bool:
        """
        发送邮件（内部方法）
        
        Args:
            message: 邮件消息对象
            
        Returns:
            bool: 是否发送成功
        """
        server = None
        try:
            # 创建SMTP连接
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.settimeout(30)  # 设置超时时间
            
            # 启用调试模式（可选）
            # server.set_debuglevel(1)
            
            # 使用TLS
            if self.use_tls:
                server.starttls()
            
            # 登录
            server.login(self.sender_email, self.sender_password)
            
            # 发送邮件
            server.sendmail(
                self.sender_email,
                self.recipients,
                message.as_string()
            )
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP认证失败: {e}")
            return False
            
        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP连接失败: {e}")
            return False
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP错误: {e}")
            return False
            
        except Exception as e:
            logger.error(f"发送邮件时发生未知错误: {e}")
            return False
            
        finally:
            # 关闭连接
            if server:
                try:
                    server.quit()
                except:
                    pass
    
    def send_with_attachment(
        self, 
        subject: str, 
        html_content: str, 
        attachments: List[Dict[str, str]] = None,
        text_content: str = None
    ) -> bool:
        """
        发送带附件的邮件
        
        Args:
            subject: 邮件主题
            html_content: HTML内容
            attachments: 附件列表，每个附件是字典，包含：
                - filename: 文件名
                - path: 文件路径
                - content: 文件内容（可选，与path二选一）
            text_content: 纯文本内容
            
        Returns:
            bool: 是否发送成功
        """
        if not self._can_send():
            logger.error("邮件配置不完整，无法发送")
            return False
        
        # 创建邮件消息
        message = self._create_message_with_attachments(
            subject, html_content, attachments, text_content
        )
        
        # 带重试的发送
        for attempt in range(1, self.retry_count + 1):
            try:
                logger.info(f"尝试发送带附件的邮件 (第 {attempt}/{self.retry_count} 次)")
                
                # 发送邮件
                success = self._send_email(message)
                
                if success:
                    logger.info(f"带附件的邮件发送成功，收件人: {', '.join(self.recipients)}")
                    return True
                else:
                    logger.warning(f"带附件的邮件发送失败 (第 {attempt} 次)")
                    
            except Exception as e:
                logger.error(f"带附件的邮件发送异常 (第 {attempt} 次): {e}")
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < self.retry_count:
                logger.info(f"等待 {self.retry_delay} 秒后重试...")
                time.sleep(self.retry_delay)
        
        logger.error(f"带附件的邮件发送失败，已重试 {self.retry_count} 次")
        return False
    
    def _create_message_with_attachments(
        self, 
        subject: str, 
        html_content: str, 
        attachments: List[Dict[str, str]] = None,
        text_content: str = None
    ) -> MIMEMultipart:
        """
        创建带附件的邮件消息
        
        Args:
            subject: 邮件主题
            html_content: HTML内容
            attachments: 附件列表
            text_content: 纯文本内容
            
        Returns:
            MIMEMultipart: 邮件消息对象
        """
        # 创建多部分消息
        message = MIMEMultipart('mixed')
        
        # 设置邮件头
        message['Subject'] = subject
        message['From'] = f"{self.sender_name} <{self.sender_email}>"
        message['To'] = ', '.join(self.recipients)
        message['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # 创建内容部分
        content_part = MIMEMultipart('alternative')
        
        # 添加纯文本部分
        if text_content:
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            content_part.attach(text_part)
        
        # 添加HTML部分
        html_part = MIMEText(html_content, 'html', 'utf-8')
        content_part.attach(html_part)
        
        # 添加内容部分到主消息
        message.attach(content_part)
        
        # 添加附件
        if attachments:
            for attachment in attachments:
                try:
                    self._add_attachment(message, attachment)
                except Exception as e:
                    logger.warning(f"添加附件失败: {e}")
        
        return message
    
    def _add_attachment(self, message: MIMEMultipart, attachment: Dict[str, str]):
        """
        添加附件到邮件
        
        Args:
            message: 邮件消息对象
            attachment: 附件信息字典
        """
        filename = attachment.get('filename', 'attachment')
        filepath = attachment.get('path')
        content = attachment.get('content')
        
        if filepath:
            # 从文件读取
            with open(filepath, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
        elif content:
            # 从内容创建
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(content.encode('utf-8'))
        else:
            logger.warning(f"附件 {filename} 没有内容")
            return
        
        # 编码附件
        encoders.encode_base64(part)
        
        # 添加附件头
        part.add_header(
            'Content-Disposition',
            'attachment',
            filename=('utf-8', '', filename)
        )
        
        message.attach(part)
    
    def test_connection(self) -> bool:
        """
        测试SMTP连接
        
        Returns:
            bool: 连接是否成功
        """
        if not self.smtp_server:
            logger.error("未配置SMTP服务器")
            return False
        
        server = None
        try:
            logger.info(f"测试SMTP连接: {self.smtp_server}:{self.smtp_port}")
            
            # 创建SMTP连接
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.settimeout(10)
            
            # 使用TLS
            if self.use_tls:
                server.starttls()
            
            # 登录（如果配置了凭据）
            if self.sender_email and self.sender_password:
                server.login(self.sender_email, self.sender_password)
            
            logger.info("SMTP连接测试成功")
            return True
            
        except Exception as e:
            logger.error(f"SMTP连接测试失败: {e}")
            return False
            
        finally:
            if server:
                try:
                    server.quit()
                except:
                    pass
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        获取配置信息（隐藏敏感信息）
        
        Returns:
            Dict[str, Any]: 配置信息
        """
        return {
            "smtp_server": self.smtp_server,
            "smtp_port": self.smtp_port,
            "use_tls": self.use_tls,
            "sender_email": self.sender_email[:3] + "***" + self.sender_email[self.sender_email.find('@'):] if self.sender_email else "",
            "sender_name": self.sender_name,
            "recipients_count": len(self.recipients),
            "retry_count": self.retry_count,
            "retry_delay": self.retry_delay
        }