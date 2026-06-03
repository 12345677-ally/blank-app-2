import streamlit as st
import time
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="AcademiaStream AI", layout="wide", page_icon="🎓")

# --- セッションステートの初期化 ---
# アプリのメインモード: 'LEARN' (学習フロー), 'NOTES' (ノート履歴), 'HISTORY' (テスト履歴)
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = 'LEARN'

# 学習フロー内のフェーズ: 'UPLOAD', 'INPUT', 'TEST', 'REVIEW'
if 'phase' not in st.session_state:
    st.session_state.phase = 'UPLOAD'

# 進行中のデータ
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = ""

# 履歴保存用リスト
if 'notes_history' not in st.session_state:
    st.session_state.notes_history = []
if 'test_history' not in st.session_state:
    st.session_state.test_history = []

# --- サイドバー (ナビゲーション) ---
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
    st.markdown("### 今日の学習記録")
    st.metric("作成したノート数", len(st.session_state.notes_history))
    st.metric("完了したテスト数", len(st.session_state.test_history))

# =========================================================
# モード 1: 学習フロー (LEARN)
# =========================================================
if st.session_state.app_mode == 'LEARN':
    st.title("🎓 AcademiaStream AI - 学習モード")
    st.markdown("大学の専門資料をAIが解析し、あなた専用の学習環境を構築します。")

    # --- Phase 1: UPLOAD ---
    if st.session_state.phase == 'UPLOAD':
        st.header("1. 資料のアップロード")
        st.info("学習したい講義資料（PDF, Word, テキストなど）をアップロードしてください。")
        
        uploaded_file = st.file_uploader("資料をドロップまたは選択", type=['pdf', 'txt', 'docx'])
        
        # モック用の開始ボタン
        topic_name = st.text_input("（デモ用）今回のテーマ名を入力", value="決定木アルゴリズム基礎")
        if st.button("資料を読み込んで開始する", type="primary"):
            st.session_state.current_topic = topic_name
            with st.spinner('AIが資料を解析し、最適な学習コンテンツを生成しています...'):
                time.sleep(2)
                st.session_state.phase = 'INPUT'
                st.rerun()

    # --- Phase 2: INPUT ---
    elif st.session_state.phase == 'INPUT':
        st.header(f"2. インプット: {st.session_state.current_topic}")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.success("🤖 AIによる解析完了: この資料は **「プロセス・アルゴリズム型」** と判定されました。")
            
            st.subheader("📌 全体サマリー")
            summary_text = "本資料は、機械学習における「決定木アルゴリズム」の構築プロセスと、情報利得を用いた分岐条件の計算方法について解説しています。不純度の概念を理解することが重要です。"
            st.write(summary_text)
            
            st.subheader("📖 構造化解説（ステップ）")
            with st.expander("Step 1: 不純度の計算", expanded=True):
                step1_text = "**内容**: ノード内のデータの混ざり具合を計算します。\n**重要用語**: ジニ不純度、エントロピー"
                st.markdown(step1_text)
            with st.expander("Step 2: 情報利得の算出"):
                step2_text = "**内容**: 分割前後の不純度の差（情報利得）を計算し、最も利得が大きい特徴量を探します。"
                st.markdown(step2_text)
            
            # 学習ノートを履歴に保存する処理（1回だけ保存する工夫が必要だが今回はモックとしてボタンで進む際に保存）
            if st.button("テストに進む (Output)", type="primary"):
                # ノート履歴に保存
                st.session_state.notes_history.append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "topic": st.session_state.current_topic,
                    "summary": summary_text,
                    "content": {"Step 1": step1_text, "Step 2": step2_text}
                })
                st.session_state.phase = 'TEST'
                st.rerun()
                
        with col2:
            st.subheader("📑 資料アウトライン")
            st.markdown("- 1. 決定木とは\n- 2. 分割の基準\n- 3. アルゴリズムの実装")

    # --- Phase 3: TEST ---
    elif st.session_state.phase == 'TEST':
        st.header(f"3. テスト: {st.session_state.current_topic}")
        st.write("解説を非表示にしました。集中して解答してください。")
        
        with st.form("test_form"):
            st.subheader("Q1. 選択式問題")
            q1_ans = st.radio("データが完全に1つのクラスに属している場合、ジニ不純度の値は？", ["0", "0.5", "1"], index=None)
            
            st.markdown("---")
            st.subheader("Q2. 穴埋め式問題")
            q2_ans = st.text_input("分割前後の不純度の差のことを【　　】と呼ぶ。")
            
            submitted = st.form_submit_button("解答を提出して採点する", type="primary")
            if submitted:
                st.session_state.user_answers = {'q1': q1_ans, 'q2': q2_ans}
                st.session_state.phase = 'REVIEW'
                st.rerun()

    # --- Phase 4: REVIEW ---
    elif st.session_state.phase == 'REVIEW':
        st.header(f"4. 採点と復習: {st.session_state.current_topic}")
        ans = st.session_state.user_answers
        
        col1, col2 = st.columns([2, 1])
        score = 0
        
        with col1:
            st.subheader("Q1. 選択式")
            if ans.get('q1') == "0":
                st.success(f"解答: {ans.get('q1')} ⭕ 正解！")
                score += 1
            else:
                st.error(f"解答: {ans.get('q1')} ❌ 不正解 (正解: 0)")
            
            st.markdown("---")
            st.subheader("Q2. 穴埋め式")
            q2_correct = ["情報利得", "インフォメーションゲイン"]
            user_q2 = str(ans.get('q2')).strip()
            if any(kw in user_q2 for kw in q2_correct):
                st.success(f"解答: {user_q2} ⭕ 正解！")
                score += 1
            else:
                st.error(f"解答: {user_q2} ❌ 不正解 (正解: 情報利得)")

        with col2:
            st.subheader("📊 今回のスコア")
            st.metric(label="正答数", value=f"{score} / 2 問")
            
            st.markdown("### 次のアクション")
            if st.button("💾 結果を保存して終了する", type="primary"):
                # テスト履歴に保存
                st.session_state.test_history.append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "topic": st.session_state.current_topic,
                    "score": f"{score}/2",
                    "details": ans
                })
                # 初期状態に戻す
                st.session_state.phase = 'UPLOAD'
                st.session_state.current_topic = ""
                st.rerun()

