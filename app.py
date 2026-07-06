import streamlit as st
import os
import pandas as pd
import time # 追加
# --- 設定 ---
# プロジェクトフォルダ内に "images" というフォルダを作成し、
# 建築物名に対応する画像ファイル（例: 水堀.png）を格納してください。
IMAGE_DIR = "images"

st.set_page_config(page_title="城建設クラフト", layout="centered")

# --- セッション状態の初期化 ---
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        '水': 0, '草': 0, '木材': 0, '石材': 0, 
        '銅鉱石': 0, '鉄鉱石': 0, '銀鉱石': 0, '金鉱石': 0, 'チタン鉱石': 0,
        '粘土': 0, '火薬': 0, 'ガラス': 0, '水晶': 0, 'プラスチック': 0,
        'ルビー': 0, 'サファイア': 0, 'エメラルド': 0, 'アメジスト': 0, 'ダイヤモンド': 0
    }
if 'buildings' not in st.session_state:
    st.session_state.buildings = []
if 'map_data' not in st.session_state:
    st.session_state.map_data = {}
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()
if 'drills' not in st.session_state:
    st.session_state.drills = {mat: 0 for mat in st.session_state.inventory.keys()}
# レシピ定義
# 拡張版RECIPESの例
RECIPES = {
    # 既存の基本建築
    "水堀": {"水": 5},
    # 石材レベル
    "石の監視棟": {"石材": 10},
    "石弓兵": {"石材": 15, "木材": 5}, # 追加：防衛部隊
    # 金属レベル
    "銅の監視棟": {"銅鉱石": 10},
    "銅の弓兵": {"銅鉱石": 15, "木材": 5}, # 追加：防衛部隊
    "鉄の監視棟": {"鉄鉱石": 10},
    "鉄の砲兵": {"鉄鉱石": 30},
    "鉄の銃兵": {"鉄鉱石": 20},
    # 希少資源レベル
    "銀の装飾棟": {"銀鉱石": 20}, # 追加：城の豪華さを上げる
    "金の装飾棟": {"金鉱石": 20}, # 追加：城の豪華さを上げる
    "未来の防衛棟": {"チタン鉱石": 50},
    "ガラスの装飾棟": {"ガラス": 10},
    "火薬庫": {"火薬": 10, "石材": 5},
    "水晶の塔": {"水晶": 20},
    "プラスチックの防衛棟": {"プラスチック": 20},
    
    "重装甲バリケード": {"鉄鉱石": 20, "石材": 15, "粘土": 10},
    "対空砲台": {"鉄鉱石": 30, "火薬": 10, "ガラス": 5},
    "未来のレーザー塔": {"チタン鉱石": 30, "水晶": 15, "プラスチック": 10},
    # 資源・インフラ施設
    "高性能精錬所": {"鉄鉱石": 20, "銀鉱石": 10, "金鉱石": 5},
    # 装飾・特殊施設
    "クリスタル温室": {"水晶": 10, "ガラス": 15, "草": 20},
    "記念碑": {"金鉱石": 20, "銀鉱石": 20, "石材": 30},

    "ルビーの装甲壁": {"ルビー": 5, "鉄鉱石": 10},
    "サファイアの監視塔": {"サファイア": 5, "石材": 20},
    "エメラルド精錬所": {"エメラルド": 5, "銀鉱石": 15, "プラスチック": 5},
    "アメジスト魔導塔": {"アメジスト": 10, "水晶": 10, "火薬": 5},
    "ダイヤモンドの記念碑": {"ダイヤモンド": 3, "金鉱石": 20, "銀鉱石": 20},

    "ルビーの溶岩forge": {"ルビー": 5, "鉄鉱石": 20, "粘土": 15},
    "サファイアの浄水塔": {"サファイア": 5, "水": 50, "ガラス": 10},
    "エメラルドの庭園": {"エメラルド": 5, "草": 30, "木材": 20},
    "アメジストの観測所": {"アメジスト": 8, "水晶": 15, "銅鉱石": 20},
    "ダイヤモンドの要塞": {"ダイヤモンド": 10, "チタン鉱石": 20, "鉄鉱石": 30},
    "多色宝石の宮殿": {"ルビー": 10, "サファイア": 10, "エメラルド": 10}
}
SCORING = {
    "水堀": {"強度": 5, "攻撃": 0, "美": 5},
    "石の監視棟": {"強度": 20, "攻撃": 5, "美": 5},
    "石の弓兵": {"強度": 5, "攻撃": 10, "美": 0},
    "銅の監視棟": {"強度": 30, "攻撃": 15, "美": 5},
    "銅の弓兵": {"強度": 30, "攻撃": 20, "美": 0},
    "鉄の監視棟": {"強度": 40, "攻撃": 20, "美": 10},
    "火薬庫": {"強度": 40, "攻撃": 20, "美": 10},
    "鉄の砲兵": {"強度":40, "攻撃": 50, "美": 0},
    "鉄の銃兵": {"強度": 40, "攻撃": 40, "美": 0},
    "銀の装飾棟": {"強度": 50, "攻撃": 15, "美": 50},
    "金の装飾棟": {"強度": 60, "攻撃": 15, "美": 60},
    "ガラスの装飾棟": {"強度": 5, "攻撃": 5, "美": 80},
    "水晶の塔": {"強度": 5, "攻撃": 60, "美": 90},
    "プラスチックの防衛棟": {"強度": 30, "攻撃": 70, "美": 70},
    "未来の防衛棟": {"強度": 70, "攻撃": 80, "美": 50},
    
    "重装甲バリケード": {"強度": 50, "攻撃": 50, "美": 40},
    "対空砲台": {"強度": 60, "攻撃": 60, "美": 50},
    "未来のレーザー塔": {"強度": 80, "攻撃": 90, "美": 70},
    "高性能精錬所": {"強度": 40, "攻撃": 20, "美": 50},
    "クリスタル温室": {"強度": 30, "攻撃": 0, "美": 70},
    "記念碑": {"強度": 30, "攻撃": 0, "美": 70},

    "ルビーの装甲壁": {"強度": 50, "攻撃": 30, "美": 50},
    "サファイアの監視塔": {"強度": 50, "攻撃": 50, "美": 50},
    "エメラルド精錬所": {"強度": 50, "攻撃": 40, "美": 60},
    "アメジスト魔導塔": {"強度": 50, "攻撃": 70, "美": 60},
    "ダイヤモンドの記念碑": {"強度": 100, "攻撃": 0, "美": 80},

    "ルビーの溶岩 forge": {"強度": 80, "攻撃": 0, "美": 50},
    "サファイアの浄水塔": {"強度": 70, "攻撃": 0, "美": 80},
    "エメラルドの庭園": {"強度": 50, "攻撃": 0, "美": 90},
    "アメジストの観測所": {"強度": 50, "攻撃": 90, "美": 90},
    "ダイヤモンドの要塞": {"強度": 100, "攻撃": 100, "美": 100},
    "多色宝石の宮殿": {"強度": 50, "攻撃": 0, "美": 100}
}

