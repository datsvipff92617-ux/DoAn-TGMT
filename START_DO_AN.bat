@echo off
chcp 65001 >nul
title HỆ THỐNG GIÁM SÁT GIAO THÔNG THÔNG MINH (ITS) - ĐỒ ÁN

echo =========================================================
echo    KHOI DONG HE THONG GIAM SAT GIAO THONG THONG MINH
echo =========================================================
echo.

:: Kiem tra xem Python da duoc cai dat chua
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [LOI] Khong tim thay Python tren he thong. Vui long cai dat Python 3.8+ de chay do an.
    pause
    exit /b
)

echo [1/3] Kiem tra va cai dat thu vien (Dependencies)...
pip install -r requirements.txt -q

echo.
echo [2/3] Dang khoi dong may chu AI Streamlit...
echo Vui long doi trong giay lat, trinh duyet web se tu dong mo len...
echo.
echo [3/3] De tat he thong, hay tat cua so nay.
echo =========================================================

:: Chay ung dung
python -m streamlit run app.py

pause
