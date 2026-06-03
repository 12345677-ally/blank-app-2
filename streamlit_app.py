import streamlit as st
import time
from datetime import datetime
import json
import io

# --- 外部ライブラリのインポート ---
try:
    import PyPDF2
    import google.generativeai as genai
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False

# --- ページ設定 ---
st.set_page_config(page_title="AcademiaStream AI", layout="wide", page_icon="🎓")

# --- セッションステートの初期化 ---
if 'app_mode' not in st.session_state: st.session_state.app_mode = 'LEARN'
if 'phase' not in st.session_state: st.session_state.phase = 'UPLOAD'
if 'user_answers' not in st.session_state: st.session_state.user_answers = {}
if 'current_topic' not in st.session_state: st.session_state.current_topic = ""
if 'notes_history' not in st.session_state: st.session_state.notes_history = []
if 'test_history' not in st.session_state: st.session_state.test_history = []

# AI通信で生成されたデータを保持する変数
if 'generated_notes' not in st.session_state: st.session_state.generated_notes = None
if 'generated_test' not in st.session_state: st.session_state.generated_test = None

# --- サイドバー (ナビゲーション & API設定) ---
with st.sidebar:
    st.title("🎓 メニュー")
    if st.button("📝 学習を始める", use_container_width=True, type="primary" if st.session_state.app_mode == 'LEARN' else "secondary"):
        st.session_state.app_mode = 'LEARN'
        st.rerun()
    if st.button("📚 学習ノート一覧", use_container_width=True, type="primary" if st.session_state.app_mode == 'NOTES' else "secondary"):
        st.session_state.app_mode = 'NOTES'
        st.rerun()
    if st.button("📊 テスト結果履歴", use_container_width=True, type="primary" if st.session_state.app_mode == 'HISTORY' else "secondary"):
        st.session_state.app_mode = 'HISTORY'
        st.rerun()
    
    st.markdown("---")
    st.markdown("### ⚙️ API設定")
    api_key = st.text_input("Gemini API Key", type="password", help="Google AI Studioで取得したAPIキーを入力してください。")
    if api_key:
        genai.configure(api_key=api_key)
    
    st.markdown("---")
    st.markdown("### 今日の学習記録")
    st.metric("作成したノート数", len(st.session_state.notes_history))
    st.metric("完了したテスト数", len(st.session_state.test_history))

# --- 補助関数 ---
def extract_text_from_file(uploaded_file):
    """アップロードされたファイルからテキストを抽出する"""
    text = ""
    if uploaded_file.name.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    else:
        # テキストファイルとして読み込む
        text = uploaded_file.getvalue().decode("utf-8")
    return text[:15000] # APIの制限を考慮し、一旦最初の15000文字程度に制限

def generate_ai_content(prompt):
    """Gemini APIを呼び出してJSON形式でコンテンツを生成する"""
    model = genai.GenerativeModel(
        'gemini-1.5-flash',
        generation_config={
            "response_mime_type": "application/json",
        }
    )
    response = model.generate_content(prompt)
    return json.loads(response.text)

