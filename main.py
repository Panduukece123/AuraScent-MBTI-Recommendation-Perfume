
# =================================================================================
# APLIKASI GUI REKOMENDASI PARFUM AURA SCENT
# =================================================================================
#
# pip install customtkinter pillow scikit-learn

import customtkinter # Import library customtkinter
from PIL import Image # Import library PIL
import os # untuk mengakses direktori file
import webbrowser # untuk membuka link di browser
from collections import Counter # untuk menghitung frekuensi
from sklearn.feature_extraction.text import TfidfVectorizer # untuk mengubah teks menjadi vektor
from sklearn.metrics.pairwise import cosine_similarity # untuk menghitung kemiripan
import json # untuk mengakses file json
import sys # untuk mengakses sistem operasi

# =================================================================================
# BAGIAN 1: MANAJEMEN DATA
# Membaca data dari file JSON eksternal
# =================================================================================

def load_perfume_database(file_path):
    """Membaca database parfum dari file JSON."""
    try:
        # Menggunakan encoding='utf-8' untuk mendukung karakter non-ASCII
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File database '{file_path}' tidak ditemukan.")
        # Di aplikasi GUI, lebih baik menampilkan dialog error
        # Tapi untuk kesederhanaan, kita print dan keluar
        return None
    except json.JSONDecodeError:
        print(f"ERROR: Format JSON dalam file '{file_path}' tidak valid.")
        return None

# Muat database saat aplikasi dimulai
database_parfum = load_perfume_database('database_parfum.json')

# Jika database gagal dimuat, hentikan aplikasi
if database_parfum is None:
    # Anda bisa menambahkan dialog error CTk di sini jika diinginkan
    sys.exit("Aplikasi tidak dapat berjalan tanpa database parfum.")