# =========================================================
# モード 2: 学習ノート一覧 (NOTES)
# =========================================================
elif st.session_state.app_mode == 'NOTES':
    st.title("📚 学習ノート一覧")
    st.markdown("過去にAIが作成した解説ノートを振り返ることができます。")
    
    if not st.session_state.notes_history:
        st.info("保存された学習ノートはまだありません。")
    else:
        # 最新のものが上に来るように逆順で表示
        for i, note in enumerate(reversed(st.session_state.notes_history)):
            with st.container(border=True):
                st.subheader(f"{note['topic']}")
                st.caption(f"作成日時: {note['date']}")
                st.write(note['summary'])
                with st.expander("詳細な解説を開く"):
                    for title, content in note['content'].items():
                        st.markdown(f"**{title}**\n{content}\n")

# =========================================================
# モード 3: テスト結果履歴 (HISTORY)
# =========================================================
elif st.session_state.app_mode == 'HISTORY':
    st.title("📊 テスト結果履歴")
    st.markdown("過去に受けたテストのスコアと解答内容を確認して、弱点を克服しましょう。")
    
    if not st.session_state.test_history:
        st.info("保存されたテスト結果はまだありません。")
    else:
        for i, test in enumerate(reversed(st.session_state.test_history)):
            with st.container(border=True):
                cols = st.columns([3, 1])
                with cols[0]:
                    st.subheader(f"{test['topic']}")
                    st.caption(f"実施日時: {test['date']}")
                with cols[1]:
                    st.metric("スコア", test['score'])
                
                with st.expander("あなたの解答詳細を見る"):
                    st.write(f"**Q1解答:** {test['details'].get('q1')}")
                    st.write(f"**Q2解答:** {test['details'].get('q2')}")
                    # 再テスト機能のモック
                    st.button("このテーマをもう一度テストする", key=f"retest_{i}")