# =========================================================
# モード 1: 学習フロー (LEARN)
# =========================================================
if st.session_state.app_mode == 'LEARN':
    st.title("🎓 AcademiaStream AI - 学習モード")
    
    if not HAS_LIBS:
        st.error("必要なライブラリがインストールされていません。ターミナルで `pip install PyPDF2 google-generativeai` を実行してください。")
        st.stop()
    if not api_key:
        st.warning("👈 サイドバーにGemini APIキーを入力して学習を開始してください。")
        st.stop()

    # --- Phase 1: UPLOAD ---
    if st.session_state.phase == 'UPLOAD':
        st.header("1. 資料のアップロード")
        st.info("学習したい講義資料（PDFまたはテキスト）をアップロードしてください。")
        
        uploaded_file = st.file_uploader("資料をドロップまたは選択", type=['pdf', 'txt'])
        topic_name = st.text_input("今回のテーマ名を入力 (履歴保存用)", value="新しい学習テーマ")
        
        if uploaded_file and st.button("資料を読み込んで開始する", type="primary"):
            st.session_state.current_topic = topic_name
            
            with st.status("AIが資料を解析中...", expanded=True) as status:
                st.write("📄 資料からテキストを抽出しています...")
                document_text = extract_text_from_file(uploaded_file)
                
                st.write("🧠 学習ノート（インプット）を生成しています...")
                notes_prompt = f"""
                あなたは大学教授であり、優秀なチューターです。以下の[入力資料]を読み込み、学生が深く理解できるための学習ノートを作成してください。
                資料の性質を判定し、「プロセス・アルゴリズム型」「用語・概念型」「論理・構造型」のいずれかを `document_type` に入れてください。
                
                出力は以下のJSON形式を厳守してください。
                {{
                  "document_type": "タイプ名",
                  "overall_summary": "資料全体の目的と結論（300字程度）",
                  "core_question": "この資料を学ぶ上で核心となる問い（1文）",
                  "structured_explanation": [
                    {{"title": "見出し", "content": "概要", "detail": "詳細なメカニズムや理由", "keywords": "関連する重要用語"}}
                  ],
                  "glossary": [
                    {{"term": "用語", "definition": "詳細な定義"}}
                  ]
                }}
                
                [入力資料]:
                {document_text}
                """
                st.session_state.generated_notes = generate_ai_content(notes_prompt)
                
                st.write("📝 テスト問題（アウトプット）を生成しています...")
                test_prompt = f"""
                以下の[入力資料]に基づき、大学の期末試験レベルの小テストを作成してください。
                問題数は合計5問（選択式2問、穴埋め式2問、記述式1問）としてください。
                また、資料の性質に合わせて出題形式のバランスを最適化してください。
                
                出力は以下のJSON形式を厳守してください。
                {{
                  "test_strategy": "出題の意図（100字）",
                  "questions": [
                    {{
                      "id": "q_choice_1", "type": "choice",
                      "question": "問題文", "options": ["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
                      "correct_answer": "正解の選択肢の文字列を完全一致で", "explanation": "詳しい解説"
                    }},
                    {{
                      "id": "q_fill_1", "type": "fill",
                      "question": "〇〇は【　　】である。", "correct_keywords": ["正解キーワード1", "正解キーワード2"],
                      "explanation": "詳しい解説"
                    }},
                    {{
                      "id": "q_desc_1", "type": "descriptive",
                      "question": "〇〇について説明せよ。", "model_answer": "模範解答",
                      "key_elements": ["必須キーワード1", "必須キーワード2"], "explanation": "詳しい解説"
                    }}
                  ]
                }}
                
                [入力資料]:
                {document_text}
                """
                st.session_state.generated_test = generate_ai_content(test_prompt)
                
                status.update(label="解析完了！学習を開始します。", state="complete", expanded=False)
                time.sleep(1)
                st.session_state.phase = 'INPUT'
                st.rerun()

    # --- Phase 2: INPUT ---
    elif st.session_state.phase == 'INPUT':
        st.header(f"2. インプット: {st.session_state.current_topic}")
        notes = st.session_state.generated_notes
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.success(f"🤖 AIによる判定: この資料は **「{notes['document_type']}」** と判定されました。")
            
            st.subheader("📌 全体サマリー")
            st.write(notes['overall_summary'])
            
            st.info(f"💡 **核心となる問い**: {notes['core_question']}")
            
            st.subheader("📖 構造化解説")
            for section in notes['structured_explanation']:
                with st.expander(section['title'], expanded=True):
                    st.markdown(f"**概要**: {section['content']}")
                    st.markdown(f"**詳細**: {section['detail']}")
                    if section.get('keywords'):
                        st.markdown(f"**重要用語**: {section['keywords']}")

            st.subheader("📚 重要用語集")
            glossary_text = ""
            for item in notes['glossary']:
                glossary_text += f"- **{item['term']}**: {item['definition']}\n"
            st.markdown(glossary_text)
            
            if st.button("テストに進む (Output)", type="primary"):
                st.session_state.notes_history.append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "topic": st.session_state.current_topic,
                    "summary": notes['overall_summary'],
                    "content": {s['title']: s['content'] + "\n\n" + s['detail'] for s in notes['structured_explanation']},
                    "glossary": glossary_text
                })
                st.session_state.phase = 'TEST'
                st.rerun()
                
        with col2:
            st.subheader("🎯 学習のヒント")
            st.markdown("テストでは、用語の暗記だけでなく、「なぜそうなるのか」という理由やメカニズムを問う問題も出題されます。**構造化解説の「詳細」**部分をよく読んでおきましょう。")

    # --- Phase 3: TEST ---
    elif st.session_state.phase == 'TEST':
        st.header(f"3. テスト: {st.session_state.current_topic}")