# --- Basis Pengetahuan MBTI ---
# --- TAMBAHAN --- Menambahkan key 'gelar' untuk setiap tipe MBTI.
basis_pengetahuan_mbti = {
    "INTJ": {"gelar": "Sang Arsitek", "deskripsi": "Pemikir imajinatif dan strategis. Anda menyukai hal yang kompleks dan elegan.", "preferensi_keyword": ["kompleks", "unik", "woody", "amber", "cerebral", "elegan", "warm spicy"]},
    "INTP": {"gelar": "Sang Logikawan", "deskripsi": "Penemu yang inovatif dengan dahaga tak terpuaskan akan pengetahuan. Anda tertarik pada yang tidak konvensional.", "preferensi_keyword": ["unik", "cerebral", "modern", "kompleks", "aromatic", "fresh", "green"]},
    "ENTJ": {"gelar": "Sang Komandan", "deskripsi": "Pemimpin yang tegas dan berani. Anda menghargai efisiensi, kekuatan, dan wibawa.", "preferensi_keyword": ["berwibawa", "elegan", "klasik", "woody", "spicy", "leather", "formal"]},
    "ENTP": {"gelar": "Sang Pendebat", "deskripsi": "Pemikir yang cerdas dan penasaran. Anda suka menantang dan menikmati hal-hal baru yang enerjik.", "preferensi_keyword": ["enerjik", "spicy", "fresh", "modern", "unik", "citrus", "aromatic"]},
    "INFJ": {"gelar": "Sang Advokat", "deskripsi": "Pendiam dan mistis, namun seorang idealis yang tak kenal lelah. Anda menyukai aroma yang dalam dan menenangkan.", "preferensi_keyword": ["tenang", "balsamic", "hangat", "lembut", "earthy", "sensual", "woody"]},
    "INFP": {"gelar": "Sang Mediator", "deskripsi": "Orang yang puitis, baik hati, dan altruistik. Anda tertarik pada aroma yang lembut, manis, dan otentik.", "preferensi_keyword": ["puitis", "lembut", "manis", "natural", "unik", "powdery", "floral"]},
    "ENFJ": {"gelar": "Sang Protagonis", "deskripsi": "Protagonis yang karismatik dan menginspirasi. Anda menyukai aroma yang hangat, ramah, dan elegan.", "preferensi_keyword": ["hangat", "elegan", "floral", "manis", "amber", "sensual", "spicy"]},
    "ENFP": {"gelar": "Sang Juru Kampanye", "deskripsi": "Semangat bebas yang antusias, kreatif, dan mudah bergaul. Anda menyukai aroma yang ceria, segar, dan tak terduga.", "preferensi_keyword": ["enerjik", "segar", "manis", "natural", "fruity", "citrus", "kasual"]},
    "ISTJ": {"gelar": "Sang Ahli Logistik", "deskripsi": "Individu yang praktis dan mengutamakan fakta. Anda menyukai hal-hal yang andal, bersih, dan klasik.", "preferensi_keyword": ["klasik", "bersih", "fresh", "berwibawa", "formal", "woody", "soapy"]},
    "ISFJ": {"gelar": "Sang Pembela", "deskripsi": "Pelindung yang sangat berdedikasi dan hangat. Anda menyukai aroma yang nyaman, bersih, dan menenangkan.", "preferensi_keyword": ["lembut", "powdery", "bersih", "tenang", "hangat", "floral", "musky"]},
    "ESTJ": {"gelar": "Sang Eksekutif", "deskripsi": "Eksekutif yang sangat baik dalam mengelola sesuatu atau orang. Anda menyukai aroma yang terstruktur dan berwibawa.", "preferensi_keyword": ["berwibawa", "klasik", "elegan", "bersih", "formal", "woody", "spicy"]},
    "ESFJ": {"gelar": "Sang Konsul", "deskripsi": "Orang yang sangat peduli, sosial dan populer. Anda menyukai aroma yang ramah, manis, dan disukai banyak orang.", "preferensi_keyword": ["manis", "floral", "hangat", "elegan", "fruity", "vanilla", "bersih"]},
    "ISTP": {"gelar": "Sang Virtuoso", "deskripsi": "Eksperimenter yang berani dan praktis. Anda tertarik pada aroma yang segar, natural, dan fungsional.", "preferensi_keyword": ["segar", "natural", "bersih", "earthy", "aquatic", "modern", "woody"]},
    "ISFP": {"gelar": "Sang Petualang", "deskripsi": "Seniman yang fleksibel dan menawan. Anda menyukai aroma yang unik, sensual, dan artistik.", "preferensi_keyword": ["unik", "sensual", "fruity", "natural", "puitis", "hangat", "floral"]},
    "ESTP": {"gelar": "Sang Pengusaha", "deskripsi": "Orang yang cerdas, bersemangat, dan sangat perseptif. Anda menyukai aroma yang berani, enerjik, dan modern.", "preferensi_keyword": ["enerjik", "segar", "spicy", "modern", "leather", "citrus", "kasual"]},
    "ESFP": {"gelar": "Sang Penghibur", "deskripsi": "Penghibur yang spontan dan antusias. Anda menyukai aroma yang ceria, manis, dan menjadi pusat perhatian.", "preferensi_keyword": ["manis", "enerjik", "sensual", "fruity", "gourmand", "tropical", "segar"]},
}

