import tkinter as tk
from tkinter import messagebox
import datetime

# --- 1. DATA SIMULASI GLOBAL ---
DAFTAR_LAPANGAN = [] 
LIST_BOOKING_SEMUA = []
ADMIN_USERNAME, ADMIN_PASSWORD = "admin", "123"
PERAN_AKTIF = "USER" 

class Lapangan:
    def __init__(self, id_lapangan, jenis, harga):
        self.id_lapangan, self.jenis, self.__harga = id_lapangan, jenis, harga
    # Harga/jam murni harga dasar
    def hitung_biaya(self, durasi): return self.__harga * durasi 

class Futsal(Lapangan):
    def __init__(self, id, harga, premium):
        super().__init__(id, "Futsal", harga); self.is_premium = premium
    # Menggunakan hitung_biaya dari class Lapangan (Tanpa tambahan/pengurangan)
    def hitung_biaya(self, durasi):
        return super().hitung_biaya(durasi) 

class Basket(Lapangan):
    def __init__(self, id, harga, outdoor):
        super().__init__(id, "Basket", harga); self.is_outdoor = outdoor
    # Menggunakan hitung_biaya dari class Lapangan (Tanpa tambahan/pengurangan)
    def hitung_biaya(self, durasi):
        return super().hitung_biaya(durasi)
    
class Booking:
    def __init__(self, lap_obj, tgl, mulai, durasi, pelanggan):
        self.lap_obj, self.tanggal = lap_obj, tgl
        self.jam_mulai, self.durasi = mulai, durasi
        self.jam_selesai = mulai + durasi
        self.total_bayar = lap_obj.hitung_biaya(durasi) 
        self.nama_pelanggan = pelanggan

    def cek_ketersediaan(self):
        if self.jam_selesai > 23: return False
        for j in range(self.jam_mulai, self.jam_selesai): 
            for b in LIST_BOOKING_SEMUA:
                if (b["id_lapangan"] == self.lap_obj.id_lapangan and b["tanggal"] == self.tanggal):
                    if (j >= b["jam_mulai"] and j < b["jam_selesai"]): return False 
        return True

    def simpan_booking(self):
        if self.cek_ketersediaan():
            LIST_BOOKING_SEMUA.append({"id_lapangan": self.lap_obj.id_lapangan, "tanggal": self.tanggal, "jam_mulai": self.jam_mulai, "jam_selesai": self.jam_selesai, "durasi": self.durasi, "total_bayar": self.total_bayar, "pelanggan": self.nama_pelanggan })
            return True
        return False

