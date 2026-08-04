# IT Support Tool Suite

> Bộ công cụ desktop dành cho kỹ thuật viên IT triển khai, cấu hình và bàn giao máy tính Windows nhanh hơn.

**Phiên bản:** `v1.2.3` · **Nền tảng:** Windows 10/11 64-bit · **Ngôn ngữ:** Python 3.10+

IT Support Tool Suite gom các tác vụ hỗ trợ thường gặp vào một giao diện duy nhất: sao lưu dữ liệu người dùng, quét mạng LAN, cấu hình IP, cài máy in mạng, cài phần mềm bằng `winget` và quản lý ứng dụng đã cài. Ứng dụng chạy với quyền người dùng thông thường và chỉ yêu cầu UAC khi một thao tác thực sự cần quyền quản trị.

## Điểm nổi bật

- Giao diện tiếng Việt, hỗ trợ chế độ sáng và tối.
- Không cần chạy toàn bộ ứng dụng bằng quyền Administrator.
- Các tác vụ dài chạy nền để hạn chế treo giao diện.
- Có bản EXE độc lập dành cho máy không cài Python.
- Hỗ trợ backup mã hóa bằng AES-256-GCM.
- Kiểm tra đường dẫn ZIP và thư mục xóa nhằm hạn chế thao tác không an toàn.

## Tính năng

### Sao lưu và khôi phục

- Sao lưu Desktop, Documents và Downloads.
- Sao lưu Chrome Profile và dữ liệu Outlook `.pst`/`.ost`.
- Quét, lựa chọn và khôi phục driver Windows.
- Xuất bản sao lưu dạng ZIP hoặc `.itsbackup` được mã hóa.
- Kiểm tra dung lượng trống và tính toàn vẹn trước khi hoàn tất.
- Ngăn thư mục backup tự sao chép vào chính nó và chặn ZIP có đường dẫn không an toàn.

> Đóng hoàn toàn Chrome và Outlook trước khi sao lưu hoặc khôi phục. Dữ liệu đăng nhập Chrome có thể được Windows mã hóa theo tài khoản hoặc thiết bị và không đảm bảo sử dụng được trên máy khác.

### Tra cứu và quản lý IP/MAC

- Hiển thị card mạng, IPv4, subnet mask và default gateway hiện tại.
- Quét tối đa 4.096 địa chỉ IPv4 mỗi lượt.
- Tra cứu trạng thái, MAC address và hostname của thiết bị.
- Sắp xếp kết quả theo địa chỉ IP và xuất CSV UTF-8.
- Đặt IP tĩnh, gateway, DNS hoặc chuyển card mạng về DHCP.
- Chạy các lệnh mạng ở chế độ ẩn, không bật liên tục cửa sổ CMD.

### Cài đặt máy in mạng

- Dò thiết bị sử dụng cổng RAW TCP `9100`.
- Nhận diện model qua PJL khi thiết bị hỗ trợ.
- Tạo Standard TCP/IP Printer Port và hàng đợi máy in.
- Sử dụng Microsoft IPP Class Driver hoặc driver thủ công từ file `.inf`.
- Gom quá trình cài đặt đặc quyền vào một lần xác nhận UAC.

### Cài phần mềm

Ứng dụng sử dụng Windows Package Manager (`winget`) để kiểm tra và cài đặt các phần mềm phổ biến như:

- 7-Zip, WinRAR, UniKey và UltraViewer;
- Google Chrome, Zalo và VLC;
- Foxit PDF Reader, LibreOffice và Notepad++;
- PowerToys, Everything, CrystalDiskInfo, CPU-Z và HWiNFO.

Các phần mềm đã có trên máy sẽ được nhận diện và tự động bỏ qua.

### Gỡ cài đặt

- Đọc ứng dụng từ Registry theo người dùng và toàn máy, bao gồm nhánh 32-bit/64-bit.
- Tìm kiếm theo tên, phiên bản hoặc nhà phát hành.
- Mở thư mục cài đặt và chạy trình gỡ chính thức.
- Chuẩn hóa lệnh MSI từ chế độ cài/sửa sang gỡ cài đặt.
- Quét tàn dư liên quan trong thư mục cài đặt, AppData, cache và Registry.
- Chỉ xóa tàn dư sau khi người dùng lựa chọn và xác nhận.

## Yêu cầu hệ thống

- Windows 10 hoặc Windows 11 64-bit.
- Python `3.10` đến dưới `3.15` nếu chạy từ source.
- Kết nối Internet cho chức năng cài phần mềm.
- `winget` cho tab **Cài phần mềm**.
- Tài khoản Administrator để chấp nhận UAC khi cấu hình mạng, driver hoặc máy in.

Nếu máy chưa có `winget`, hãy cài hoặc cập nhật **App Installer** từ Microsoft Store.

