# 🛠️ IT Support Tool Suite

<div align="center">

> **Bộ công cụ Desktop chuyên nghiệp dành cho Kỹ thuật viên IT và System Administrator**  
> *Tối ưu hóa quy trình triển khai, cấu hình, sao lưu và bảo trì máy tính Windows.*

[![Version](https://img.shields.io/badge/version-v1.2.5-blue.svg?style=for-the-badge)](VERSION)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011%20(64--bit)-0078D6.svg?style=for-the-badge&logo=windows)](https://microsoft.com)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Security](https://img.shields.io/badge/encryption-AES--256--GCM-green.svg?style=for-the-badge)](docs/SECURITY.md)

</div>

---

## 📌 Giới thiệu

**IT Support Tool Suite** là bộ công cụ desktop toàn diện giúp kỹ thuật viên IT đơn giản hóa và tự động hóa các thao tác quản trị hệ thống hàng ngày trên môi trường Windows. Thay vì thao tác thủ công qua nhiều công cụ rời rạc, ứng dụng hợp nhất toàn bộ tính năng cần thiết vào một giao diện trực quan, mượt mà và an toàn.

Được thiết kế dựa trên nguyên tắc **đặc quyền tối thiểu (Least Privilege)**, ứng dụng vận hành ở quyền người dùng thông thường và chỉ nâng cấp UAC đối với các tác vụ quản trị chuyên biệt.

---

## 🚀 Điểm nổi bật

- 🇻🇳 **Giao diện hiện đại:** Hỗ trợ hoàn toàn Tiếng Việt, tương thích mượt mà với Dark Mode & Light Mode.
- 🔐 **Bảo mật cao:** Mã hóa dữ liệu sao lưu bằng thuật toán chuẩn quân đội **AES-256-GCM**.
- 🛡️ **An toàn hệ thống:** Kiểm tra dung lượng trống, chặn Path Traversal và ngăn nguy cơ tự sao chép lặp vô tận.
- ⚡ **Hiệu năng tối ưu:** Xử lý tác vụ nặng dưới dạng tiến trình nền (Async Worker Threads), giao diện không bị treo đơ.
- 🎯 **UAC Thông minh:** Chỉ yêu cầu quyền Administrator đúng lúc khi cấu hình mạng hoặc cài driver/máy in.
- 📦 **Chạy độc lập:** Cung cấp bản EXE Portable hoàn chỉnh, không yêu cầu cài đặt môi trường Python.

---

## 📋 Mục lục

- [Điểm nổi bật](#-điểm-nổi-bật)
- [Tính năng chi tiết](#-tính-năng-chi-tiết)
  - [Sao lưu & Khôi phục](#1-sao-lưu--khôi-phục-backup--restore)
  - [Tra cứu & Cấu hình Mạng](#2-tra-cứu--cấu-hình-mạng-network-management)
  - [Cài đặt Máy in Nước / Mạng](#3-cài-đặt-máy-in-mạng-network-printer-setup)
  - [Triển khai Phần mềm](#4-triển-khai-phần-mềm-winget-package-manager)
  - [Gỡ ứng dụng & Dọn dẹp](#5-gỡ-ứng-dụng--dọn-dẹp-tàn-dư-uninstaller)
- [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
- [Hướng dẫn sử dụng](#-hướng-dẫn-sử-dụng)
  - [Chạy bản EXE Portable](#chạy-bản-exe-portable)
  - [Chạy từ Mã nguồn (Source Code)](#chạy-từ-mã-nguồn-source-code)
- [Phát triển & Đóng gói Release](#-phát-triển--đóng-gói-release)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
- [Khắc phục sự cố](#-khắc-phục-sự-cố)
- [Bảo mật & Quyền riêng tư](#-bảo-mật--quyền-riêng-tư)
- [Giấy phép & Bản quyền](#-giấy-phép--bản-quyền)

---

## ⚡ Tính năng chi tiết

### 1. 💾 Sao lưu & Khôi phục (Backup & Restore)
*Giúp chuyển đổi máy tính hoặc sao lưu định kỳ cho người dùng nhanh chóng, an toàn.*
- **Phạm vi sao lưu:** Thư mục cá nhân (`Desktop`, `Documents`, `Downloads`), hồ sơ trình duyệt Chrome (`Profile`), và dữ liệu mail Outlook (`.pst` / `.ost`).
- **Sao lưu Driver:** Tự động quét, đóng gói và khôi phục toàn bộ Driver thiết bị trên hệ thống Windows.
- **Đóng gói & Mã hóa:** Xuất định dạng file nén `.zip` tiêu chuẩn hoặc định dạng mã hóa an toàn `.itsbackup` (AES-256-GCM).
- **Cơ chế an toàn:** Tự động kiểm tra dung lượng ổ đĩa khả dụng, xác minh tính toàn vẹn SHA-256 trước khi xuất và chặn triệt để lỗ hổng ZIP đè đường dẫn không an toàn.

> [!IMPORTANT]
> Hãy đóng hoàn toàn Google Chrome và Microsoft Outlook trước khi tiến hành sao lưu hoặc khôi phục. Dữ liệu tài khoản mã hóa theo máy của Chrome có thể yêu cầu đăng nhập lại trên thiết bị mới.

---

### 2. 🌐 Tra cứu & Cấu hình Mạng (Network Management)
*Quản lý và chẩn đoán kết nối mạng LAN tập trung.*
- **Thông tin Card mạng:** Hiển thị chi tiết IPv4, Subnet Mask, Default Gateway và trạng thái kết nối.
- **Quét mạng LAN hàng loạt:** Cho phép quét song song tối đa **4.096 địa chỉ IPv4** trong từng Subnet `/20` - `/24`.
- **Nhận diện thiết bị:** Tra cứu chính xác trạng thái Online/Offline, MAC Address và Hostname thiết bị trong mạng.
- **Cấu hình IP linh hoạt:** Chuyển đổi nhanh giữa chế độ **DHCP** và **IP Tĩnh (Static IP)** kèm DNS tuỳ chỉnh.
- **Xuất báo cáo:** Hỗ trợ xuất danh sách thiết bị quét ra file `.csv` chuẩn UTF-8.
- **Trải nghiệm chạy ẩn:** Thực thi lệnh `netsh` và `arp` ở chế độ ẩn, không bật cửa sổ CMD gây phiền người dùng.

---

### 3. 🖨️ Cài đặt Máy in Mạng (Network Printer Setup)
*Tự động hóa kết nối máy in văn phòng qua cổng IP.*
- **Dò tìm tự động:** Quét thiết bị lắng nghe trên cổng RAW TCP `9100`.
- **Nhận diện Model:** Trích xuất tên model chi tiết thông qua giao thức PJL (Printer Job Language).
- **Tạo Cổng & Hàng đợi:** Tự động khởi tạo Standard TCP/IP Port và cài đặt hàng đợi máy in.
- **Tương thích Driver đa dạng:** Sử dụng Microsoft IPP Class Driver có sẵn hoặc nạp file `.inf` tùy chỉnh.
- **Tối ưu UAC:** Gom tất cả thao tác đòi hỏi quyền System/Admin vào duy nhất 1 lần xác nhận UAC.

---

### 4. 📦 Triển khai Phần mềm (Winget Package Manager)
*Cài đặt nhanh các công cụ cơ bản cho máy mới bàn giao.*
Tự động kiểm tra và nâng cấp/cài đặt các ứng dụng phổ biến thông qua **Windows Package Manager (`winget`)**:

| Nhóm phần mềm | Ứng dụng hỗ trợ |
| :--- | :--- |
| **Tiện ích hệ thống** | `7-Zip`, `WinRAR`, `UniKey`, `UltraViewer` |
| **Giao tiếp & Trình duyệt**| `Google Chrome`, `Zalo`, `VLC Media Player` |
| **Văn phòng & Tài liệu** | `Foxit PDF Reader`, `LibreOffice`, `Notepad++` |
| **Chẩn đoán & Công cụ IT**| `PowerToys`, `Everything`, `CrystalDiskInfo`, `CPU-Z`, `HWiNFO` |

> [!TIP]
> Ứng dụng sẽ tự động kiểm tra phần mềm đã tồn tại trên máy để bỏ qua, tránh việc cài đè hoặc tốn tài nguyên mạng.

---

### 5. 🧹 Gỡ ứng dụng & Dọn dẹp tàn dư (Uninstaller)
*Gỡ sạch triệt để các phần mềm rác hoặc lỗi thời.*
- **Quét toàn diện:** Tra cứu Registry của cả 32-bit và 64-bit (User scope & Machine scope).
- **Bộ lọc tìm kiếm:** Tìm nhanh ứng dụng theo Tên, Phiên bản hoặc Nhà phát hành (Publisher).
- **Chuẩn hóa lệnh MSI:** Tự động khắc phục lệnh gỡ lỗi của installer MSI (chuyển từ Repair/Modify sang Uninstall).
- **Dọn dẹp tàn dư (Deep Clean):** Quét và xóa sạch tập tin dư thừa trong `Program Files`, `AppData`, `Temp` và Registry keys liên quan.
- **Xác nhận an toàn:** Hiển thị chi tiết các mục tàn dư và yêu cầu người dùng xác nhận trước khi thực hiện xóa.

---

## 🖥️ Yêu cầu hệ thống

| Thành phần | Yêu cầu tối thiểu |
| :--- | :--- |
| **Hệ điều hành** | Windows 10 hoặc Windows 11 (64-bit) |
| **Môi trường Python** *(chạy source)* | Python `3.10` đến `< 3.15` |
| **Quyền truy cập** | Account có quyền Administrator (cho thao tác UAC) |
| **Công cụ đi kèm** | Windows Package Manager (`winget`) cho tab Cài phần mềm |
| **Kết nối mạng** | Cần Internet để tải phần mềm qua `winget` |

> [!NOTE]
> Nếu hệ thống chưa có `winget`, vui lòng cập nhật **App Installer** từ [Microsoft Store](https://apps.microsoft.com/store/detail/9NBLGGH4NNS1).

---

## 🛠️ Hướng dẫn sử dụng

### Chạy bản EXE Portable

1. **Tải bản đóng gói phát hành sẵn:**  
   👉 **[📥 Tải về ITSupportToolSuite-v1.2.5.exe](https://github.com/HoangGia73/HelpdeskApp/releases/download/v1.2.5/ITSupportToolSuite-v1.2.5.exe)** (Bản Portable)  
   *(Hoặc xem danh sách tất cả bản phát hành tại [GitHub Releases](https://github.com/HoangGia73/HelpdeskApp/releases))*

2. Nhấp đúp chuột để chạy trực tiếp. **Không cần chọn "Run as Administrator"** (Ứng dụng sẽ tự nâng quyền UAC khi thực sự cần).
3. Kiểm tra mã SHA-256 để đảm bảo tính toàn vẹn:
   ```powershell
   Get-FileHash -Algorithm SHA256 .\dist\ITSupportToolSuite-v1.2.5.exe
   ```
   *(Đối chiếu kết quả với file [`dist/SHA256SUMS-v1.2.5.txt`](https://github.com/HoangGia73/HelpdeskApp/releases/download/v1.2.5/SHA256SUMS-v1.2.5.txt))*

---

### Chạy từ Mã nguồn (Source Code)

Mở PowerShell tại thư mục dự án và thực hiện các bước:

```powershell
# 1. Tạo và kích hoạt môi trường ảo Python
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Cập nhật pip & cài đặt gói phụ thuộc
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .

# 3. Khởi chạy ứng dụng
python -m it_support_suite
```

*Nếu gặp lỗi PowerShell chặn script kích hoạt môi trường ảo, hãy chạy:*
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

---

## 👨‍💻 Phát triển & Đóng gói Release

### Môi trường Phát triển (Development)

Cài đặt thư viện hỗ trợ kiểm thử và phát triển:
```powershell
python -m pip install -r requirements-dev.txt
python -m pip install -e .
```

Khởi chạy bộ kiểm thử tự động (Unit test suite):
```powershell
python -m pytest
```

### Đóng gói Phiên bản Release

Để tạo bản EXE độc lập đi kèm mã băm SHA-256 checksum:
```powershell
.\scripts\release.ps1 -Version 1.2.4
```
*Script sẽ tự động chạy test suite, đóng gói PyInstaller và lưu kết quả vào thư mục `dist/`.*

---

## 📁 Cấu trúc dự án

```text
toolhelpdesk/
├── 📁 src/it_support_suite/       # Mã nguồn chính của ứng dụng
│   ├── 📄 __main__.py             # Điểm khởi chạy ứng dụng (Entry point)
│   ├── 📄 gui.py                  # Giao diện người dùng CustomTkinter chính
│   ├── 📄 backup_*.py             # Mô-đun Sao lưu, Khôi phục & Mã hóa AES
│   ├── 📄 network_*.py            # Mô-đun Quét IP, MAC & Cấu hình Mạng
│   ├── 📄 printer_*.py            # Mô-đun Dò tìm & Cài đặt Máy in
│   ├── 📄 software_*.py           # Mô-đun Triển khai ứng dụng qua Winget
│   └── 📄 uninstaller_*.py        # Mô-đun Gỡ ứng dụng & Dọn dẹp tàn dư
├── 📁 tests/                      # Bộ kiểm thử tự động (Pytest)
├── 📁 scripts/                    # Scripts tự động hóa build & release (release.ps1)
├── 📁 packaging/                  # Cấu hình PyInstaller & Installer spec
├── 📁 docs/                       # Tài liệu Bảo mật, Privacy, Support & EULA
├── 📄 requirements.txt            # Thư viện Runtime phụ thuộc
├── 📄 requirements-dev.txt        # Thư viện Development phụ thuộc
└── 📄 pyproject.toml              # Cấu hình package Python
```

---

## ❓ Khắc phục sự cố (Troubleshooting)

<details>
<summary><b>1. Tab Gỡ cài đặt không hiển thị danh sách ứng dụng?</b></summary>

- Đảm bảo bạn đã tắt hoàn toàn phiên bản ứng dụng cũ trước khi mở bản EXE mới.
- Bấm nút **Làm mới** và xóa mọi ký tự tìm kiếm trong ô tìm kiếm.
- Kiểm tra file log tại: `%LOCALAPPDATA%\ITSupportToolSuite\logs\application.log`.
</details>

<details>
<summary><b>2. Không thể cài đặt phần mềm qua Tab Cài phần mềm?</b></summary>

Kiểm tra trạng thái của `winget` bằng PowerShell:
```powershell
winget --version
winget source update
```
Nếu nhận báo lỗi không tìm thấy `winget`, bạn cần cập nhật ứng dụng **App Installer** trên máy.
</details>

<details>
<summary><b>3. Thao tác đổi IP tĩnh hoặc Cài máy in bị thất bại?</b></summary>

- Đảm bảo bạn đã bấm **Yes / Đồng ý** trên cửa thoại UAC nâng quyền.
- Kiểm tra phần mềm bảo mật doanh nghiệp (Antivirus/EDR) có đang chặn PowerShell, `PnPUtil`, `DISM` hoặc dịch vụ `Print Spooler` hay không.
</details>

<details>
<summary><b>4. Quá trình sao lưu bỏ qua file Google Chrome hoặc Outlook?</b></summary>

- Hãy chắc chắn đã kết thúc hoàn toàn tiến trình `chrome.exe` hoặc `outlook.exe` trong Task Manager trước khi sao lưu.
</details>

---

## 🔒 Bảo mật & Dữ liệu

- 🔑 **Mật khẩu mã hóa:** Mật khẩu sao lưu yêu cầu độ dài tối thiểu **12 ký tự**. Mật khẩu này không được lưu trữ ở bất kỳ đâu và **không thể khôi phục** nếu bị quên.
- 🛡️ **Nguyên tắc bảo mật:** Không đính kèm dữ liệu sao lưu, mật khẩu, Chrome profile hoặc file mailbox Outlook vào các yêu cầu hỗ trợ (Support tickets).
- 📜 **Định danh phát hành:** Các bản phát hành chính thức bắt buộc phải ký số **Authenticode** hợp lệ.

*Xem thêm tài liệu chi tiết:*  
[Security Policy](docs/SECURITY.md) · [Privacy Policy](docs/PRIVACY.md) · [Support Guide](docs/SUPPORT.md) · [EULA](docs/EULA.md) · [Releasing Guide](docs/RELEASING.md)

---

## 🧰 Công nghệ sử dụng

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Tkinter-CustomTkinter-blue?style=flat-square" />
  <img src="https://img.shields.io/badge/PowerShell-5391FE?style=flat-square&logo=powershell&logoColor=white" />
  <img src="https://img.shields.io/badge/Windows-Winget-0078D6?style=flat-square&logo=windows&logoColor=white" />
  <img src="https://img.shields.io/badge/Security-AES--256--GCM-success?style=flat-square" />
  <img src="https://img.shields.io/badge/PyInstaller-Packaging-orange?style=flat-square" />
</p>

---

## ⚖️ Giấy phép

Copyright © IT Support Tool Suite. All rights reserved.

Đây là phần mềm sở hữu độc quyền (**Proprietary Software**). Nghiêm cấm mọi hành vi sao chép, phân phối, sửa đổi hoặc sử dụng thương mại khi chưa được sự đồng ý bằng văn bản từ chủ sở hữu bản quyền.  
Chi tiết xem tại [LICENSE](LICENSE) và [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).