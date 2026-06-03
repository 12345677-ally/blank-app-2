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
            summary_text = "本資料は、機械学習における「決定木アルゴリズム」の構築プロセスと、情報利得を用いた分岐条件の計算方法について解説しています。データをどのように分割すれば最も効率よく分類できるかを決定するための、ジニ不純度やエントロピーといった指標の理解が不可欠です。"
            st.write(summary_text)
            
            st.info("💡 **核心となる問い**: 「複雑なデータを、最もシンプルな質問の繰り返しで分類するにはどうすればよいか？」")
            
            st.subheader("📖 構造化解説（ステップ）")
            with st.expander("Step 1: 不純度（Impurity）の計算", expanded=True):
                step1_text = "**内容**: ノード内のデータの混ざり具合（純度）を計算します。値が小さいほど、同じクラスのデータが集まっている（純度が高い）ことを意味します。\n\n**詳細**: 決定木は、データを分割する前と後で「どれだけデータがきれいに分かれたか」を評価します。その評価基準となるのが不純度です。代表的な指標として「ジニ不純度」と「エントロピー」があり、どちらも完全に1つのクラスに分類できている場合は `0` になります。\n\n**重要用語**: ジニ不純度、エントロピー"
                st.markdown(step1_text)
            with st.expander("Step 2: 情報利得（Information Gain）の算出"):
                step2_text = "**内容**: 親ノードの不純度から、子ノードの不純度の加重平均を引いた値（情報利得）を計算します。この値が最大になる特徴量を分岐条件として採用します。\n\n**詳細**: どの質問（特徴量と閾値）でデータを分割すれば一番うまく分類できるかを決めるステップです。分割前後の不純度の差が一番大きい＝一番情報が整理された（情報利得が最大）、という基準で最適な分岐点を探します。"
                st.markdown(step2_text)
            with st.expander("Step 3: 再帰的な分割と過学習（Overfitting）の防止"):
                step3_text = "**内容**: Step1と2を繰り返しデータを分割し続けますが、最後まで分割しきると訓練データに適合しすぎる「過学習」が起きます。そのため、木の深さに制限を設ける（剪定）ことが重要です。\n\n**詳細**: アルゴリズムをそのまま放置すると、データが1件になるまで分岐を続けてしまいます（深さ最大）。これは訓練データのノイズまで丸暗記している状態で、未知のデータへの予測性能が落ちます。これを防ぐため、「深さは最大5まで」「1つの葉には最低10件のデータが必要」といった制約（事前剪定）を設けます。"
                st.markdown(step3_text)

            st.subheader("📚 重要用語集")
            glossary_text = """
- **決定木 (Decision Tree)**: ツリー状の構造を用いて分類や回帰を行う機械学習モデル。
- **ノード (Node)**: 木の分岐点。最初のノードを「根ノード(Root)」、途中の分岐を「内部ノード」、末端を「葉ノード(Leaf)」と呼ぶ。
- **過学習 (Overfitting)**: 訓練データに過剰に適合し、未知のデータに対する汎化性能が低下する現象。
- **剪定 (Pruning)**: 過学習を防ぐために、決定木の成長を制限したり、一度成長させた木の一部を切り落とす手法。
            """
            st.markdown(glossary_text)
            
            # 学習ノートを履歴に保存する処理
            if st.button("テストに進む (Output)", type="primary"):
                # ノート履歴に保存
                st.session_state.notes_history.append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "topic": st.session_state.current_topic,
                    "summary": summary_text,
                    "content": {
                        "Step 1: 不純度の計算": step1_text, 
                        "Step 2: 情報利得の算出": step2_text, 
                        "Step 3: 再帰的な分割と過学習の防止": step3_text,
                        "重要用語集": glossary_text
                    }
                })
                st.session_state.phase = 'TEST'
                st.rerun()
                
        with col2:
            st.subheader("📑 資料アウトライン")
            st.markdown("- 1. 決定木とは\n- 2. 分割の基準\n  - 2.1 ジニ不純度\n  - 2.2 エントロピー\n- 3. アルゴリズムの実装\n- 4. 過学習と剪定")

    # --- Phase 3: TEST ---
    elif st.session_state.phase == 'TEST':
        st.header(f"3. テスト: {st.session_state.current_topic}")
        st.write("解説を非表示にしました。集中して解答してください。")
        
        with st.form("test_form"):
            st.subheader("【選択式】")
            q1_ans = st.radio("Q1. データが完全に1つのクラスに属している場合、ジニ不純度の値は？", ["0", "0.5", "1"], index=None)
            q2_ans = st.radio("Q2. 次のうち、決定木アルゴリズムが分岐条件を決定する際に「最大化」しようとする指標はどれか？", ["ジニ不純度", "エントロピー", "情報利得", "学習率"], index=None)
            
            st.markdown("---")
            st.subheader("【穴埋め式】")
            q3_ans = st.text_input("Q3. 親ノードの不純度から、子ノードの不純度の加重平均を引いた値のことを【　　】と呼ぶ。")
            q4_ans = st.text_input("Q4. 決定木が訓練データに適合しすぎてしまい、未知のデータに対する予測精度が下がる現象を【　　】という。")
            
            st.markdown("---")
            st.subheader("【記述式】")
            q5_ans = st.text_area("Q5. 決定木モデルにおいて、Q4の現象を防ぐための具体的な対策を1つ挙げ、簡潔に説明せよ。")
            
            submitted = st.form_submit_button("解答を提出して採点する", type="primary")
            if submitted:
                st.session_state.user_answers = {'q1': q1_ans, 'q2': q2_ans, 'q3': q3_ans, 'q4': q4_ans, 'q5': q5_ans}
                st.session_state.phase = 'REVIEW'
                st.rerun()

    # --- Phase 4: REVIEW ---
    elif st.session_state.phase == 'REVIEW':
        st.header(f"4. 採点と復習: {st.session_state.current_topic}")
        ans = st.session_state.user_answers
        
        col1, col2 = st.columns([2, 1])
        score = 0
        max_score = 4 # 自動採点対象の問題数
        
        with col1:
            st.subheader("【選択式】")
            # Q1 レビュー
            st.markdown("**Q1. データが完全に1つのクラスに属している場合、ジニ不純度の値は？**")
            if ans.get('q1') == "0":
                st.success(f"あなたの解答: {ans.get('q1')} ⭕ 正解！")
                score += 1
            else:
                st.error(f"あなたの解答: {ans.get('q1')} ❌ 不正解 (正解: 0)")
            with st.expander("Q1の詳細解説を読む"):
                st.write("ジニ不純度はデータの「混ざり具合」を示します。ノード内のデータがすべて同じクラス（例えばすべて「犬」）であれば、混ざり具合はゼロとなるため、ジニ不純度も『0』になります。計算式上、純度が最も高い状態です。")
            
            # Q2 レビュー
            st.markdown("**Q2. 決定木アルゴリズムが分岐条件を決定する際に「最大化」しようとする指標はどれか？**")
            if ans.get('q2') == "情報利得":
                st.success(f"あなたの解答: {ans.get('q2')} ⭕ 正解！")
                score += 1
            else:
                st.error(f"あなたの解答: {ans.get('q2')} ❌ 不正解 (正解: 情報利得)")
            with st.expander("Q2の詳細解説を読む"):
                st.write("決定木は『どれだけ情報を整理できたか（不純度を減らせたか）』を基準に分岐を行います。この整理できた度合いを**情報利得（Information Gain）**と呼びます。ジニ不純度やエントロピーは、情報利得を計算するための「不純度の指標」であり、これら自体は「最小化」されるべきものです。")

            st.markdown("---")
            st.subheader("【穴埋め式】")
            # Q3 レビュー
            st.markdown("**Q3. 親ノードの不純度から、子ノードの不純度の加重平均を引いた値のことを【　　】と呼ぶ。**")
            q3_correct = ["情報利得", "インフォメーションゲイン"]
            user_q3 = str(ans.get('q3')).strip()
            if any(kw in user_q3 for kw in q3_correct):
                st.success(f"あなたの解答: {user_q3} ⭕ 正解！")
                score += 1
            else:
                st.error(f"あなたの解答: {user_q3} ❌ 不正解 (正解: 情報利得)")
            
            # Q4 レビュー
            st.markdown("**Q4. 訓練データに適合しすぎて未知のデータに対する予測精度が下がる現象を【　　】という。**")
            q4_correct = ["過学習", "オーバーフィッティング"]
            user_q4 = str(ans.get('q4')).strip()
            if any(kw in user_q4 for kw in q4_correct):
                st.success(f"あなたの解答: {user_q4} ⭕ 正解！")
                score += 1
            else:
                st.error(f"あなたの解答: {user_q4} ❌ 不正解 (正解: 過学習)")
            
            with st.expander("Q4の詳細解説を読む"):
                st.write("決定木は条件分岐を細かく繰り返すことで、訓練データを100%正確に分類する木を作ることができます。しかし、細かすぎる条件は『そのデータ特有のノイズ』まで学習してしまうため、新しい未知のデータが来た時に上手く分類できなくなります。これを**過学習（オーバーフィッティング）**と呼びます。")

            st.markdown("---")
            st.subheader("【記述式】(自己採点)")
            st.markdown("**Q5. 決定木モデルにおいて、Q4の現象(過学習)を防ぐための具体的な対策を1つ挙げ、簡潔に説明せよ。**")
            st.info(f"**あなたの解答:**\n\n{ans.get('q5')}")
            
            st.markdown("**🤖 模範解答:**")
            st.write("> **剪定（プルーニング）を行う。** または **木の深さ（max_depth）に制限を設ける。** 分岐の回数や葉ノードのデータ数に制限をかけることで、木が複雑になりすぎるのを防ぐ。")
            
            st.markdown("**📌 採点基準（必須キーワード）:** `剪定` または `深さの制限`")
            
            st.write("模範解答と照らし合わせて、自己評価をしてください。")
            btn_cols = st.columns(3)
            with btn_cols[0]:
                if st.button("🟢 完璧 (3点)"): st.toast("素晴らしい！知識が定着しています。")
            with btn_cols[1]:
                if st.button("🟡 だいたい合ってる (2点)"): st.toast("惜しい！キーワードを再確認しましょう。")
            with btn_cols[2]:
                if st.button("🔴 やり直し (0点)"): st.toast("次は正解できるように復習しましょう！")

        with col2:
            st.subheader("📊 今回のスコア")
            st.metric(label="自動採点正答数", value=f"{score} / {max_score} 問")
            st.caption("※記述式のスコアは自己評価となります。")
            
            st.markdown("### 次のアクション")
            if st.button("💾 結果を保存して終了する", type="primary"):
                # テスト履歴に保存
                st.session_state.test_history.append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "topic": st.session_state.current_topic,
                    "score": f"{score}/{max_score}",
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
                    st.metric("自動採点スコア", test['score'])
                
                with st.expander("あなたの解答詳細を見る"):
                    st.write(f"**Q1 (選択):** {test['details'].get('q1')}")
                    st.write(f"**Q2 (選択):** {test['details'].get('q2')}")
                    st.write(f"**Q3 (穴埋め):** {test['details'].get('q3')}")
                    st.write(f"**Q4 (穴埋め):** {test['details'].get('q4')}")
                    st.write(f"**Q5 (記述):** {test['details'].get('q5')}")
                    # 再テスト機能のモック
                    st.button("このテーマをもう一度テストする", key=f"retest_{i}")
