# Caro AI

Ứng dụng chơi cờ Caro với trí tuệ nhân tạo

---

## Cài đặt

**Bước 1 — Tải source code**

```bash
git clone https://github.com/your-repo/caro-ai.git
cd caro-ai
```

**Bước 2 — Cài thư viện cần thêm** *(chỉ cần nếu muốn chạy test)*

```bash
pip install -r requirements.txt
```

---

## Chạy chương trình

```bash
python main_gui.py
```

Giao diện đồ họa sẽ mở ra. Người chơi đóng vai **X** và đi trước, AI đóng vai **O**.

---

## Chạy kiểm thử

**Chạy toàn bộ test cases:**

```bash
python -m pytest tests/ -v
```

**Chạy riêng từng module:**

```bash
# Test logic game
python -m pytest tests/test_logic.py -v

# Test AI agent
python -m pytest tests/test_minimax_lv2.py -v
```

## Hướng Dẫn Thay Đổi Cấu Hình Thuật Toán

Mặc định chương trình được thiết lập cấu hình Độ sâu tìm kiếm (Depth) = 3.
Nếu muốn thử thách AI ở độ khó cao hơn (Depth = 4) hoặc muốn máy chạy nhanh hơn (Depth = 2), có thể chỉnh sửa trực tiếp trong file mã nguồn.

1. Mở file main_gui.py bằng bất kỳ Text Editor nào (VSCode, Notepad,...).
2. Tìm đến dòng số 6: ai = agent(depth=3)
3. Thay đổi tham số depth thành con số bạn muốn. Ví dụ:

```bash
# Đổi độ sâu tính toán thành 2
ai = agent(depth=2)
```

4. Lưu file và chạy lại chương trình (python main_gui.py).
 
---

## Cấu trúc thư mục

```
24020279_24020246_23020595_CaroAI/
├── main_gui.py              
├── gui.py                                
├── caro_ai/
│   ├── logic.py             
│   └── ai/
│       └── minimax_lv2.py   
└── tests/
    ├── test_logic.py        
    └── test_minimax_lv2.py
    └── __init__.py
```
