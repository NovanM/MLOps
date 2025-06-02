# MLOps
# MLOps Project with Jenkins CI/CD Pipeline
mlops2

Proyek MLOps ini menggunakan Jenkins untuk mengotomatisasi proses CI/CD dengan integrasi GitHub webhook. Pipeline ini memungkinkan deployment otomatis setiap kali ada perubahan kode yang di-push ke repository.

## Prerequisites

Sebelum memulai, pastikan lingkungan server (misal EC2 Ubuntu) sudah siap dengan komponen berikut:

### 1. Update Sistem dan Install Docker

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose
```

### 2. Konfigurasi Docker User

Tambahkan user ke grup docker agar tidak perlu sudo saat menjalankan docker:

```bash
sudo usermod -aG docker $USER
```

**Penting:** Logout dan login ulang setelahnya agar perubahan grup berlaku.

### 3. Verifikasi Instalasi

Pastikan Docker dan Docker Compose sudah terinstall dan berjalan:

```bash
docker --version
docker-compose --version
```

### 4. Persiapan Folder Jenkins

Siapkan folder data untuk Jenkins agar data persisten:

```bash
mkdir -p ./jenkins_home
sudo chown -R 1000:1000 ./jenkins_home
sudo chmod -R 755 ./jenkins_home
```

### 5. GitHub Personal Access Token (PAT)

Siapkan GitHub Personal Access Token dengan permission:
- `repo` (akses repository)
- `admin:repo_hook` (mengelola webhook)

Token ini akan digunakan untuk konfigurasi Jenkins agar bisa terhubung ke GitHub.

## Langkah Setup Jenkins dengan Docker Compose

Semua konfigurasi docker-compose sudah tersedia di file `docker-compose.yml` di repo ini.

### 1. Cleanup Container Lama

Hentikan dan hapus container lama Jenkins (jika ada):

```bash
docker rm -f jenkins
```

### 2. Jalankan Jenkins

```bash
docker-compose up -d
```

### 3. Verifikasi Container

Cek container berjalan:

```bash
docker ps
```

### 4. Akses Aplikasi

- **Jenkins Dashboard:** `http://<IP-public-EC2>:8080`
- **Aplikasi MLOps:** `http://<IP-public-EC2>:3000`

### 5. Setup Awal Jenkins

Lakukan setup awal Jenkins (unlock, install plugin default, dll) melalui web interface.

## Konfigurasi GitHub dan Jenkins untuk Webhook

### 1. Tambahkan GitHub Server di Jenkins

1. Masuk ke **Jenkins → Manage Jenkins → Configure System**
2. Scroll ke bagian **GitHub Servers → Add GitHub Server**
3. Centang **Manage hooks** untuk mengaktifkan webhook otomatis
4. Masukkan **Personal Access Token (PAT)** GitHub yang sudah dibuat
5. Tes koneksi dengan tombol **Test Connection**

### 2. Buat Webhook Otomatis di GitHub

Dengan konfigurasi di atas, Jenkins akan otomatis membuat webhook di repo GitHub yang terhubung. 

**Jika ingin konfigurasi manual:**
1. Masuk ke repo GitHub → **Settings → Webhooks → Add webhook**
2. **Payload URL:** `http://<IP-EC2>:8080/github-webhook/`
3. **Content type:** `application/json`
4. **Event:** pilih **Just the push event** (atau sesuai kebutuhan)
5. Simpan

## Testing Webhook dan Pipeline Jenkins

1. Push perubahan ke GitHub pada branch yang terhubung
2. Jenkins akan otomatis trigger pipeline sesuai Jenkinsfile di repo
3. Pantau pipeline di **Jenkins → Job yang berjalan**
4. Jika webhook gagal, cek log Jenkins dan GitHub webhook delivery di repo settings

## Struktur Repo dan File Penting

```
├── docker-compose.yml     # Konfigurasi layanan docker termasuk Jenkins
├── Jenkinsfile           # Pipeline declarative untuk proses CI/CD
├── app.py               # Aplikasi utama
├── requirements.txt     # Dependencies aplikasi
├── templates/           # File template web
├── Script/             # File script project
├── Notebook/           # File notebook ML
└── Data/               # File data ML
```

## Contoh Skenario Webhook Berjalan

1. **Anda melakukan perubahan kode** di branch `main` (atau branch yang sudah dikonfigurasi pipeline) lalu melakukan `git push` ke GitHub.

2. **GitHub otomatis mengirim payload webhook** ke Jenkins pada URL:  
   `http://<IP-EC2>:8080/github-webhook/`

3. **Jenkins menerima webhook** tersebut dan otomatis memicu job pipeline yang sudah diatur pada Jenkinsfile.

4. **Pipeline mulai berjalan** secara otomatis:  
   - Melakukan checkout kode terbaru  
   - Menjalankan proses build, test, dan deploy sesuai script pipeline

5. **Monitoring real-time:** Anda bisa memantau progres pipeline di dashboard Jenkins secara real-time.

6. **Deployment otomatis:** Jika pipeline selesai sukses, aplikasi atau model Anda akan terdeploy/update sesuai alur pipeline.

7. **Error handling:** Jika terjadi error, Jenkins akan menandai job gagal dan Anda bisa langsung cek log untuk debugging.

---

Skenario ini memastikan integrasi GitHub-Jenkins berjalan otomatis dan efisien tanpa perlu trigger manual.
