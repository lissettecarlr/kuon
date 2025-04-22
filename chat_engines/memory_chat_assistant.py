import os
import time
import sys
from typing import Dict, Any, Optional, List, Generator, Union
import threading
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken
import json
from loguru import logger

# 加载环境变量
load_dotenv()

# 配置日志
logger.remove()
logger.add(sys.stdout, level="INFO")


class MemoryChatAssistant:
    """带有长短期记忆功能的OpenAI对话客户端
    
    此类实现了一个智能对话系统，能够记住与用户的对话内容，并将重要信息压缩保存为长期记忆。
    支持自动内存管理、定时压缩和记忆持久化。
    """
    
    # 默认配置
    DEFAULT_MEMORY_MODEL = "gpt-4.1"
    DEFAULT_CHAT_MODEL = "gpt-4.1"
    DEFAULT_COMPRESS_INTERVAL = 600  # 10分钟
    DEFAULT_CONTEXT_MULTIPLIER = 0.5
    DEFAULT_MAX_MEMORIES = 1000
    
    # 模型上下文长度映射
    MODEL_CONTEXT_LENGTHS = {
        "gpt-4o": 128000,
        "gpt-4.1": 1047576,
        "gpt-4": 8192,
        "gpt-3.5-turbo": 4096
    }
    
    # 默认系统提示
    DEFAULT_SYSTEM_PROMPT = """
    你现在扮演的是久远（Kuon），《传颂之物》系列中的主要女主角之一。你是一位聪明、温柔、善良但有点傲娇的兽耳少女，还有一条长长的尾巴。智慧聪颖，精通医术，性格坚强且富有责任感。你有着神秘的身世，对朋友非常关心，喜欢用温柔的话语安慰他人。你的语气温和，有时会带点俏皮和腹黑，面对困境时总能冷静分析情况，做出明智的决策。请用久远的口吻和风格与我互动，展现她的性格和魅力。
    """
    
    def __init__(self, 
                 openai_api_key: str,
                 openai_base_url: str,
                 memory_model_name: str = DEFAULT_MEMORY_MODEL,
                 chat_model_name: str = DEFAULT_CHAT_MODEL,
                 compress_interval: int = DEFAULT_COMPRESS_INTERVAL,
                 context_length_multiplier: float = DEFAULT_CONTEXT_MULTIPLIER,
                 max_long_term_memories: int = DEFAULT_MAX_MEMORIES
                 ):
        """
        初始化带记忆功能的AI助手

        Args:
            openai_api_key: OpenAI API密钥
            openai_base_url: OpenAI API基础URL
            memory_model_name: 记忆模型名称
            chat_model_name: 聊天模型名称
            compress_interval: 记忆压缩时间间隔（秒），为0则不自动清除
            context_length_multiplier: 上下文长度倍率，范围0.1-1.0，降低可节省成本
            max_long_term_memories: 长期记忆的最大条目数
        """
        # API客户端设置
        self.client = OpenAI(api_key=openai_api_key, base_url=openai_base_url)
        self.chat_model_name = chat_model_name
        self.memory_model_name = memory_model_name
        
        # 内存管理设置
        self.compress_interval = compress_interval
        self.context_length_multiplier = max(0.1, min(1.0, context_length_multiplier))
        self.max_long_term_memories = max(10, max_long_term_memories)  # 至少保留10条记忆
        self.max_context_length = int(self._get_model_context_length(chat_model_name) * self.context_length_multiplier)
        
        # 记忆存储
        self.short_term_memory: List[Dict[str, str]] = []
        self.long_term_memory = []
        
        # 记忆持久化
        memory_file_path = "memory.json"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.memory_file_path = os.path.join(current_dir, memory_file_path)
        self.long_term_memory = self._load_long_term_memory()
        
        # 内部状态
        self.timer_last_conversation = None  # 记忆的定时器
        self.system_prompt = self.DEFAULT_SYSTEM_PROMPT
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4系列使用的编码器

        # 初始化日志
        logger.debug("初始化AI完成，使用模型: {}".format(chat_model_name))
        logger.debug(f"短期记忆最大token数: {self.max_context_length}")
        logger.debug(f"已加载长期记忆条目数: {len(self.long_term_memory)}")
        logger.debug(f"长期记忆最大条目数: {self.max_long_term_memories}")

    def _get_model_context_length(self, model_name: str) -> int:
        """根据模型名称获取对应的上下文长度限制"""
        return self.MODEL_CONTEXT_LENGTHS.get(model_name, 200000)

    def _count_tokens(self, messages: List[Dict[str, str]]) -> int:
        """计算消息列表的token数量"""
        num_tokens = 0
        for message in messages:
            # 每条消息的固定token开销
            num_tokens += 4  # 消息格式开销
            
            for key, value in message.items():
                num_tokens += len(self.tokenizer.encode(value))
                num_tokens += len(self.tokenizer.encode(key))
        
        # 格式收尾需要的token
        num_tokens += 2
        return num_tokens

    def chat(self, user_message: str) -> Generator[str, None, None]:
        """
        与AI助手对话，支持流式返回回复内容
        
        Args:
            user_message: 用户消息

        Yields:
            AI助手的回复内容片段
            
        Raises:
            RuntimeError: 当API调用失败时
        """
        # 构建对话上下文
        conversation = [
            {"role": "developer", "content": self.system_prompt},
        ]
        last_user_message = {"role": "user", "content": user_message}
        conversation.extend(self.long_term_memory)
        conversation.extend(self.short_term_memory)
        conversation.append(last_user_message)
        
        # 记录token使用情况
        total_tokens = self._count_tokens(conversation)
        logger.debug(f"当前对话总token数: {total_tokens}, 最大上下文限制: {self.max_context_length}")

        # 清除旧定时器
        if self.timer_last_conversation is not None:
            self.timer_last_conversation.cancel()

        # 调用API获取回复
        try:
            response = self.client.chat.completions.create(
                model=self.chat_model_name,
                messages=conversation,
                stream=True
            )
            
            # 流式处理回复
            full_response = ""
            for chunk in response:
                if chunk.choices[0].finish_reason == "stop":
                    break
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            # 更新短期记忆
            self.short_term_memory.append(last_user_message)
            self.short_term_memory.append({"role": "assistant", "content": full_response})

            # 检查是否需要压缩记忆
            self._check_and_compress_memory()
        
        except Exception as e:
            error_message = f"OpenAI API调用错误: {str(e)}"
            logger.error(error_message)
            raise RuntimeError(error_message)
        
        # 设置新定时器
        if self.compress_interval > 0:
            self.timer_last_conversation = threading.Timer(self.compress_interval, self._timeout_last_conversation)
            self.timer_last_conversation.start()
        
    def _timeout_last_conversation(self) -> None:
        """超时处理：将短期记忆转化为长期记忆"""
        self._convert_short_term_to_long_term()
        logger.debug("超时保存已完成，短期记忆已转化为长期记忆")
        
    def _check_and_compress_memory(self) -> None:
        """检查并在必要时压缩短期记忆"""
        tokens = self._count_tokens(self.short_term_memory)
        threshold = self.max_context_length * 0.5
        logger.debug(f"短期记忆token数: {tokens}, 压缩阈值: {threshold}")
        
        if tokens > threshold:
            logger.debug("短期记忆超过阈值，开始压缩")
            try:
                self._convert_short_term_to_long_term()
            except Exception as e:
                # 压缩失败的回退策略：保留最近几轮对话
                logger.error(f"短期记忆压缩失败: {e}")
                if len(self.short_term_memory) > 4:  # 如果对话超过2轮
                    logger.debug(f"保留最近2轮对话，丢弃 {len(self.short_term_memory) - 4} 条消息")
                    self.short_term_memory = self.short_term_memory[-4:]  # 保留最近2轮对话

    def _limit_long_term_memory(self) -> None:
        """
        限制长期记忆的大小并校验记忆格式
        
        规范要求:
        1. 每个记忆项必须包含role和content字段
        2. role必须是user或assistant
        3. user和assistant角色必须交替出现
        """
        if not self.long_term_memory:
            logger.debug("长期记忆为空，无需限制和校验")
            return
        
        # 校验并过滤记忆格式
        valid_memories = []
        invalid_count = 0
        expected_role = "user"  # 确保以user开始
        
        for memory in self.long_term_memory:
            # 基本格式检查
            if not isinstance(memory, dict) or "role" not in memory or "content" not in memory:
                logger.warning(f"发现无效记忆格式: {memory}")
                invalid_count += 1
                continue
            
            # 角色检查
            if memory["role"] not in ["user", "assistant"]:
                logger.warning(f"发现无效角色: {memory['role']}")
                invalid_count += 1
                continue
            
            # 角色顺序检查
            if memory["role"] != expected_role:
                logger.warning(f"角色顺序不符合预期，预期 {expected_role}，实际 {memory['role']}")
                if valid_memories and memory["role"] == valid_memories[-1]["role"]:
                    invalid_count += 1
                    continue
            
            # 更新下一个预期角色
            expected_role = "assistant" if memory["role"] == "user" else "user"
            valid_memories.append(memory)
        
        if invalid_count > 0:
            logger.warning(f"过滤了 {invalid_count} 条无效记忆")
            self.long_term_memory = valid_memories
        
        # 限制记忆数量
        if len(self.long_term_memory) > self.max_long_term_memories:
            removed_count = len(self.long_term_memory) - self.max_long_term_memories
            self.long_term_memory = self.long_term_memory[-self.max_long_term_memories:]
            logger.debug(f"长期记忆超出上限，移除了最早的 {removed_count} 条记忆，当前记忆数: {len(self.long_term_memory)}")
        
        # 确保记忆序列完整
        if len(self.long_term_memory) % 2 != 0:
            logger.warning("记忆数量不是偶数，可能缺少成对的对话")
            if self.long_term_memory and self.long_term_memory[-1]["role"] == "user":
                logger.warning("移除末尾不完整的user记忆")
                self.long_term_memory.pop()

    # ----- 记忆持久化方法 -----

    def _load_long_term_memory(self) -> List[Dict[str, str]]:
        """从文件加载长期记忆，如果文件不存在则创建空文件"""
        if os.path.exists(self.memory_file_path):
            try:
                with open(self.memory_file_path, 'r', encoding='utf-8') as f:
                    memory = json.load(f)
                    self.long_term_memory = memory
                    self._limit_long_term_memory()
                    return self.long_term_memory
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.error(f"加载长期记忆文件失败: {e}")
                return []
        else:
            # 创建空文件
            logger.debug(f"长期记忆文件不存在，创建新文件: {self.memory_file_path}")
            with open(self.memory_file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            return []
    
    def _save_long_term_memory(self) -> None:
        """保存长期记忆到文件"""
        try:
            self._limit_long_term_memory()
            with open(self.memory_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.long_term_memory, f, ensure_ascii=False, indent=2)
                logger.debug(f"已保存 {len(self.long_term_memory)} 条长期记忆到 {self.memory_file_path}")
        except Exception as e:
            logger.error(f"保存长期记忆文件失败: {e}")
    
    # ----- 记忆压缩和处理方法 -----
    
    def _compress_conversations(self) -> List[Dict[str, str]]:
        """
        压缩短期记忆为重要记忆列表
        
        Returns:
            压缩后的记忆列表，格式为[{"role":"user","content":"..."}, {"role":"assistant","content":"..."}]
        """
        if not self.short_term_memory:
            logger.debug("短期记忆为空，无需压缩")
            return []
        
        # 压缩提示
        system_message = {
            "role": "developer",
            "content":"""
            对话内容精简提纯
            你的任务是从对话中提取重要信息并精简为简洁的对话对。
            必须返回JSON数组格式如下：
            [
                {"role":"user","content":"用户的重要信息"},
                {"role":"assistant","content":"助手的回应"}
            ]
            规则：
            1. 必须保持user和assistant角色交替出现
            2. 保留用户个人信息、偏好和重要事件
            3. 删除无实质内容的客套话，例如问好等。
            4. 内容精简，对长内容进行精简，只保留关键内容，适应AI的处理能力。
            5. 当不存在重要信息时，返回空数组。
            """  
        }
        
        try:
            # 构建压缩请求
            prompt_message = {
                "role": "user",
                "content": f"请从以下对话中提取重要记忆：\n\n{str(self.short_term_memory)}"
            }
            
            # 调用API进行压缩
            response = self.client.chat.completions.create(
                model=self.memory_model_name,
                messages=[system_message, prompt_message],
                temperature=0.5
            )
            
            response_content = response.choices[0].message.content
            result = self._parse_memory_response(response_content)
            return result
                
        except Exception as e:
            logger.error(f"记忆压缩错误: {e}")
            raise RuntimeError(f"记忆压缩过程中发生错误: {str(e)}")

    def _parse_memory_response(self, response_content: str) -> List[Dict[str, str]]:
        """解析记忆压缩API的响应内容"""
        try:
            memory_data = json.loads(response_content)

            # 处理常见返回格式情况
            if isinstance(memory_data, dict) and "memories" in memory_data:
                logger.debug("从'memories'键获取记忆列表")
                return memory_data["memories"]
            
            elif isinstance(memory_data, list):
                if all(isinstance(item, dict) and "role" in item and "content" in item for item in memory_data):
                    return memory_data
                else:
                    logger.error("返回的记忆格式不符合要求")
                    raise ValueError("记忆压缩失败：返回的记忆格式不符合要求")
            
            # 尝试从其他键中获取记忆列表
            else:
                for key, value in memory_data.items():
                    if isinstance(value, list):
                        if all(isinstance(item, dict) and "role" in item and "content" in item for item in value):
                            logger.debug(f"从键'{key}'获取记忆列表")
                            return value
                
                # 没有找到有效的记忆列表
                logger.error("API返回格式不符合预期")
                raise ValueError("记忆压缩失败：API返回格式不符合预期")
                
        except json.JSONDecodeError:
            logger.error(f"JSON解析错误: {response_content[:100]}...")
            raise ValueError(f"记忆提取时遇到JSON解析错误: {response_content[:100]}...")
        
    def _convert_short_term_to_long_term(self) -> None:
        """将短期记忆转化为长期记忆并保存"""
        if len(self.short_term_memory) == 0:
            logger.debug("短期记忆为空，无需转换")
            return
        try:
            logger.debug("开始将短期记忆转换为长期记忆")
            compressed_memories = self._compress_conversations()
            if compressed_memories:
                logger.debug(f"添加 {len(compressed_memories)} 条压缩记忆到长期记忆")
                self.long_term_memory.extend(compressed_memories)
                self.short_term_memory = []  # 清空短期记忆
                logger.debug("清空短期记忆")
                self._save_long_term_memory()
            else:
                logger.debug("压缩后无有效记忆，跳过保存")
                
        except Exception as e:
            logger.error(f"短期记忆转化为长期记忆失败: {e}")
            raise RuntimeError(f"短期记忆转化为长期记忆失败: {str(e)}")
    
    # ----- 公共接口 -----
            
    def clear_memory(self, clear_type: str = "all") -> None:
        """
        清除助手的记忆
        
        Args:
            clear_type: 清除类型，可以是'all'、'short_term'或'long_term'
        """
        if clear_type in ["all", "short_term"]:
            self.short_term_memory = []
            logger.info("短期记忆已清除")
            
        if clear_type in ["all", "long_term"]:
            self.long_term_memory = []
            self._save_long_term_memory()
            logger.info("长期记忆已清除")

    def exit(self) -> None:
        """退出对话，保存记忆并清理资源"""
        # 关闭定时器
        if self.timer_last_conversation is not None:
            self.timer_last_conversation.cancel()
        # 将短期记忆转化为长期记忆
        self._convert_short_term_to_long_term()


# ----- 测试和辅助函数 -----

def main():
    """交互式测试MemoryChatAssistant的主函数"""
    # 从环境变量中读取配置
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    if not api_key:
        logger.error("错误: 未找到OPENAI_API_KEY环境变量")
        print("错误: 未找到OPENAI_API_KEY环境变量")
        return

    client = MemoryChatAssistant(
        openai_api_key=api_key,
        openai_base_url=api_base,
        memory_model_name="gpt-4.1",
        chat_model_name="gpt-4.1",
        context_length_multiplier=0.5,  # 默认使用模型上下文长度的50%
        max_long_term_memories=100,  # 默认最多保存100条长期记忆
        compress_interval=60,  # 默认每60秒压缩一次
    )
    
    print("欢迎使用带记忆功能的AI助手!")
    print("输入'退出'或'exit'结束对话")
    print("输入'清除记忆'清除所有记忆")
    print("输入'保存记忆'保存短期记忆到长期记忆")

    while True:
        user_input = input("\n用户: ")
        
        if user_input.lower() in ["退出", "exit", "quit", "q"]:
            print("谢谢使用，再见!")
            client.exit()
            break
            
        if user_input == "清除记忆":
            client.clear_memory()
            continue
            
        if user_input == "保存记忆":
            client._convert_short_term_to_long_term()
            print("短期记忆已保存到长期记忆")
            continue
            
        print("\nAI助手: ", end="")
        try:
            for chunk in client.chat(user_input):
                print(chunk, end="", flush=True)
            print()  # 换行
        except Exception as e:
            print(f"\n对话出错: {e}")


def test_compress_conversations():
    """测试对话压缩功能"""
    # 使用环境变量
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_BASE_URL", "")
    
    # 初始化客户端
    client = MemoryChatAssistant(
        openai_api_key=api_key,
        openai_base_url=api_base,
        memory_model_name="gpt-4.1",
        chat_model_name="gpt-4.1",
        context_length_multiplier=0.5,  # 使用50%的上下文长度
    )
    
    logger.info("开始测试对话压缩功能")
    
    client.short_term_memory = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你也好"},
        {"role": "user", "content": "你好，我是小明。我喜欢打篮球。"},
        {"role": "assistant", "content": "你好，小明。我也喜欢打篮球。"},
        {"role": "user", "content": "你喜欢吃什么水果？"},
        {"role": "assistant", "content": "我喜欢吃苹果。"},
    ]
    
    logger.info(f"测试短期记忆条数: {len(client.short_term_memory)}")
    compressed_memories = client._compress_conversations()
    logger.info(f"压缩后记忆条数: {len(compressed_memories)}")
    print("压缩结果:", compressed_memories)
    return compressed_memories


# 示例环境变量设置（仅供参考，实际使用时应通过.env文件或系统环境变量设置）
# $env:OPENAI_API_KEY ="YOUR_API_KEY"
# $env:OPENAI_BASE_URL = "https://api.example.com/v1"

if __name__ == "__main__":
    main()


