import re
import requests
import json
import html
import streamlit as st
import datetime
from datetime import datetime

# 设置页面配置，使用机器人emoji作为图标
st.set_page_config(
    page_title="Cookie-AI智能助手",
    page_icon="🤖",  # 使用机器人emoji作为图标
    layout="wide"
)

# 添加 post_process_latex 函数的定义
def post_process_latex(text):
    """
    后处理 AI 输出，确保数学公式被正确包裹在 $$ 符号内
    """
    # 移除多余的 $ 符号
    text = re.sub(r'\${2,}', '$$', text)
    
    # 查找可能的公式开始和结束
    pattern = r'(\\begin\{.*?\}|\\end\{.*?\}|\\\[|\\\]|\\(|\\))'
    
    def replace_func(match):
        formula = match.group(1)
        if formula in ['\\(', '\\)']:
            return '$$'
        if formula in ['\\[', '\\]']:
            return '$$'
        return formula
    
    # 使用正则表达式查找可能的公式边界并替换
    processed_text = re.sub(pattern, replace_func, text)
    
    return processed_text

# API设置部分保留在侧边栏
with st.sidebar.form(key="api_settings_form"):
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        st.subheader("API 设置")
    with col2:
        submit_button = st.form_submit_button("保存新设置")
    with col3:
        reset_button = st.form_submit_button("恢复默认设置")
    
    default_api_key = "sk-1xOLoJ1NRluWwc5oC5Cc8f32E8D940C791AdEb8b656bD4C6"
    default_api_base = "https://api.tu-zi.com"
    default_model = "gpt-4o-all"
    
    if 'api_key' not in st.session_state:
        st.session_state.api_key = default_api_key
    if 'api_base' not in st.session_state:
        st.session_state.api_base = default_api_base
    if 'model' not in st.session_state:
        st.session_state.model = default_model
    
    if 'show_default' not in st.session_state:
        st.session_state.show_default = {'api_key': True, 'api_base': True, 'model': True}
    
    api_key = st.text_input("API密钥", 
                            value="默认" if st.session_state.show_default['api_key'] else st.session_state.api_key, 
                            type="password", 
                            key="api_key_input")
    api_base = st.text_input("API基础URL", 
                             value="默认" if st.session_state.show_default['api_base'] else st.session_state.api_base, 
                             key="api_base_input")
    
    # 使用下拉选择框替代文本输入框
    available_models = [
        "gpt-4o-all",
        "gpt-4o",
        "gpt-4o-mini",
        "claude-3-5-sonnet-20240620",
        "claude-3-5-sonnet-20240620-fast",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20241022-fast",
        "claude-3-5-haiku-20241022-fast",
        "openai-gpt-4o",
        "OpenAI-gpt-4o",
        "Claude-claude-3-5-sonnet-20240620",
        "Claude-claude-3-5-sonnet-20241022",
        "o1-mini-all",
        "o1-preview-all",
        "openai-dall-e-3",
        "o1-preview-fast",
        "o1-mini-fast",
    ]
    model = st.selectbox(
        "模型名称",
        options=available_models,
        index=available_models.index(default_model) if default_model in available_models else 0,
        key="model_input"
    )
    
    if submit_button:
        st.session_state.api_key = default_api_key if api_key == "默认" else api_key
        st.session_state.api_base = default_api_base if api_base == "默认" else api_base
        st.session_state.model = model
        st.session_state.show_default = {
            'api_key': api_key == "默认",
            'api_base': api_base == "默认",
            'model': model == default_model
        }
        st.success("API设置已更新")
    
    if reset_button:
        st.session_state.api_key = default_api_key
        st.session_state.api_base = default_api_base
        st.session_state.model = default_model
        st.session_state.show_default = {'api_key': True, 'api_base': True, 'model': True}
        st.success("API设置已恢复为默认值")
        st.rerun()  # 重新运行应用以更新输入框的显示

# 主要内容移到主区域
st.markdown("""
    # 🤖 Cookie-AI智能助手
    #### ✅连续对话 | 🌐实时联网 | 🎯精准回答
""", unsafe_allow_html=True)

