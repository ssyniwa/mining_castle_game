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
        '粘土': 0, '火薬': 0, 'ガラス': 0, 'レンガ': 0, '水晶': 0, 'プラスチック': 0
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
    "草の壁": {"草": 5},
    "木の壁": {"木材": 5},
    "松明": {"木材": 2, "草": 1}, # 追加：灯りとして周囲を照らす
    "草の櫓": {"木材": 10, "草": 5}, # 追加：高い位置からの防衛
    
    # 石材レベル
    "石の壁": {"石材": 5},
    "石の監視棟": {"石材": 10},
    "石弓兵": {"石材": 15, "木材": 5}, # 追加：防衛部隊
    
    # 金属レベル
    "銅の監視棟": {"銅鉱石": 10},
    "銅の弓兵": {"銅鉱石": 15, "木材": 5}, # 追加：防衛部隊
    "鉄の監視棟": {"鉄鉱石": 10},
    "鉄の弓兵": {"鉄鉱石": 15, "木材": 5}, # 追加：防衛部隊
    "鉄の槍兵": {"鉄鉱石": 15, "石材": 5}, # 追加：防衛部隊
    "鉄の砲兵": {"鉄鉱石": 30},
    "鉄の銃兵": {"鉄鉱石": 20},
    # 希少資源レベル
    "銀の装飾棟": {"銀鉱石": 20}, # 追加：城の豪華さを上げる
    "金の装飾棟": {"金鉱石": 20}, # 追加：城の豪華さを上げる
    "未来の防衛棟": {"チタン鉱石": 50},
    
    "粘土の壁": {"粘土": 5},
    "レンガの壁": {"レンガ": 5},
    "ガラスの装飾棟": {"ガラス": 10},
    "火薬庫": {"火薬": 10, "石材": 5},
    "水晶の塔": {"水晶": 20},
    "プラスチックの防衛棟": {"プラスチック": 20}
}

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
    # 第1段階：基盤づくり
    "木の壁を5つ配置": list(st.session_state.map_data.values()).count("木の壁") >= 5,
    "水堀を3つ配置": list(st.session_state.map_data.values()).count("水堀") >= 3,
    
    # 第2段階：石造りへの進化
    "石の壁を5つ配置": list(st.session_state.map_data.values()).count("石の壁") >= 5,
    "石の監視棟を2つ配置": list(st.session_state.map_data.values()).count("石の監視棟") >= 2,
    
    # 第3段階：金属防衛の導入
    "銅の監視棟を2つ配置": list(st.session_state.map_data.values()).count("銅の監視棟") >= 2,
    "鉄の監視棟を3つ配置": list(st.session_state.map_data.values()).count("鉄の監視棟") >= 3,
    "鉄の砲兵を1つ配置": "鉄の砲兵" in st.session_state.map_data.values(),
    
    # 第4段階：未来の城へ
    "未来の防衛棟を2つ配置": list(st.session_state.map_data.values()).count("未来の防衛棟") >= 2
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
    for b_name, recipe in RECIPES.items():
        # 材料の表示用文字列を作成 (例: "水堀 (水: 5)")
        recipe_str = ", ".join([f"{mat}: {amount}" for mat, amount in recipe.items()])
        
        # ボタンにレシピ情報を付与
        if st.button(f"{b_name} ({recipe_str})を作る"):
            update_resources()
            build_structure(b_name)
            st.rerun()
    st.subheader("掘削機をクラフト")
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
        
        # 5x5 グリッド
        for y in range(5):
            cols = st.columns(5)
            for x in range(5):
                pos = (x, y)
                building_name = st.session_state.map_data.get(pos, None)
                
                # 画像の表示ロジック
                img_path = os.path.join(IMAGE_DIR, f"{building_name}.png")
                if building_name and os.path.exists(img_path):
                    cols[x].image(img_path, width=200)
                else:
                    if cols[x].button("＋", key=f"btn_{x}_{y}"):
                        update_resources()
                        st.session_state.map_data[pos] = selected
                        st.session_state.buildings.remove(selected)
                        st.rerun()
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

    # マップ配置データの表示
    st.subheader("🏰 配置済みの施設")
    if st.session_state.map_data:
        st.write(st.session_state.map_data)
    else:
        st.write("まだ施設を配置していません")
