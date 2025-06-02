# MLOps
# MLOps Project with Jenkins CI/CD Pipeline

## Prerequisites

Sebelum memulai, pastikan lingkungan server (misal EC2 Ubuntu) sudah siap dengan:

1. Update sistem dan install Docker serta Docker Compose:

   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y docker.io docker-compose
Tambahkan user ke grup docker agar tidak perlu sudo saat menjalankan docker:


sudo usermod -aG docker $USER
Logout dan login ulang setelahnya agar perubahan grup berlaku.

Pastikan Docker dan Docker Compose sudah terinstall dan berjalan:

docker --version
docker-compose --version
Siapkan folder data untuk Jenkins agar data persisten

mkdir -p ~/jenkins_home
Siapkan GitHub Personal Access Token (PAT) dengan permission:

repo (akses repository)

admin:repo_hook (mengelola webhook)

Token ini akan digunakan untuk konfigurasi Jenkins agar bisa terhubung ke GitHub.

Langkah Setup Jenkins dengan Docker Compose
Semua konfigurasi docker-compose sudah tersedia di file docker-compose.yml di repo ini.

Hentikan dan hapus container lama Jenkins (jika ada):

docker rm -f jenkins
Jalankan Jenkins dengan docker-compose:

docker-compose up -d
Cek container berjalan:

docker ps
Akses Jenkins di browser:

http://<IP-public-EC2>:8080

Akses Aplikasi MLOps di browseer:
http://<ip-public-ec2:3000

Lakukan setup awal Jenkins (unlock, install plugin default, dll).

Konfigurasi GitHub dan Jenkins untuk Webhook
Tambahkan GitHub Server di Jenkins:

Masuk ke Jenkins → Manage Jenkins → Configure System.

Scroll ke bagian GitHub Servers → Add GitHub Server.

Centang Manage hooks untuk mengaktifkan webhook otomatis.

Masukkan Personal Access Token (PAT) GitHub yang sudah dibuat.

Tes koneksi dengan tombol Test Connection.

Buat Webhook Otomatis di GitHub:

Dengan konfigurasi di atas, Jenkins akan otomatis membuat webhook di repo GitHub yang terhubung. Jika ingin manual:

Masuk ke repo GitHub → Settings → Webhooks → Add webhook.

Payload URL: http://<IP-EC2>:8080/github-webhook/

Content type: application/json

Event: pilih Just the push event (atau sesuai kebutuhan)

Simpan.

Testing Webhook dan Pipeline Jenkins
Push perubahan ke GitHub pada branch yang terhubung.

Jenkins akan otomatis trigger pipeline sesuai Jenkinsfile di repo.

Pantau pipeline di Jenkins → Job yang berjalan.

Jika webhook gagal, cek log Jenkins dan GitHub webhook delivery di repo settings.

Struktur Repo dan File Penting
docker-compose.yml — konfigurasi layanan docker termasuk Jenkins.

Jenkinsfile — pipeline declarative untuk proses CI/CD.

Folder Script/, Notebook/, Data/ — file project dan data ML.

app.py dan requirements — aplikasi utama.

Folder templates/ — file template web.



---

## Contoh Skenario Webhook Berjalan

1. **Anda melakukan perubahan kode** di branch `main` (atau branch yang sudah dikonfigurasi pipeline) lalu melakukan `git push` ke GitHub.

2. GitHub otomatis mengirim payload webhook ke Jenkins pada URL:  
   `http://<IP-EC2>:8080/github-webhook/`

3. Jenkins menerima webhook tersebut dan otomatis memicu job pipeline yang sudah diatur pada Jenkinsfile.

4. Pipeline mulai berjalan secara otomatis:  
   - Melakukan checkout kode terbaru  
   - Menjalankan proses build, test, dan deploy sesuai script pipeline

5. Anda bisa memantau progres pipeline di dashboard Jenkins secara real-time.

6. Jika pipeline selesai sukses, aplikasi atau model Anda akan terdeploy/update sesuai alur pipeline.

7. Jika terjadi error, Jenkins akan menandai job gagal dan Anda bisa langsung cek log untuk debugging.

---

Skenario ini memastikan integrasi GitHub-Jenkins berjalan otomatis dan efisien tanpa perlu trigger manual.