# --- 2. IMPLEMENTASI GUI TKINTER ---
class AplikasiBooking(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplikasi Booking Lapangan")
        self.geometry("1100x600")
        self.jenis_lapangan_aktif, self.tgl_aktif = "Futsal", datetime.date.today().strftime("%Y-%m-%d")
        self.jam_mulai_tersedia = range(8, 23) 
        self._setup_data(); self._create_widgets(); self.tampilkan_lapangan()

    def _setup_data(self):
        # HARGA FINAL BERDASARKAN PERMINTAAN USER (Tanpa Tambahan/Diskon)
        DAFTAR_LAPANGAN.extend([
            Futsal("FUTSAL_1", 30000, False),    # Harga dasar 30.000/jam
            Futsal("FUTSAL_2", 60000, True),     # Harga dasar 60.000/jam 
            Basket("BASKET_A", 50000, True),     # Harga dasar 50.000/jam
            Basket("BASKET_B", 100000, False)   # Harga dasar 100.000/jam
        ])

    def _create_widgets(self):
        self.mode_frame = tk.Frame(self); self.mode_frame.pack(pady=5); self._create_mode_selector() 
        self.filter_frame = tk.Frame(self); self.filter_frame.pack(pady=5); self._create_filter_widgets() 

        self.canvas = tk.Canvas(self); self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas)
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion = self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True); self.scrollbar.pack(side="right", fill="y")
        
    def _create_mode_selector(self):
        global PERAN_AKTIF
        [w.destroy() for w in self.mode_frame.winfo_children()]
        tk.Label(self.mode_frame, text="Mode Tampilan:").pack(side=tk.LEFT, padx=5)

        tk.Button(self.mode_frame, text="USER", command=lambda: self.set_peran("USER"), relief=tk.RAISED if PERAN_AKTIF == "USER" else tk.FLAT).pack(side=tk.LEFT, padx=5)
        
        btn_text = "ADMIN (Logout)" if PERAN_AKTIF == "ADMIN" else "ADMIN"
        cmd = lambda: self.set_peran("USER") if PERAN_AKTIF == "ADMIN" else self._form_login_admin()
        tk.Button(self.mode_frame, text=btn_text, command=cmd, relief=tk.RAISED if PERAN_AKTIF == "ADMIN" else tk.FLAT).pack(side=tk.LEFT, padx=5)
        
    def _form_login_admin(self):
        top = tk.Toplevel(self); top.title("Admin Login"); entries = {}
        for i, (l, s) in enumerate([("Username:", ""), ("Password:", "*")]):
            tk.Label(top, text=l).grid(row=i, column=0, padx=10, pady=5, sticky='w')
            e = tk.Entry(top, width=25, show=s); e.grid(row=i, column=1, padx=10, pady=5); entries[l.split(':')[0].lower()] = e
        
        def proses():
            if entries['username'].get() == ADMIN_USERNAME and entries['password'].get() == ADMIN_PASSWORD:
                messagebox.showinfo("Sukses", "Login Admin Berhasil!"); top.destroy(); self.set_peran("ADMIN")
            else: messagebox.showerror("Gagal", "Username atau Password salah.")

        tk.Button(top, text="Login", command=proses).grid(row=2, column=0, columnspan=2, pady=15)

    def set_peran(self, peran_baru):
        global PERAN_AKTIF; PERAN_AKTIF = peran_baru; self._create_mode_selector(); self.tampilkan_lapangan() 

    def _create_filter_widgets(self):
        [w.destroy() for w in self.filter_frame.winfo_children()]
        for jenis in ["Futsal", "Basket"]:
            active = (jenis == self.jenis_lapangan_aktif)
            tk.Button(self.filter_frame, text=jenis, command=lambda j=jenis: self._set_jenis(j), padx=10, relief=tk.RAISED if active else tk.FLAT, bg="#dddddd" if active else "white").pack(side=tk.LEFT, padx=5)

    def _set_jenis(self, jenis):
        self.jenis_lapangan_aktif = jenis; self._create_filter_widgets(); self.tampilkan_lapangan() 

    def _get_booking(self, id, tgl, jam):
        for b in LIST_BOOKING_SEMUA:
            if b["id_lapangan"] == id and b["tanggal"] == tgl and (jam >= b["jam_mulai"] and jam < b["jam_selesai"]): return b
        return None

    def _is_slot_available(self, id, tgl, jam, dur):
        for j in range(jam, jam + dur):
            if j >= 23: return False
            if self._get_booking(id, tgl, j): return False 
        return True 

    def tampilkan_lapangan(self):
        global PERAN_AKTIF; [w.destroy() for w in self.scroll_frame.winfo_children()]
        filtered = [l for l in DAFTAR_LAPANGAN if l.jenis == self.jenis_lapangan_aktif]
        tk.Label(self.scroll_frame, text=f"LAPANGAN {self.jenis_lapangan_aktif.upper()} (Mode: {PERAN_AKTIF})", font=("Helvetica", 14, "bold"), pady=10).pack(fill='x')

        for lap_obj in filtered:
            f = tk.Frame(self.scroll_frame, bd=1, relief=tk.GROOVE, padx=5, pady=10); f.pack(fill='x', padx=5, pady=5)
            
            info = f"ID: {lap_obj.id_lapangan} "
            if isinstance(lap_obj, Futsal): info += "(Premium)" if lap_obj.is_premium else "(Reguler)"
            elif isinstance(lap_obj, Basket): info += "(Outdoor)" if lap_obj.is_outdoor else "(Indoor)"
            
            tk.Label(f, text=info, font=("Helvetica", 12, "bold")).pack(anchor='w')
            tk.Label(f, text=f"Harga/Jam: Rp{lap_obj.hitung_biaya(1):,.0f}").pack(anchor='w')
            slot_frame = tk.Frame(f, pady=5); slot_frame.pack(fill='x')

            for jam in self.jam_mulai_tersedia:
                is_available = self._is_slot_available(lap_obj.id_lapangan, self.tgl_aktif, jam, 1)
                b_info = self._get_booking(lap_obj.id_lapangan, self.tgl_aktif, jam)
                
                # Logika Slot Tombol
                if PERAN_AKTIF == "USER":
                    if is_available:
                        # Di mode USER, jika slot tersedia, hanya menampilkan jam dan dinonaktifkan.
                        config = {"text": f"{jam:02d}:00", "bg": "#a0e0a0", "fg": "black", "state": tk.DISABLED, "cmd": None}
                    else:
                        # Jika slot terisi, tampilkan nama pembooking di jam mulai
                        text = f"{jam:02d}:00\n({b_info.get('pelanggan', 'TERISI')})" if jam == b_info["jam_mulai"] else "---" 
                        config = {"text": text, "bg": "gray", "fg": "white", "state": tk.DISABLED, "font": ("Helvetica", 7)}
                else: # ADMIN MODE
                    if is_available:
                        # Tersedia: Admin bisa Book Manual
                        cmd = lambda l=lap_obj, j=jam: self._form_booking_manual(l, j)
                        config = {"text": "Book Man.", "bg": "#ffffb3", "fg": "black", "state": tk.NORMAL, "cmd": cmd}
                    else:
                        # Terisi: Admin bisa Cancel/Unblock (hanya di jam mulai booking)
                        if jam == b_info["jam_mulai"]:
                            cmd = lambda l=lap_obj, j=jam: self._handle_cancel(l, j)
                            config = {"text": f"Cancel ({b_info.get('pelanggan', 'N/A')})", "bg": "#ff9999", "fg": "black", "state": tk.NORMAL, "cmd": cmd}
                        else:
                            config = {"text": "TERISI", "bg": "#cc6666", "fg": "white", "state": tk.DISABLED}

                btn = tk.Button(slot_frame, text=config['text'], bg=config['bg'], fg=config['fg'], state=config['state'], command=config.get('cmd'), padx=5)
                if 'font' in config: btn.config(font=config['font'])
                btn.pack(side=tk.LEFT, padx=3, pady=3)

    def _form_booking_manual(self, lap_obj, jam_mulai):
        top = tk.Toplevel(self); top.title(f"Book Manual: {lap_obj.id_lapangan} Jam {jam_mulai}:00")
        tk.Label(top, text="Nama Pembooking:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
        nama_entry = tk.Entry(top, width=30); nama_entry.grid(row=0, column=1, padx=10, pady=5)
        tk.Label(top, text="Jam Mulai:").grid(row=1, column=0, sticky='w'); tk.Label(top, text=f"{jam_mulai}:00").grid(row=1, column=1, sticky='w')
        tk.Label(top, text="Durasi (Jam):").grid(row=2, column=0, sticky='w')
        durasi_var = tk.StringVar(top, value=1) 
        max_durasi = 2 if lap_obj.jenis == "Futsal" else 5
        available_durations = [d for d in range(1, max_durasi + 1) if self._is_slot_available(lap_obj.id_lapangan, self.tgl_aktif, jam_mulai, d)]
        
        if not available_durations:
            messagebox.showwarning("Perhatian", "Tidak ada durasi yang tersedia dari jam ini."); top.destroy(); return

        durasi_var.set(available_durations[0]) 
        durasi_menu = tk.OptionMenu(top, durasi_var, *available_durations); durasi_menu.grid(row=2, column=1, sticky='w')
        
        def proses():
            nama, durasi = nama_entry.get().strip(), int(durasi_var.get())
            if not nama: messagebox.showerror("Error", "Nama harus diisi."); return
            booking_baru = Booking(lap_obj, self.tgl_aktif, jam_mulai, durasi, nama)
            if booking_baru.simpan_booking():
                messagebox.showinfo("Sukses!", f"Booking berhasil untuk {nama} selama {durasi} jam. Total: Rp{booking_baru.total_bayar:,.0f}"); top.destroy(); self.tampilkan_lapangan()
            else: messagebox.showerror("Gagal", "Slot waktu bentrok atau melewati batas jam 23:00.") 

        tk.Button(top, text="Book Sekarang", command=proses).grid(row=3, column=0, columnspan=2, pady=15)

    def _handle_cancel(self, lap_obj, jam_mulai):
        global LIST_BOOKING_SEMUA
        
        booking_to_remove = None
        for b in LIST_BOOKING_SEMUA:
            if (b["id_lapangan"] == lap_obj.id_lapangan and 
                b["tanggal"] == self.tgl_aktif and 
                b["jam_mulai"] == jam_mulai):
                booking_to_remove = b
                break
        
        if booking_to_remove:
            pelanggan, durasi = booking_to_remove.get('pelanggan'), booking_to_remove.get('durasi')
            
            if messagebox.askyesno("Admin Unblock", f"Yakin ingin MENGOSONGKAN booking {pelanggan} untuk {durasi} jam (mulai {jam_mulai}:00)?"):
                LIST_BOOKING_SEMUA.remove(booking_to_remove)
                messagebox.showinfo("Sukses", f"Booking {pelanggan} dibatalkan."); self.tampilkan_lapangan()
        else:
            messagebox.showwarning("Error", "Booking tidak ditemukan atau ini bukan jam mulai booking yang valid.")

if __name__ == "__main__":
    app = AplikasiBooking()
    app.mainloop()