# 在初始化聊天历史和上下文的部分之前添加
if 'sessions' not in st.session_state:
    st.session_state.sessions = {}
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = 'default'
    st.session_state.sessions['default'] = {
        'chat_history': [],
        'chat_context': [],
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'title': '新会话'
    }

# 初始化聊天历史和上下文时修改为
if st.session_state.current_session_id not in st.session_state.sessions:
    st.session_state.sessions[st.session_state.current_session_id] = {
        'chat_history': [],
        'chat_context': [],
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'title': '新会话'
    }

# 替换所有 st.session_state.chat_history 为
# st.session_state.sessions[st.session_state.current_session_id]['chat_history']
# 替换所有 st.session_state.chat_context 为
# st.session_state.sessions[st.session_state.current_session_id]['chat_context']

system_message = """你叫Cookie，是一个专业、友好的AI助手。你能够回答各种领域的问题，解释复杂概念，并协助用户完成各种任务。
请用清晰、易懂的语言回答问题，适时使用例子来说明，必要时可以使用图表或公式来辅助解释。
回答时保持友好和专业，适当使用emoji让对话更生动，对用户保持积极鼓励的态度。"""

# 使用保存的设置
api_key_to_use = st.session_state.api_key
api_base_to_use = st.session_state.api_base
model_to_use = st.session_state.model

def latex_to_streamlit(text):
    """将文本中的LaTeX公式转换为Streamlit支持的格式"""
    # 行内公式
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text)
    # 行间公式
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text)
    return text

def render_message(message):
    """渲染消息，处理LaTeX公式"""
    # 分割文本和公式
    parts = re.split(r'(\$\$.*?\$\$|\$.*?\$)', message)
    for part in parts:
        if part.startswith('$') and part.endswith('$'):
            # 这是一个公式，使用 st.latex 渲染
            st.latex(part.strip('$'))
        else:
            # 这是普通文本，使用 st.markdown 渲染
            st.markdown(part)

# 创建一个空的容器用于显示AI响应
ai_response_container = st.empty()

# 修改自定义CSS样式部分