# --- Kuesioner MBTI ---
kuesioner_mbti = [
    { "dimensi": "E/I", "pertanyaan": "Setelah acara sosial besar, Anda merasa...", "pilihan": {"a": {"teks": "Bersemangat dan ingin terus bersosialisasi.", "nilai": "E"}, "b": {"teks": "Lelah dan ingin menyendiri untuk mengisi energi.", "nilai": "I"}} },
    { "dimensi": "E/I", "pertanyaan": "Ketika berada di lingkungan baru, Anda biasanya...", "pilihan": {"a": {"teks": "Cepat bersosialisasi dan memperkenalkan diri.", "nilai": "E"}, "b": {"teks": "Mengamati dulu dan cenderung pendiam di awal.", "nilai": "I"}} },
    { "dimensi": "E/I", "pertanyaan": "Waktu luang ideal bagi Anda adalah...", "pilihan": {"a": {"teks": "Berkumpul dengan banyak teman.", "nilai": "E"}, "b": {"teks": "Sendiri atau dengan satu dua orang terdekat.", "nilai": "I"}} },
    { "dimensi": "S/N", "pertanyaan": "Saat mempelajari sesuatu, Anda lebih suka...", "pilihan": {"a": {"teks": "Fakta konkret dan langkah-langkah jelas.", "nilai": "S"}, "b": {"teks": "Konsep umum dan hubungan antar ide.", "nilai": "N"}} },
    { "dimensi": "S/N", "pertanyaan": "Anda lebih nyaman dengan informasi yang...", "pilihan": {"a": {"teks": "Bersifat praktis dan berdasarkan pengalaman.", "nilai": "S"}, "b": {"teks": "Bersifat teoritis dan penuh kemungkinan.", "nilai": "N"}} },
    { "dimensi": "S/N", "pertanyaan": "Saat menyelesaikan masalah, Anda lebih mengandalkan...", "pilihan": {"a": {"teks": "Langkah-langkah logis yang terbukti berhasil.", "nilai": "S"}, "b": {"teks": "Intuisi dan ide-ide kreatif yang belum diuji.", "nilai": "N"}} },
    { "dimensi": "T/F", "pertanyaan": "Dalam mengambil keputusan, Anda lebih mengandalkan...", "pilihan": {"a": {"teks": "Logika dan analisa objektif.", "nilai": "T"}, "b": {"teks": "Nilai-nilai dan perasaan pribadi.", "nilai": "F"}} },
    { "dimensi": "T/F", "pertanyaan": "Dalam konflik, Anda cenderung...", "pilihan": {"a": {"teks": "Langsung dan fokus pada penyelesaian masalah.", "nilai": "T"}, "b": {"teks": "Menjaga perasaan orang lain dan mencari harmoni.", "nilai": "F"}} },
    { "dimensi": "T/F", "pertanyaan": "Ketika seseorang meminta bantuan, Anda lebih fokus pada...", "pilihan": {"a": {"teks": "Solusi logis yang efisien.", "nilai": "T"}, "b": {"teks": "Kebutuhan emosional dan dukungan moral.", "nilai": "F"}} },
    { "dimensi": "J/P", "pertanyaan": "Dalam bekerja, Anda lebih suka...", "pilihan": {"a": {"teks": "Rencana yang teratur dan target jelas.", "nilai": "J"}, "b": {"teks": "Kebebasan untuk menyesuaikan di tengah jalan.", "nilai": "P"}} },
    { "dimensi": "J/P", "pertanyaan": "Saat menyusun jadwal, Anda cenderung...", "pilihan": {"a": {"teks": "Mengikuti rencana yang sudah dibuat.", "nilai": "J"}, "b": {"teks": "Fleksibel dan menyesuaikan dengan kondisi.", "nilai": "P"}} },
    { "dimensi": "J/P", "pertanyaan": "Anda lebih merasa nyaman ketika...", "pilihan": {"a": {"teks": "Segala sesuatu terorganisir dengan baik.", "nilai": "J"}, "b": {"teks": "Ada ruang untuk spontanitas dan perubahan.", "nilai": "P"}} }
]


# =================================================================================
# BAGIAN 2: LOGIKA REKOMENDASI (SISTEM PAKAR & CONTENT-BASED)
# =================================================================================

# Rekomendasi Fungsi
def rekomendasikan_parfum(tipe_mbti, top_n=5):
   
    # --- Corpus teks 
    corpus_parfum = [f"{p['nama']} {p['brand']} {p['keluarga_aroma']} {p['notes_utama']} {p['accords']} {' '.join(p['keywords'])}" for p in database_parfum]
    
    # Inisialisasi TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words=None, ngram_range=(1,2))
    tfidf_matrix = vectorizer.fit_transform(corpus_parfum)
    
    # Validasi tipe MBTI dan ambil profil preferensi
    if tipe_mbti not in basis_pengetahuan_mbti:
        return [], {"deskripsi": f"Tipe MBTI '{tipe_mbti}' tidak valid atau tidak ditemukan."}
        
    profil_pengguna = basis_pengetahuan_mbti[tipe_mbti]
    preferensi_teks = ' '.join(profil_pengguna['preferensi_keyword'])
    
    # Ubah teks preferensi menjadi vektor TF-IDF
    profil_vector = vectorizer.transform([preferensi_teks])
    
    # Hitung cosine similarity antara profil pengguna dan semua parfum
    cosine_scores = cosine_similarity(profil_vector, tfidf_matrix)
    
    # Buat daftar parfum beserta skornya (hanya yang skornya > 0)
    skor_parfum = [{"parfum": database_parfum[i], "skor": score} for i, score in enumerate(cosine_scores[0]) if score > 0]
    
    # Urutkan rekomendasi berdasarkan skor tertinggi
    rekomendasi_terurut = sorted(skor_parfum, key=lambda x: x['skor'], reverse=True)
    
    return rekomendasi_terurut[:top_n], profil_pengguna


