# Tugas 2 Jaringan Komputer (Gasal 2019/2020)

- Nama : Farhan Azyumardhi Azmi
- NPM : 1706979234
- Kelas : B


# Persiapan

## Tool yang dibutuhkan

- Python 3.6 atau versi terbaru.
- PIP untuk Python 3.

## Instalasi

- Bila menggunakan Ubuntu/Debian, jalankan `sudo apt-get install gcc python3-dev`
- Bila menggunakan RedHat/CentOS, jalankan `sudo yum install gcc python3-devel`
- Install semua dependency dengan menjalankan `pip install -r requirements.txt` atau `pip3 install -r requirements.txt` (Disarankan menggunakan virtual environment).

# Penggunaan

## Server

Jalankan server dengan perintah 
`python app-server.py [host] [port]` atau
`python3 app-server.py [host] [port]`.

## Client

Setelah server dinyalakan, jalankan client dengan perintah 
`python app-client.py [host] [port] [perintah]` atau
`python3 app-client.py [host] [post] [perintah]`. 

Untuk melihat semua perintah yang memungkinkan, jalankan 
`python app-client.py --help` atau 
`python3 app-client.py --help`.


# Referensi
- https://realpython.com/python-sockets/
- https://github.com/realpython/materials/tree/master/python-sockets-tutorial
