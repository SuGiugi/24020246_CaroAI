# Caro AI

Ứng dụng chơi cờ Caro với trí tuệ nhân tạo

---

## Cài đặt

**Bước 1 — Tải source code**

```bash
git clone https://github.com/your-repo/caro-ai.git
cd caro-ai
```

**Bước 2 — Cài thư viện kiểm thử** *(chỉ cần nếu muốn chạy test)*

```bash
pip install pytest
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
caro-ai/
├── main_gui.py              # Điểm khởi chạy chương trình
├── gui.py                   # Giao diện đồ họa Tkinter
├── benchmark_weights.py     # Công cụ đánh giá trọng số AI
├── pytest.ini               # Cấu hình pytest
├── caro_ai/
│   ├── logic.py             # Logic game (bàn cờ, thắng/thua/hòa)
│   └── ai/
│       └── minimax_lv2.py   # AI agent (Minimax + Alpha-Beta)
└── tests/
    ├── test_logic.py        # 44 test cases cho logic game
    └── test_minimax_lv2.py  # 41 test cases cho AI agent
```