# =================================================================================
# BAGIAN 3: KELAS APLIKASI GUI (DENGAN CUSTOMTKINTER)
# =================================================================================

class PerfumeApp(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("AuraScent - Rekomendasi Parfum MBTI")
        self.geometry("1280x720")
        self.minsize(800, 600)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self.last_mbti_type = None
        self.previous_screen_handler = self.show_welcome_screen 
        self.show_welcome_screen()

    def clear_main_frame(self):
        """Menghapus semua widget dari frame utama."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_welcome_screen(self):
        """Menampilkan layar selamat datang."""
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure((0, 2), weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        content_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.grid(row=1, column=0, pady=20)
        
        customtkinter.CTkLabel(content_frame, text="AuraScent", font=("Helvetica", 48, "bold")).pack(pady=(0,10))
        
        # Tampilkan gambar utama
        main_image_path = "images/main_perfume.png"
        try:
            pil_image = Image.open(main_image_path)
            ctk_image = customtkinter.CTkImage(pil_image, size=(500, 312)) 
            image_label = customtkinter.CTkLabel(content_frame, image=ctk_image, text="")
            image_label.pack(pady=20)
        except FileNotFoundError:
            placeholder = customtkinter.CTkFrame(content_frame, width=500, height=312, fg_color="gray20")
            placeholder.pack(pady=20)
            customtkinter.CTkLabel(placeholder, text="Gambar utama tidak ditemukan\n(Letakkan di folder 'images/main_perfume.png')").pack(expand=True)
            
        customtkinter.CTkLabel(content_frame, text="Temukan aroma yang paling mencerminkan kepribadian unik Anda.", 
                               font=("Helvetica", 18), text_color="gray70").pack(pady=(10, 20))
        
        button_container = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        button_container.pack(pady=20, fill="x", expand=True)
        button_container.grid_columnconfigure((0,1,2), weight=1)
        
        customtkinter.CTkButton(button_container, text="Saya Tahu Tipe MBTI", command=self.open_mbti_input, height=50, font=("Helvetica", 16, "bold")).grid(row=0, column=0, padx=10, sticky="ew")
        customtkinter.CTkButton(button_container, text="Bantu Saya Menemukannya", command=self.open_questionnaire, height=50, font=("Helvetica", 16, "bold")).grid(row=0, column=1, padx=10, sticky="ew")
        customtkinter.CTkButton(button_container, text="Lihat Semua Parfum", command=self.show_all_perfumes_screen, height=50, font=("Helvetica", 16, "bold")).grid(row=0, column=2, padx=10, sticky="ew")

    # Metode ini diubah untuk menampilkan gelar MBTI.
    def show_results(self, tipe_mbti):
        """Menampilkan hasil rekomendasi parfum berdasarkan tipe MBTI."""
        self.clear_main_frame()
        self.last_mbti_type = tipe_mbti
        rekomendasi, profil = rekomendasikan_parfum(tipe_mbti)
        
        self.previous_screen_handler = lambda: self.show_results(self.last_mbti_type)
        
        self.main_frame.grid_rowconfigure(0, weight=0)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=0)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Header: Judul, gelar, dan deskripsi profil
        header_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=40, pady=20, sticky="ew")
        
        customtkinter.CTkLabel(header_frame, text=f"Profil Aroma untuk {tipe_mbti}", font=("Helvetica", 32, "bold")).pack()
        
        #  Label  untuk menampilkan "gelar" MBTI.
        customtkinter.CTkLabel(header_frame, text=profil.get('gelar', ''), font=("Helvetica", 20, "bold"), text_color="gray80").pack(pady=(5,0))
        
        customtkinter.CTkLabel(header_frame, text=profil['deskripsi'], wraplength=800, justify="center", font=("Helvetica", 16), text_color="gray70").pack(pady=(5,0))
        
        # Konten: Daftar rekomendasi dalam scrollable frame
        scroll_frame = customtkinter.CTkScrollableFrame(self.main_frame, label_text="5 Rekomendasi Parfum Teratas (Klik untuk detail)", label_font=("Helvetica", 16, "bold"))
        scroll_frame.grid(row=1, column=0, padx=40, pady=10, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        if not rekomendasi:
            customtkinter.CTkLabel(scroll_frame, text="Maaf, belum ada parfum yang cocok di database kami.", font=("Helvetica", 14)).pack(pady=20)
        else:
            for i, item in enumerate(rekomendasi):
                parfum = item['parfum']
                self.create_perfume_card(scroll_frame, parfum, i)
                
        # Footer: Tombol kembali
        bottom_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, pady=20)
        customtkinter.CTkButton(bottom_frame, text="Kembali ke Halaman Utama", command=self.show_welcome_screen, height=40, font=("Helvetica", 14, "bold")).pack()

    def show_all_perfumes_screen(self):
        """Menampilkan daftar semua parfum yang ada di database."""
        self.clear_main_frame()
        
        self.previous_screen_handler = self.show_all_perfumes_screen
        
        self.main_frame.grid_rowconfigure(0, weight=0)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=0)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Header
        header_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=40, pady=20, sticky="ew")
        customtkinter.CTkLabel(header_frame, text="Daftar Semua Parfum", font=("Helvetica", 32, "bold")).pack()
        
        # Konten: Daftar semua parfum dalam scrollable frame
        scroll_frame = customtkinter.CTkScrollableFrame(self.main_frame, label_text="Klik parfum untuk melihat detail", label_font=("Helvetica", 16, "bold"))
        scroll_frame.grid(row=1, column=0, padx=40, pady=10, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        sorted_database = sorted(database_parfum, key=lambda p: p['nama'])

        for i, parfum in enumerate(sorted_database):
            self.create_perfume_card(scroll_frame, parfum, i)
            
        # Footer: Tombol kembali
        bottom_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, pady=20)
        customtkinter.CTkButton(bottom_frame, text="Kembali ke Halaman Utama", command=self.show_welcome_screen, height=40, font=("Helvetica", 14, "bold")).pack()

    def create_perfume_card(self, parent_frame, parfum_data, row_index):
        """Membuat widget kartu untuk satu parfum dan menempatkannya di parent_frame."""
        card = customtkinter.CTkFrame(parent_frame, corner_radius=10, border_width=1, fg_color=("#F0F0F0", "#1C1C1C"))
        card.grid(row=row_index, column=0, pady=10, sticky="ew")
        card.grid_columnconfigure(0, weight=0) 
        card.grid_columnconfigure(1, weight=1) 

        click_handler = lambda event, p=parfum_data: self.show_article_screen(p)
        card.bind("<Button-1>", click_handler)

        image_label = customtkinter.CTkLabel(card, text="", width=120, bg_color="transparent")
        image_label.grid(row=0, column=0, padx=15, pady=15, sticky="ns")
        image_label.bind("<Button-1>", click_handler)
        image_path = parfum_data.get("gambar", None)
        if image_path and os.path.exists(image_path):
            try:
                pil_image = Image.open(image_path)
                ctk_image = customtkinter.CTkImage(pil_image, size=(120, 120))
                image_label.configure(image=ctk_image)
            except Exception:
                image_label.configure(text="Gambar\nError")
        else:
            image_label.configure(text="Gambar\ntidak\tersedia")
        
        content_frame = customtkinter.CTkFrame(card, fg_color="transparent")
        content_frame.grid(row=0, column=1, padx=(0, 20), pady=15, sticky="nsew")
        content_frame.bind("<Button-1>", click_handler)

        label_nama = customtkinter.CTkLabel(content_frame, text=f"{parfum_data['nama']}", font=("Helvetica", 20, "bold"), anchor="w", bg_color="transparent")
        label_nama.pack(fill="x")
        label_nama.bind("<Button-1>", click_handler)
        
        label_brand = customtkinter.CTkLabel(content_frame, text=f"oleh {parfum_data['brand']}", font=("Helvetica", 14), text_color="gray60", anchor="w", bg_color="transparent")
        label_brand.pack(fill="x")
        label_brand.bind("<Button-1>", click_handler)
        
        customtkinter.CTkFrame(content_frame, height=1, fg_color="gray30").pack(fill="x", pady=8)
        customtkinter.CTkLabel(content_frame, text=f"Keluarga Aroma: {parfum_data['keluarga_aroma']}", font=("Helvetica", 14), anchor="w").pack(fill="x")
        customtkinter.CTkLabel(content_frame, text=f"Notes Utama: {parfum_data.get('notes_utama', '')}", font=("Helvetica", 14, "italic"), anchor="w").pack(fill="x", pady=(5,0))

    def show_article_screen(self, parfum_data):
        """Menampilkan layar detail artikel dan INFO untuk satu parfum."""
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0) 
        self.main_frame.grid_columnconfigure(0, weight=1)

        article_scroll_frame = customtkinter.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        article_scroll_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        article_scroll_frame.grid_columnconfigure(0, weight=1)
        
        wrapper_frame = customtkinter.CTkFrame(article_scroll_frame, fg_color="transparent")
        wrapper_frame.grid(row=0, column=0, padx=40, pady=20, sticky="ew")
        wrapper_frame.grid_columnconfigure(0, weight=1)

        image_path = parfum_data.get("gambar")
        if image_path and os.path.exists(image_path):
            try:
                pil_image = Image.open(image_path)
                ctk_image = customtkinter.CTkImage(pil_image, size=(250, 250))
                image_label = customtkinter.CTkLabel(wrapper_frame, image=ctk_image, text="")
                image_label.pack(pady=(0, 20))
            except Exception as e:
                print(f"Error memuat gambar artikel: {e}")
        
        customtkinter.CTkLabel(wrapper_frame, text=parfum_data['nama'], font=("Helvetica", 40, "bold")).pack()
        customtkinter.CTkLabel(wrapper_frame, text=f"oleh {parfum_data['brand']}", font=("Helvetica", 18), text_color="gray60").pack(pady=(0, 15))

        detail_frame = customtkinter.CTkFrame(wrapper_frame, corner_radius=10)
        detail_frame.pack(fill="x", expand=True, pady=10)
        detail_frame.grid_columnconfigure(1, weight=1)

        customtkinter.CTkLabel(detail_frame, text="Tahun Rilis:", font=("Helvetica", 14, "bold")).grid(row=0, column=0, padx=15, pady=8, sticky="w")
        customtkinter.CTkLabel(detail_frame, text=str(parfum_data.get('year', '-')), font=("Helvetica", 14)).grid(row=0, column=1, padx=15, pady=8, sticky="w")
        customtkinter.CTkLabel(detail_frame, text="Perfumer:", font=("Helvetica", 14, "bold")).grid(row=1, column=0, padx=15, pady=8, sticky="w")
        customtkinter.CTkLabel(detail_frame, text=parfum_data.get('perfumer', '-'), font=("Helvetica", 14)).grid(row=1, column=1, padx=15, pady=8, sticky="w")
        customtkinter.CTkLabel(detail_frame, text="Main Accords:", font=("Helvetica", 14, "bold")).grid(row=2, column=0, padx=15, pady=8, sticky="w")
        customtkinter.CTkLabel(detail_frame, text=parfum_data.get('accords', '-'), font=("Helvetica", 14), wraplength=500, justify="left").grid(row=2, column=1, padx=15, pady=8, sticky="w")
        
        purchase_url = parfum_data.get("purchase_link")
        if purchase_url:
            buy_button = customtkinter.CTkButton(wrapper_frame, text="More Info", 
                                                 height=45, font=("Helvetica", 16, "bold"),
                                                 command=lambda url=purchase_url: webbrowser.open(url))
            buy_button.pack(pady=20, padx=50, fill="x")

        customtkinter.CTkLabel(wrapper_frame, text="Deskripsi", font=("Helvetica", 20, "bold"), anchor="w").pack(fill="x", pady=(20, 5))
        customtkinter.CTkFrame(wrapper_frame, height=2, fg_color="gray30").pack(fill="x")
        customtkinter.CTkLabel(wrapper_frame, text=parfum_data.get('artikel', 'Artikel tidak tersedia.'), 
                               font=("Georgia", 16), wraplength=800, justify="left", anchor="w").pack(pady=10, fill='x')

        back_button = customtkinter.CTkButton(self.main_frame, text="< Kembali", 
                                              command=self.previous_screen_handler,
                                              height=40, font=("Helvetica", 14, "bold"))
        back_button.grid(row=1, column=0, pady=20)

    def open_mbti_input(self):
        """Membuka window pop-up untuk input MBTI secara langsung."""
        win = customtkinter.CTkToplevel(self)
        win.title("Masukkan Tipe MBTI")
        win.geometry("400x180")
        win.transient(self)
        win.grab_set() 
        win.resizable(False, False)
        
        customtkinter.CTkLabel(win, text="Pilih tipe kepribadian Anda:", font=("Helvetica", 16)).pack(pady=20)
        mbti_types = list(basis_pengetahuan_mbti.keys())
        mbti_var = customtkinter.StringVar()
        dropdown = customtkinter.CTkComboBox(win, variable=mbti_var, values=mbti_types, width=200, height=35, state="readonly", font=("Helvetica", 14))
        dropdown.pack(pady=5)
        dropdown.set("Pilih salah satu...")
        
        def on_submit():
            if mbti_var.get() in mbti_types:
                self.show_results(mbti_var.get())
                win.destroy()
                
        customtkinter.CTkButton(win, text="Dapatkan Rekomendasi", command=on_submit, height=35, font=("Helvetica", 14, "bold")).pack(pady=20)

    def open_questionnaire(self):
        """Membuka window pop-up untuk kuesioner MBTI."""
        self.q_window = customtkinter.CTkToplevel(self)
        self.q_window.title("Kuesioner Kepribadian")
        self.q_window.transient(self)
        self.q_window.grab_set()
        self.q_window.resizable(False, False)
        
        self.current_q_index = 0
        self.answers = []
        self.answer_var = customtkinter.StringVar()
        
        self.q_frame = customtkinter.CTkFrame(self.q_window, fg_color="transparent")
        self.q_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.display_question()
    
    def display_question(self):
        """Menampilkan pertanyaan kuesioner saat ini."""
        for widget in self.q_frame.winfo_children():
            widget.destroy()
            
        question_data = kuesioner_mbti[self.current_q_index]
        
        customtkinter.CTkLabel(self.q_frame, text=f"Pertanyaan {self.current_q_index + 1}/{len(kuesioner_mbti)}", font=("Helvetica", 12, "bold"), text_color="gray70").pack(pady=(0,10), anchor="w")
        customtkinter.CTkLabel(self.q_frame, text=question_data["pertanyaan"], wraplength=450, font=("Helvetica", 18, "bold")).pack(pady=(0,20), anchor="w")
        self.answer_var.set("")
        
        options_frame = customtkinter.CTkFrame(self.q_frame, fg_color="transparent")
        options_frame.pack(fill="x", pady=10)
        customtkinter.CTkRadioButton(options_frame, text=question_data["pilihan"]["a"]["teks"], variable=self.answer_var, value=question_data["pilihan"]["a"]["nilai"], font=("Helvetica", 14)).pack(anchor="w", pady=8)
        customtkinter.CTkRadioButton(options_frame, text=question_data["pilihan"]["b"]["teks"], variable=self.answer_var, value=question_data["pilihan"]["b"]["nilai"], font=("Helvetica", 14)).pack(anchor="w", pady=8)
        
        btn_text = "Lanjut" if self.current_q_index < len(kuesioner_mbti) - 1 else "Lihat Hasil"
        customtkinter.CTkButton(self.q_frame, text=btn_text, command=self.next_question, height=40, font=("Helvetica", 14, "bold")).pack(pady=20, side="bottom")

    def next_question(self):
        """Memproses jawaban dan lanjut ke pertanyaan berikutnya atau menampilkan hasil."""
        if not self.answer_var.get():
            return 
        
        self.answers.append(self.answer_var.get())
        self.current_q_index += 1
        
        if self.current_q_index < len(kuesioner_mbti):
            self.display_question()
        else:
            final_mbti = self.calculate_mbti_from_answers(self.answers)
            self.q_window.destroy()
            self.show_results(final_mbti)

    def calculate_mbti_from_answers(self, answers):
        """Menghitung tipe MBTI dari kumpulan jawaban."""
        counts = Counter(answers)
        mbti_type = ""
        mbti_type += "E" if counts.get('E', 0) > counts.get('I', 0) else "I"
        mbti_type += "S" if counts.get('S', 0) > counts.get('N', 0) else "N"
        mbti_type += "T" if counts.get('T', 0) > counts.get('F', 0) else "F"
        mbti_type += "J" if counts.get('J', 0) > counts.get('P', 0) else "P"
        return mbti_type


# =================================================================================
# BAGIAN 4: TITIK EKSEKUSI PROGRAM
# =================================================================================

if __name__ == "__main__":
    # Mengatur tema dasar aplikasi (panggil sebelum inisialisasi CTk)
    customtkinter.set_appearance_mode("System") 
    customtkinter.set_default_color_theme("green")

    # Membuat dan menjalankan aplikasi
    app = PerfumeApp()
    app.mainloop()