def calculate_score():
    total = {"強度": 0, "攻撃": 0, "美": 0}
    for b_name in st.session_state.map_data.values():
        if b_name in SCORING:
            for key in total:
                total[key] += SCORING[b_name].get(key, 0)
    return total
# --- 関数 ---
def build_structure(name):
    for mat, amount in RECIPES[name].items():
        if st.session_state.inventory[mat] < amount:
            st.error(f"{mat}が足りません！")
            return
    for mat, amount in RECIPES[name].items():
        st.session_state.inventory[mat] -= amount
    st.session_state.buildings.append(name)
    st.success(f"{name}を建設しました！")
def check_goals():
    goals = {
    "鉄壁の要塞 (強度500以上)": calculate_score()["強度"] >= 500,
    "軍事拠点 (攻撃力300以上)": calculate_score()["攻撃"] >= 300,
    # --- 芸術特化型：美しさを重視 ---
    "黄金の宮殿 (美しさ400以上)": calculate_score()["美"] >= 400,
    # --- バランス型：すべてを平均的に高める ---
    "調和の取れた城 (強度・攻撃・美 各200以上)": 
        all(score >= 200 for score in calculate_score().values()),
    # --- コンプリート目標 ---
    "究極の城 (総合スコア1500以上)": sum(calculate_score().values()) >= 1500
}
    return goals