st.markdown("""
<style>
.chat-message {
    padding: 0.5rem; 
    border-radius: 0.5rem; 
    margin-bottom: 1rem; 
    display: flex;
    align-items: flex-start;
}
.chat-message.user {
    background-color: #E6FFE6;  /* 淡绿色 */
    justify-content: flex-end;
}
.chat-message.bot {
    background-color: #FFE6E6;  /* 淡粉色 */
}
.chat-message .message {
    width: 100%;
    padding: 0.5rem 1rem;
    color: #333;  /* 深灰色文字，确保在浅色背景上可读 */
}
.chat-message.user .message {
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

# 显示聊天历史
for message in st.session_state.sessions[st.session_state.current_session_id]['chat_history']:
    if isinstance(message, tuple) and message[0] == "image":
        st.image(message[1], use_column_width=True)
    elif message.startswith("你:"):
        st.markdown(f'''
        <div class="chat-message user">
            <div class="message"><strong>:You</strong> 🙋<br>{html.escape(message[3:])}</div>
        </div>
        ''', unsafe_allow_html=True)
    elif message.startswith("AI:"):
        st.markdown(f'''
        <div class="chat-message bot">
            <div class="message">🤖 <strong>Cookie:</strong><br>{post_process_latex(message[3:])}</div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.text(message)

# 定义API调用函数
def simplify_context(context, max_messages=7):
    if len(context) <= max_messages:
        return context
    
    # 保留系统消息（如果存在）
    simplified = [msg for msg in context if msg["role"] == "system"]
    
    # 添加最近的消息，确保用户和助手的消息交替出现
    recent_messages = context[-max_messages:]
    for i, msg in enumerate(recent_messages):
        if i == 0 and msg["role"] == "assistant":
            simplified.append({"role": "user", "content": "继续我们的对话。"})
        simplified.append(msg)
    
    return simplified

def stream_api_call(context):
    headers = {
        "Authorization": f"Bearer {api_key_to_use}",
        "Content-Type": "application/json"
    }
    
    simplified_context = simplify_context(context)
    
    if simplified_context[0]["role"] != "system":
        simplified_context.insert(0, {"role": "system", "content": system_message})
    
    data = {
        "model": model_to_use,
        "messages": simplified_context,
        "max_tokens": 1000,
        "stream": True
    }
    
    try:
        url = f"{api_base_to_use}/v1/chat/completions"
        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status()
        
        full_response = ""
        response_container = st.empty()
        
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8').split('data: ')[1])
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        if 'delta' in chunk['choices'][0] and 'content' in chunk['choices'][0]['delta']:
                            content = chunk['choices'][0]['delta']['content']
                            full_response += content
                            processed_response = post_process_latex(full_response)
                            response_container.markdown(processed_response)
                except json.JSONDecodeError:
                    continue
                except IndexError:
                    continue
        
        return post_process_latex(full_response)
    except Exception as e:
        return f"API请求错误: {str(e)}"

# 添加新的辅助函数用于处理文档
def process_document(file):
    """
    处理上传的文档，提取文本内容
    """
    import io
    import docx
    import PyPDF2
    from PIL import Image
    
    file_extension = file.name.lower().split('.')[-1]
    
    try:
        if file_extension == 'pdf':
            # 处理PDF文件
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.getvalue()))
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            return text_content
            
        elif file_extension in ['doc', 'docx']:
            # 处理Word文档
            doc = docx.Document(io.BytesIO(file.getvalue()))
            text_content = ""
            for para in doc.paragraphs:
                text_content += para.text + "\n"
            return text_content
            
        elif file_extension in ['png', 'jpg', 'jpeg']:
            # 处理图片，返回base64编码
            import base64
            return base64.b64encode(file.getvalue()).decode('utf-8')
            
        else:
            return None
    except Exception as e:
        st.error(f"处理文件时出错: {str(e)}")
        return None

# 创建一个表单来包含输入框、发送按钮和清空聊天按钮
with st.form(key="chat_form", clear_on_submit=True):
    # 创建三列布局
    col1, col2, col3 = st.columns([9, 0.6, 0.6])
    
    # 在第一列放置输入框
    with col1:
        user_input = st.text_input(
            "输入问题:", 
            key="user_input", 
            label_visibility="collapsed", 
            placeholder="有什么我可以帮你的吗？"
        )
        
    # 在第二列放置发送按钮
    with col2:
        submit_button = st.form_submit_button(
            "**✈️**",
            help="发送消息"  # 当鼠标悬停时显示的提示文本
        )
    
    # 在第三列放置清空聊天按钮
    with col3:
        clear_button = st.form_submit_button(
            "🔄",
            help="清空当前对话，开始新会话"
        )
    
    # 添加文件上传器，并应用自定义样式
    uploaded_file = st.file_uploader(
        "上传文件", 
        type=["png", "jpg", "jpeg", "pdf", "doc", "docx"], 
        key="file_uploader"
    )
    st.markdown('<style>div[data-testid="stFileUploader"] {margin-bottom: -15px;}</style>', unsafe_allow_html=True)

# 处理表单提交
if submit_button:
    if api_key_to_use and (user_input or uploaded_file):
        # 如果是新会话且用户输入了问题，将第一个问题设置为标题
        current_session = st.session_state.sessions[st.session_state.current_session_id]
        if len(current_session['chat_history']) == 0 and user_input:
            # 截取前20个字符作为标题，如果超过20个字符则添加省略号
            title = user_input[:20] + ('...' if len(user_input) > 20 else '')
            current_session['title'] = title

        if user_input:
            st.session_state.sessions[st.session_state.current_session_id]['chat_history'].append(f"你: {user_input}")
            st.session_state.sessions[st.session_state.current_session_id]['chat_context'].append({"role": "user", "content": user_input})
        
        if uploaded_file:
            file_extension = uploaded_file.name.lower().split('.')[-1]
            
            if file_extension in ['png', 'jpg', 'jpeg']:
                # 处理图片
                image_base64 = process_document(uploaded_file)
                image_url = f"data:image/jpeg;base64,{image_base64}"
                st.session_state.sessions[st.session_state.current_session_id]['chat_history'].append(("image", uploaded_file))
                st.session_state.sessions[st.session_state.current_session_id]['chat_context'].append({"role": "user", "content": [
                    {"type": "text", "text": user_input if user_input else "请分析这张图片"},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]})
            else:
                # 处理文档
                document_content = process_document(uploaded_file)
                if document_content:
                    prompt = f"""请分析以下文档内容：\n\n{document_content}\n\n"""
                    if user_input:
                        prompt += f"用户的具体问题是：{user_input}"
                    else:
                        prompt += "请总结文档的主要内容，并提供关键信息分析。"
                    
                    st.session_state.sessions[st.session_state.current_session_id]['chat_history'].append(f"你: [上传了文件 {uploaded_file.name}] {user_input if user_input else ''}")
                    st.session_state.sessions[st.session_state.current_session_id]['chat_context'].append({"role": "user", "content": prompt})
        
        # 调用API
        with st.spinner('🤖 Claude正在思考中...'):
            ai_response = stream_api_call(st.session_state.sessions[st.session_state.current_session_id]['chat_context'])
        
        # 更新聊天历史和上下文
        processed_response = post_process_latex(ai_response)
        # 移除这一行，因为用户消息已经在前面添加过了
        # st.session_state.chat_history.append(f"你: {user_input}")
        st.session_state.sessions[st.session_state.current_session_id]['chat_history'].append(f"AI: {processed_response}")
        st.session_state.sessions[st.session_state.current_session_id]['chat_context'].append({"role": "assistant", "content": ai_response})
        
        # 显示AI响应
        st.markdown(f'<div class="chat-message bot"><div class="message"><strong>AI:</strong><br>{processed_response}</div></div>', unsafe_allow_html=True)
        
        # 清空上传的文件
        st.session_state.last_uploaded_image = None
        
        # 重新加载页面以显示新消息
        st.rerun()
    else:
        st.warning("请输入API密钥和问题或上传文件。")

# 处理清空聊天按钮点击事件
if clear_button:
    new_session_id = f"会话_{len(st.session_state.sessions)}"
    st.session_state.sessions[new_session_id] = {
        'chat_history': [],
        'chat_context': [],
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'title': '新会话'
    }
    st.session_state.current_session_id = new_session_id
    st.session_state.last_uploaded_image = None
    ai_response_container.empty()
    st.rerun()

# 添加声明
st.markdown(
    """
    <div style="background-color: #E6F3FF; padding: 10px; border-radius: 5px; color: #003366;">
    ⚠️ <strong>温馨提示</strong> AI助手会尽力提供准确的信息，但回答仅供参考。重要决策请自行验证。
    </div>
    """,
    unsafe_allow_html=True
)

# 在API设置部分之后，主要内容之前的会话管理部分修改为
with st.sidebar:
    st.markdown("## 会话管理")
    
    # 获取所有会话并按时间戳倒序排序
    sorted_sessions = sorted(
        st.session_state.sessions.items(),
        key=lambda x: x[1]['timestamp'],
        reverse=True  # 最新的在前
    )
    
    # 为每个会话创建一个行
    for session_id, session_data in sorted_sessions:
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # 创建一个按钮，显示会话标题
            is_current = session_id == st.session_state.current_session_id
            
            if st.button(
                session_data.get('title', '新会话'),
                key=f"session_btn_{session_id}",
                use_container_width=True,
                type="secondary" if is_current else "secondary"
            ):
                st.session_state.current_session_id = session_id
                st.rerun()
        
        with col2:
            # 只要有多个会话就显示删除按钮（移除了对当前会话的限制）
            if len(st.session_state.sessions) > 1:
                if st.button(
                    "🗑️",
                    key=f"delete_btn_{session_id}",
                    help="删除此会话"
                ):
                    # 删除会话
                    del st.session_state.sessions[session_id]
                    # 如果删除的是当前会话，切换到最新的会话
                    if session_id == st.session_state.current_session_id:
                        # 重新获取排序后的会话列表
                        remaining_sessions = sorted(
                            st.session_state.sessions.items(),
                            key=lambda x: x[1]['timestamp'],
                            reverse=True
                        )
                        # 切换到最新的会话
                        st.session_state.current_session_id = remaining_sessions[0][0]
                    st.rerun()
