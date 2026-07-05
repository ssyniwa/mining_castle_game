import streamlit as st
import os

# --- 設定 ---
# プロジェクトフォルダ内に "images" というフォルダを作成し、
# 建築物名に対応する画像ファイル（例: 水堀.png）を格納してください。
IMAGE_DIR = "images"

st.set_page_config(page_title="城建設クラフト", layout="centered")

# --- セッション状態の初期化 ---
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        '水': 0, '草': 0, '木材': 0, '石材': 0, 
        '銅鉱石': 0, '鉄鉱石': 0, '銀鉱石': 0, '金鉱石': 0, 'チタン鉱石': 0
    }
if 'buildings' not in st.session_state:
    st.session_state.buildings = []
if 'map_data' not in st.session_state:
    st.session_state.map_data = {}

# レシピ定義
RECIPES = {
    "水堀": {"水": 5}, "草の壁": {"草": 5}, "木の壁": {"木材": 5},
    "石の壁": {"石材": 5}, "石の監視棟": {"石材": 10},
    "銅の監視棟": {"銅鉱石": 10}, "鉄の監視棟": {"鉄鉱石": 10},
    "鉄の砲兵": {"鉄鉱石": 20}, "未来の防衛棟": {"チタン鉱石": 50}
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

# --- UI ---
st.title("🏰 城建設クラフト")
tab1, tab2, tab3 = st.tabs(["⛏️ 採掘", "🔨 建築", "🏰 配置"])

with tab1:
    st.subheader("採掘")
    cols = st.columns(3)
    for i, mat in enumerate(st.session_state.inventory.keys()):
        if cols[i % 3].button(mat):
            st.session_state.inventory[mat] += 1
            st.rerun()

with tab2:
    st.subheader("建築物をクラフト")
    for b_name in RECIPES.keys():
        if st.button(f"{b_name} を作る"):
            build_structure(b_name)
            st.rerun()

with tab3:
    st.subheader("城を設計する")
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
                        st.session_state.map_data[pos] = selected
                        st.session_state.buildings.remove(selected)
                        st.rerun()