# --- 2. 材料自動加算ロジック (UI表示の前に実行) ---
def update_resources():
    now = time.time()
    elapsed = now - st.session_state.last_update
    # 10秒ごとに1つ生産すると仮定
    for mat, count in st.session_state.drills.items():
        if count > 0:
            st.session_state.inventory[mat] += count * (elapsed // 2)
    st.session_state.last_update = now


def build_drill(mat):
    cost = 50 # 掘削機のコスト
    if st.session_state.inventory.get('鉄鉱石', 0) >= cost:
        st.session_state.inventory['鉄鉱石'] -= cost
        st.session_state.drills[mat] += 1
        st.success(f"{mat}用掘削機を建設しました！")
    else:
        st.error("鉄鉱石が50必要です！")


# --- UI ---
st.title("🏰 城建設クラフト")
tab1, tab2, tab3 = st.tabs(["⛏️ 採掘", "🔨 建築", "🏰 配置"])

with tab1:
    st.subheader("採掘")
    cols = st.columns(3)
    for i, mat in enumerate(st.session_state.inventory.keys()):
        if cols[i % 3].button(mat):
            update_resources()
            st.session_state.inventory[mat] += 1
            st.rerun()

with tab2:
    st.subheader("建築物をクラフト")
    
    # レシピを列ごとに分割して表示
    cols = st.columns(3) # 3列で表示
    for i, (b_name, recipe) in enumerate(RECIPES.items()):
        # 材料の表示用文字列を作成
        recipe_str = ", ".join([f"{mat}: {amount}" for mat, amount in recipe.items()])
        
        # 3列のどこに配置するかを i % 3 で決定
        if cols[i % 3].button(f"{b_name}\n({recipe_str})"):
            update_resources()
            build_structure(b_name)
            st.rerun()

    st.divider() # 区切り線
    st.subheader("掘削機をクラフト")
    # 掘削機の選択と作成ボタンも同様にコンパクトに配置可能
    target_mat = st.selectbox("掘削する材料を選択:", list(st.session_state.inventory.keys()))
    if st.button(f"{target_mat}用掘削機を作る (コスト: 鉄鉱石50)"):
        update_resources()
        build_drill(target_mat)
        st.rerun()

with tab3:
    st.subheader("城を設計する")
    # 全配置リセットボタン
    # 配置タブ内：リセットボタンの処理を修正
    if st.button("🏰 マップをリセット"):
        # 配置済みの全ての建築物を取得してリストに戻す
        for building_name in st.session_state.map_data.values():
            st.session_state.buildings.append(building_name)
        
        # マップデータをクリア
        st.session_state.map_data = {}
        st.success("配置をリセットし、建築物をリストに戻しました！")
        st.rerun()

    
    if not st.session_state.buildings and not st.session_state.map_data:
        st.info("建築物を作るとここに表示されます")
    else:
        selected = st.selectbox("配置する建築物:", st.session_state.buildings)

        # 枠で囲ってパネル化
    with st.container(border=True):
        for y in range(5):
            cols = st.columns(5)
            for x in range(5):
                pos = (x, y)
                building_name = st.session_state.map_data.get(pos, None)
                img_path = os.path.join(IMAGE_DIR, f"{building_name}.png")
                
                if building_name and os.path.exists(img_path):
                    # 画像にキャプションを追加して情報量を増やす
                    cols[x].image(img_path, width=200)
                else:
                    # 空地ボタンの見た目を少し強調
                    if cols[x].button("＋", key=f"btn_{x}_{y}"):
                        update_resources()
                        st.session_state.map_data[pos] = selected
                        st.session_state.buildings.remove(selected)
                        st.rerun()
        
    st.divider()
    st.subheader("🏰 城の評価")
    
    # 全てのマス（25マス）が埋まっているかチェック
    if len(st.session_state.map_data) == 25:
        score = calculate_score()
        st.success("城が完成しました！採点結果です：")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("強度", score["強度"])
        col2.metric("攻撃力", score["攻撃"])
        col3.metric("美しさ", score["美"])
        
        # 総合評価
        total_score = sum(score.values())
        st.write(f"### 総合スコア: {total_score}")
    else:
        st.info(f"城の採点を受けるには、すべてのマスに建築物を配置してください ({len(st.session_state.map_data)}/25)")
# --- ステータス表示（追加部分） ---
with st.sidebar:
    st.header("📊 ダッシュボード")
    
    # 目標状況をサイドバーに移動
    st.subheader("🎯 現在の目標")
    goals = check_goals()
    for goal, is_done in goals.items():
        color = "green" if is_done else "gray"
        st.markdown(f":{color}[{'✅' if is_done else '⬜'} {goal}]")
        
    st.divider()
    # 所持材料の表示
    st.subheader("🎒 所持材料")
    # DataFrameを使って表形式で表示
    df_inventory = pd.DataFrame.from_dict(st.session_state.inventory, orient='index', columns=['数量'])
    st.table(df_inventory)
    
    # 建築済み（配置前）の建築物リスト
    st.subheader("🏗️ 未配置の建築物")
    if st.session_state.buildings:
        st.write(", ".join(st.session_state.buildings))
    else:
        st.write("なし")

    
