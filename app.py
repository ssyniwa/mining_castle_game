import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="城建設クラフト", layout="centered")

# --- 初期化 ---
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        '水': 0, '草': 0, '木材': 0, '石材': 0, 
        '銅鉱石': 0, '鉄鉱石': 0, '銀鉱石': 0, '金鉱石': 0, 'チタン鉱石': 0
    }
if 'buildings' not in st.session_state:
    st.session_state.buildings = []

# レシピ定義（必要な材料と数量）
RECIPES = {
    "水堀": {"水": 5},
    "草の壁": {"草": 5},
    "木の壁": {"木材": 5},
    "石の壁": {"石材": 5},
    "石の監視棟": {"石材": 10},
    "銅の監視棟": {"銅鉱石": 10},
    "鉄の監視棟": {"鉄鉱石": 10},
    "鉄の砲兵": {"鉄鉱石": 20},
    "未来の防衛棟": {"チタン鉱石": 50}
}

# --- 関数 ---
def build_structure(name):
    recipe = RECIPES[name]
    # 材料チェック
    for mat, amount in recipe.items():
        if st.session_state.inventory[mat] < amount:
            st.error(f"{mat}が足りません！")
            return
    # 材料消費
    for mat, amount in recipe.items():
        st.session_state.inventory[mat] -= amount
    st.session_state.buildings.append(name)
    st.success(f"{name}を建設しました！")

# --- UI ---
st.title("🏰 城建設クラフト")

# タブで採掘と建築を切り替え
tab1, tab2 = st.tabs(["採掘", "建築"])

with tab1:
    st.subheader("採掘")
    cols = st.columns(3)
    for i, mat in enumerate(st.session_state.inventory.keys()):
        if cols[i % 3].button(mat):
            st.session_state.inventory[mat] += 1
            st.rerun()

with tab2:
    st.subheader("建築")
    for b_name in RECIPES.keys():
        if st.button(f"{b_name} を作る"):
            build_structure(b_name)
            st.rerun()

# ステータス表示
st.divider()
st.subheader("現在の所持品")
st.write(st.session_state.inventory)

st.subheader("建築済みの施設")
st.write(st.session_state.buildings)
