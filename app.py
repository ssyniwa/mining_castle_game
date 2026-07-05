import streamlit as st
import pandas as pd

# ページ設定（スマホ対応）
st.set_page_config(page_title="城建設ゲーム", layout="centered")

# 初期化：セッション状態にデータを保存
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        '水': 0, '草': 0, '木材': 0, '石材': 0, 
        '銅鉱石': 0, '鉄鉱石': 0, '銀鉱石': 0, '金鉱石': 0, 'チタン鉱石': 0
    }

st.title("🏰 城建設クラフト")

# 1. 採掘エリア
st.subheader("⛏️ 採掘")
# 2列で表示（スマホ対応）
cols = st.columns(3)
materials = list(st.session_state.inventory.keys())

for i, mat in enumerate(materials):
    if cols[i % 3].button(mat):
        st.session_state.inventory[mat] += 1
        st.rerun()

# 2. インベントリ表示
st.subheader("🎒 所持材料")
df = pd.DataFrame.from_dict(st.session_state.inventory, orient='index', columns=['数量'])
st.table(df)