## Chạy bản EXE

Bản đóng gói mới nhất nằm tại:

```text
dist\ITSupportToolSuite-v1.2.3.exe
```

Chỉ cần nhấp đúp để chạy. Không chọn **Run as administrator**; ứng dụng sẽ tự yêu cầu UAC tại đúng thao tác cần thiết.

Vì bản phát triển chưa có chữ ký số, Windows SmartScreen có thể cảnh báo. Chỉ chạy file nhận từ nguồn tin cậy và đối chiếu SHA-256 trong `dist\SHA256SUMS-v1.2.3.txt`.

## Chạy từ source

Mở PowerShell tại thư mục dự án:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
python -m it_support_suite
```

Những lần chạy sau:

```powershell
.\.venv\Scripts\Activate.ps1
python -m it_support_suite
```

Nếu PowerShell chặn script kích hoạt môi trường ảo:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

## Phát triển và kiểm thử

Cài bộ thư viện dành cho phát triển:

```powershell
python -m pip install -r requirements-dev.txt
python -m pip install -e .
```

Chạy toàn bộ test:

```powershell
python -m pytest
```

Đóng gói phiên bản mới:

```powershell
.\scripts\release.ps1 -Version 1.2.4
```

Script release sẽ chạy test, tạo EXE bằng PyInstaller và xuất checksum SHA-256. Hãy tăng version cho mỗi bản phát hành để giữ các artifact cũ trong `dist`.

## Cấu trúc dự án

```text
toolhelpdesk/
├── src/it_support_suite/       # Mã nguồn ứng dụng
│   ├── __main__.py             # Điểm khởi chạy
│   ├── gui.py                  # Cửa sổ chính và giao diện tab
│   ├── backup_*.py             # Sao lưu, khôi phục và mã hóa
│   ├── network_*.py            # Quét và cấu hình mạng
│   ├── printer_*.py            # Quét và cài máy in
│   ├── software_*.py           # Cài phần mềm bằng winget
│   └── uninstaller_*.py        # Liệt kê và gỡ ứng dụng
├── tests/                      # Kiểm thử tự động
├── scripts/release.ps1         # Quy trình đóng gói release
├── packaging/                  # Cấu hình PyInstaller/installer
├── docs/                       # Tài liệu bảo mật, riêng tư và hỗ trợ
├── requirements.txt            # Thư viện runtime
└── requirements-dev.txt        # Thư viện phát triển
```

## Khắc phục sự cố

### Tab Gỡ cài đặt không hiển thị ứng dụng

- Đảm bảo đang chạy đúng phiên bản mới nhất.
- Đóng hoàn toàn bản cũ trước khi mở EXE mới.
- Nhấn **Làm mới** và kiểm tra ô tìm kiếm đang để trống.
- Xem log tại `%LOCALAPPDATA%\ITSupportToolSuite\logs\application.log`.

### Không cài được phần mềm

```powershell
winget --version
winget source update
```

Nếu lệnh đầu tiên không tồn tại, hãy cập nhật App Installer.

### Không đổi được IP hoặc cài máy in

Chấp nhận hộp thoại UAC và xác nhận tài khoản được dùng có quyền quản trị. Một số phần mềm bảo mật doanh nghiệp có thể chặn PowerShell, DISM, PnPUtil hoặc thay đổi Print Spooler.

### Backup bỏ qua file Chrome hoặc Outlook

Đóng ứng dụng và kết thúc toàn bộ tiến trình `chrome.exe` hoặc `outlook.exe` trong Task Manager, sau đó thử lại.

## Bảo mật và dữ liệu

- Mật khẩu backup mã hóa phải có ít nhất 12 ký tự, không được lưu và không thể khôi phục nếu bị quên.
- Không gửi backup, mật khẩu, Chrome Profile hoặc mailbox Outlook khi yêu cầu hỗ trợ.
- Trước khi báo lỗi, hãy xóa thông tin nhạy cảm khỏi ảnh chụp và log.
- Bản phát hành thương mại phải được ký Authenticode hợp lệ.

Xem thêm: [Security](docs/SECURITY.md), [Privacy](docs/PRIVACY.md), [Support](docs/SUPPORT.md), [EULA](docs/EULA.md) và [Release guide](docs/RELEASING.md).

## Công nghệ

Python · Tkinter · CustomTkinter · PowerShell · winget · DISM · PnPUtil · Netsh · PyInstaller · cryptography

## Giấy phép

Đây là phần mềm sở hữu độc quyền. Không có quyền sử dụng, sao chép, sửa đổi hoặc phân phối nếu chưa có thỏa thuận bằng văn bản với chủ sở hữu bản quyền. Xem [LICENSE](LICENSE) và [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) để biết chi tiết.