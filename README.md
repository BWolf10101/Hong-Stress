Ini merupakan tools sederhana yang di buat hanya untuk uji coba,ini merupakan tools pertama saya yg saya buat untuk uji coba kemanan system dari serangan bot, tools ini belum sempurna dan dapat di blokir oleh system kemanan seperti vercel dll. tetapi HongStress ini tetap dapat bekerja untuk uji coba pentesting tingkat medium.

kerja dari tools ini mengirimkan request yang begitu banyak pada server untuk uji coba system security pada server atau domain untuk dapat memblok aktifitas anomali

untuk penggunaan beta 1:
"python3 ddosatckbeta.py --url https://target-domain --duration 120 --rps 200 --methods "GET,POST" --payloads payloads.txt"

untuk penggunaan beta 2:
"python3 ddosatckbeta2.py --url target --duration 300 --rps 100"

Argumen	Deskripsi
--url	Target URL (contoh: https://target-domain)
--duration	Durasi serangan dalam detik (default: 60)
--rps	Request per second (default: 100)
--methods	Metode HTTP/HTTPS yang digunakan (default: GET,POST,PUT,HEAD,OPTIONS)
--payloads	File teks berisi payload untuk POST/PUT (default: payloads.txt)
