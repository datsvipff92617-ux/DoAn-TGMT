import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ================= CẤU HÌNH GIAO DIỆN =================
st.set_page_config(
    page_title="Báo cáo Kết quả Giám sát",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS để làm đẹp
st.markdown("""
    <style>
    .reportview-container {
        background: #1e1e1e;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        background: -webkit-linear-gradient(45deg, #FF4B2B, #FF416C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 30px;
    }
    .metric-card {
        background: #2b2b2b;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF416C;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .insight-box {
        background: rgba(255, 65, 108, 0.1);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(255, 65, 108, 0.3);
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📊 BÁO CÁO KẾT QUẢ GIÁM SÁT GIAO THÔNG (SHOWCASE)</div>', unsafe_allow_html=True)
st.markdown("---")

# ================= DỮ LIỆU ĐỘNG TỪ TRANG CHỦ =================
if 'counts' not in st.session_state or sum(st.session_state.counts.values()) == 0:
    st.warning("⚠️ Chưa có dữ liệu phân tích! Vui lòng quay lại trang 'App' (Trang chủ) và nhấn BẮT ĐẦU CHẠY để hệ thống đếm xe, sau đó quay lại đây để xem báo cáo.")
    st.stop()

counts = st.session_state.counts

DATA = {
    "Loại xe": ["Motorbike", "Car", "Truck", "Bus"],
    "Số lượng": [counts.get("motorbike", 0), counts.get("car", 0), counts.get("truck", 0), counts.get("bus", 0)],
    "Màu sắc": ["#00d2ff", "#3a7bd5", "#f953c6", "#ff9966"]
}
df = pd.DataFrame(DATA)
total_vehicles = df["Số lượng"].sum()

if total_vehicles == 0:
    st.warning("⚠️ Không phát hiện phương tiện nào trong video.")
    st.stop()

# ================= BỐ CỤC GIAO DIỆN =================
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("🎥 Băng Hình Phân Tích (Replay)")
    st.markdown("Đoạn băng ghi hình Demo minh họa quá trình AI bám sát và đếm lưu lượng phương tiện.")
    
    # Load video đã nén
    base_dir = os.path.dirname(os.path.dirname(__file__))
    video_path = os.path.join(base_dir, "data", "showcase_h264.mp4")
    
    if os.path.exists(video_path):
        st.video(video_path, format="video/mp4")
    else:
        st.warning("Đang chờ tải video phân tích (file data/showcase_h264.mp4)...")
        
    # Tính toán Insights tự động
    motorbike_pct = counts.get("motorbike", 0) / total_vehicles * 100 if total_vehicles > 0 else 0
    
    st.markdown(f"""
        <div class="insight-box">
            <h4>💡 AI Insights (Phân tích tự động):</h4>
            <ul>
                <li><b>Cảnh báo mật độ:</b> Lưu lượng xe máy chiếm đến {motorbike_pct:.1f}% tổng phương tiện, cho thấy đặc thù rõ nét của giao thông đô thị nội khu.</li>
                <li><b>Cập nhật Real-time:</b> Hệ thống vừa ghi nhận tổng cộng <b>{total_vehicles}</b> phương tiện trong phiên làm việc hiện tại của bạn.</li>
                <li><b>Độ chính xác:</b> Hệ thống YOLOv8n kết hợp thuật toán ByteTrack duy trì khả năng bám vết (tracking) liên tục trong điều kiện ánh sáng thực tế.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.subheader("📈 Tổng Quan Lưu Lượng")
    
    # 4 Ô Metrics
    m1, m2 = st.columns(2)
    m3, m4 = st.columns(2)
    
    m1.metric("🏍️ Xe Máy (Motorbike)", f'{counts.get("motorbike", 0)}', f'{counts.get("motorbike", 0)/total_vehicles*100:.1f}%')
    m2.metric("🚗 Ô tô (Car)", f'{counts.get("car", 0)}', f'{counts.get("car", 0)/total_vehicles*100:.1f}%')
    m3.metric("🚚 Xe Tải (Truck)", f'{counts.get("truck", 0)}', f'{counts.get("truck", 0)/total_vehicles*100:.1f}%')
    m4.metric("🚌 Xe Buýt (Bus)", f'{counts.get("bus", 0)}', f'{counts.get("bus", 0)/total_vehicles*100:.1f}%')
    
    st.markdown("---")
    
    # Biểu đồ tròn
    st.subheader("Phân bổ Phương tiện")
    fig_pie = px.pie(
        df, 
        values='Số lượng', 
        names='Loại xe', 
        hole=0.4,
        color='Loại xe',
        color_discrete_sequence=df["Màu sắc"]
    )
    fig_pie.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="white",
        margin=dict(t=0, b=0, l=0, r=0)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Biểu đồ cột
    st.subheader("Thống kê Chi tiết")
    fig_bar = px.bar(
        df, 
        x='Loại xe', 
        y='Số lượng',
        color='Loại xe',
        text='Số lượng',
        color_discrete_sequence=df["Màu sắc"]
    )
    fig_bar.update_traces(textposition='outside')
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="white",
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.success("✅ Dữ liệu đang được đồng bộ trực tiếp từ kết quả phân tích AI.")
