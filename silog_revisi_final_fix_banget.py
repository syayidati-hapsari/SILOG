# SILOG - Sistem Informasi Logistik
# Tugas Final Struktur Data
# Nama  : SYAYIDATI HAPSARI
# NIM   : 5250411216  (digit terakhir: 6 -> GENAP)
#
# Fitur:
# 1. Weighted Undirected Graph (Adjacency List via Dictionary)
# 2. Binary Search Tree for Resi
# 3. Array/List + Dictionary untuk Kurir & Manifest
#
# Catatan (NIM GENAP):
# - No. resi wajib diawali '2'
# - Algoritma sorting: Selection Sort (descending)
# -  kota hub default: SURABAYA, YOGYAKARTA
#   (saalah satunya mengandung 3 huruf pertama nama depan: SYA)

from __future__ import annotations

import heapq
import re
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple


# =========================
# KONFIGURASI
# =========================
LAST_NIM_DIGIT = 6
# FIRSTNAME_PREFIX = "SYA"
RATE_PER_KM = 2000
RATE_PER_KG = 5000

DEFAULT_CITIES = ["SURABAYA", "YOGYAKARTA"]


# =========================
# DATA CLASS
# =========================
@dataclass
class Receipt:
    no_resi: str
    sender: str
    origin: str
    destination: str
    weight: float
    distance_km: float
    total_cost: float


@dataclass
class Courier:
    courier_id: str
    name: str
    vehicle_type: str


# =========================
# TABEL HELPER
# =========================
def print_table(headers: List[str], rows: List[List[str]], col_widths: List[int] = None, indent: int = 0):
    """Cetak tabel dengan border ASCII. indent = jumlah spasi menjorok ke kanan."""
    if not col_widths:
        col_widths = [max(len(str(headers[i])), max((len(str(r[i])) for r in rows), default=0))
                      for i in range(len(headers))]

    pad = " " * indent

    def row_line(cells):
        return pad + "| " + " | ".join(str(c).ljust(col_widths[i]) for i, c in enumerate(cells)) + " |"

    sep = pad + "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

    print(sep)
    print(row_line(headers))
    print(sep)
    for row in rows:
        print(row_line(row))
    print(sep)


# =========================
# BST UNTUK RESI
# =========================
class BSTNode:
    def __init__(self, data: Receipt):
        self.data = data
        self.left: Optional["BSTNode"] = None
        self.right: Optional["BSTNode"] = None


class ReceiptBST:
    def __init__(self):
        self.root: Optional[BSTNode] = None

    def insert(self, data: Receipt) -> bool:
        if self.root is None:
            self.root = BSTNode(data)
            return True
        curr = self.root
        while True:
            if data.no_resi == curr.data.no_resi:
                return False
            elif data.no_resi < curr.data.no_resi:
                if curr.left is None:
                    curr.left = BSTNode(data)
                    return True
                curr = curr.left
            else:
                if curr.right is None:
                    curr.right = BSTNode(data)
                    return True
                curr = curr.right

    def search(self, no_resi: str) -> Optional[Receipt]:
        curr = self.root
        while curr is not None:
            if no_resi == curr.data.no_resi:
                return curr.data
            elif no_resi < curr.data.no_resi:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def inorder(self) -> List[Receipt]:
        result: List[Receipt] = []
        def _traverse(node: Optional[BSTNode]):
            if not node:
                return
            _traverse(node.left)
            result.append(node.data)
            _traverse(node.right)
        _traverse(self.root)
        return result

    def to_list(self) -> List[Receipt]:
        return self.inorder()


# =========================
# GRAPH BERBOBOT TIDAK BERARAH
# =========================
class WeightedGraph:
    def __init__(self):
        self.adj: Dict[str, Dict[str, float]] = {}

    @staticmethod
    def normalize_city(city: str) -> str:
        return city.strip().upper()

    def add_city(self, city: str) -> bool:
        city = self.normalize_city(city)
        if not city:
            return False
        if city in self.adj:
            return False
        self.adj[city] = {}
        return True

    def add_route(self, city1: str, city2: str, distance: float) -> Tuple[bool, str]:
        city1 = self.normalize_city(city1)
        city2 = self.normalize_city(city2)
        if city1 == city2:
            return False, "Kota asal dan tujuan tidak boleh sama."
        if city1 not in self.adj or city2 not in self.adj:
            return False, "Pastikan kedua kota sudah terdaftar."
        if distance <= 0:
            return False, "Jarak harus lebih besar dari 0."
        self.adj[city1][city2] = distance
        self.adj[city2][city1] = distance
        return True, "Rute berhasil ditambahkan."

    def has_city(self, city: str) -> bool:
        return self.normalize_city(city) in self.adj

    def is_connected(self, start: str, end: str) -> bool:
        return self.shortest_distance(start, end) is not None

    def shortest_distance(self, start: str, end: str) -> Optional[float]:
        """Dijkstra: mengembalikan jarak terpendek; None jika tak terhubung."""
        start = self.normalize_city(start)
        end = self.normalize_city(end)
        if start not in self.adj or end not in self.adj:
            return None
        if start == end:
            return 0.0
        dist = {node: float("inf") for node in self.adj}
        dist[start] = 0.0
        pq = [(0.0, start)]
        visited = set()
        while pq:
            curr_dist, node = heapq.heappop(pq)
            if node in visited:
                continue
            visited.add(node)
            for nxt, weight in self.adj[node].items():
                new_dist = curr_dist + weight
                if new_dist < dist[nxt]:
                    dist[nxt] = new_dist
                    heapq.heappush(pq, (new_dist, nxt))
        return dist[end] if dist[end] != float("inf") else None

    def show_cities(self) -> None:
        if not self.adj:
            print("Belum ada kota yang terdaftar.")
            return
        print("\nDaftar Kota Hub:")
        rows = [[str(i), city] for i, city in enumerate(self.adj.keys(), 1)]
        print_table(["No", "Nama Kota"], rows, [4, 20])

    def show_routes(self) -> None:
        if not self.adj:
            print("Belum ada data graph.")
            return
        print("\nDaftar Rute Antar-Kota:")
        rows = []
        for i, city in enumerate(self.adj.keys(), 1):
            if not self.adj[city]:
                rows.append([str(i), city, "-", "Belum ada rute"])
            else:
                for j, (neighbor, dist) in enumerate(self.adj[city].items()):
                    if j == 0:
                        rows.append([str(i), city, neighbor, f"{dist:g} KM"])
                    else:
                        rows.append(["", "", neighbor, f"{dist:g} KM"])
        print_table(["No", "Kota Asal", "Kota Tujuan", "Jarak"], rows, [4, 15, 15, 12])


# =========================
# UTILITAS
# =========================
def clear_screen():
    print("\n" + "=" * 70)


def pause():
    input("\nTekan ENTER untuk kembali...")


def input_nonempty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Input tidak boleh kosong.")


def input_float(prompt: str, minimum: Optional[float] = None) -> float:
    while True:
        try:
            value = float(input(prompt).strip())
            if minimum is not None and value < minimum:
                print(f"Nilai harus >= {minimum}.")
                continue
            return value
        except ValueError:
            print("Masukkan angka yang valid.")


def input_int(prompt: str, minimum: Optional[int] = None, maximum: Optional[int] = None) -> int:
    while True:
        try:
            value = int(input(prompt).strip())
            if minimum is not None and value < minimum:
                print(f"Nilai harus >= {minimum}.")
                continue
            if maximum is not None and value > maximum:
                print(f"Nilai harus <= {maximum}.")
                continue
            return value
        except ValueError:
            print("Masukkan bilangan bulat yang valid.")


def ask_yes_no(prompt: str) -> bool:
    while True:
        choice = input(prompt).strip().upper()
        if choice in ("Y", "N"):
            return choice == "Y"
        print("Masukkan Y atau N.")


def format_money(amount: float) -> str:
    return f"Rp {amount:,.0f}".replace(",", ".")


def calculate_badge_and_bonus(package_count: int) -> Tuple[str, int]:
    if package_count == 0:
        return "Kurir Santai", 0
    if 1 <= package_count <= 3:
        return "Kurir Reguler", 25000
    if 4 <= package_count <= 6:
        return "Kurir Produktif", 60000
    return "Kurir Elite", 120000


def valid_resi_format(no_resi: str) -> bool:
    if not re.fullmatch(r"\d{4}", no_resi):
        return False
    return no_resi.startswith("2")


# =========================
# SORTING - SELECTION SORT DESCENDING
# =========================
def selection_sort_desc(items: List[Receipt]) -> List[Receipt]:
    arr = items[:]
    n = len(arr)
    for i in range(n):
        max_idx = i
        for j in range(i + 1, n):
            if arr[j].total_cost > arr[max_idx].total_cost:
                max_idx = j
        arr[i], arr[max_idx] = arr[max_idx], arr[i]
    return arr


# =========================
# MENU SISTEM
# =========================
graph = WeightedGraph()
bst = ReceiptBST()
couriers: List[Courier] = []
manifest: Dict[str, List[str]] = {}
assigned_resi: set[str] = set()


def seed_default_cities():
    print("Mendaftarkan kota-kota hub default ke dalam graph...")
    for city in DEFAULT_CITIES:
        if graph.add_city(city):
            print(f"  -> Kota '{city}' berhasil ditambahkan.")
        else:
            print(f"  -> Kota '{city}' sudah ada, dilewati.")
    print(f"Total {len(DEFAULT_CITIES)} kota hub default telah terdaftar.\n")


def menu_1():
    while True:
        clear_screen()
        print("MENU 1) KELOLA JARINGAN HUB DAN RUTE LOGISTIK")
        print("1.1) Input Hub Kota Baru")
        print("1.2) Input Rute Antar-Kota")
        print("1.3) Tampil Data Hub & Rute")
        print("0) Kembali ke MENU UTAMA")

        choice = input("Pilih menu: ").strip()
        if choice == "1.1":
            input_city_menu()
        elif choice == "1.2":
            input_route_menu()
        elif choice == "1.3":
            graph.show_cities()
            graph.show_routes()
            pause()
        elif choice == "0":
            return
        else:
            print("Pilihan tidak valid.")
            pause()


def input_city_menu():
    while True:
        clear_screen()
        city = input_nonempty("Masukkan nama kota hub baru: ")
        if graph.add_city(city):
            print("Hub kota berhasil ditambahkan.")
        else:
            print("Kota sudah ada atau input tidak valid.")
        if not ask_yes_no("Apakah ingin menambahkan kota lagi (Y/N)? "):
            break


def input_route_menu():
    while True:
        clear_screen()
        if len(graph.adj) < 2:
            print("Minimal harus ada 2 kota untuk menambahkan rute.")
            pause()
            return
        graph.show_cities()
        c1 = input_nonempty("Masukkan kota asal: ")
        c2 = input_nonempty("Masukkan kota tujuan: ")
        dist = input_float("Masukkan jarak rute (KM): ", minimum=0.000001)
        ok, msg = graph.add_route(c1, c2, dist)
        print(msg)
        if not ask_yes_no("Apakah ingin menambahkan rute lagi (Y/N)? "):
            break


def input_receipt_menu():
    while True:
        clear_screen()
        print("INPUT RESI PENGIRIMAN BARU")
        if len(graph.adj) < 2:
            print("Belum cukup kota hub untuk validasi rute pengiriman.")
            pause()
            return

        no_resi = input_nonempty("Masukkan No. Resi (4 digit, diawali '2'): ")
        if not valid_resi_format(no_resi):
            print("No. resi harus 4 digit dan diawali dengan '2'.")
            if not ask_yes_no("Coba input resi lagi (Y/N)? "):
                return
            continue

        if bst.search(no_resi) is not None:
            print("No. resi sudah terdaftar.")
            if not ask_yes_no("Coba input resi lagi (Y/N)? "):
                return
            continue

        sender   = input_nonempty("Nama Pengirim: ")
        origin   = input_nonempty("Kota Asal: ").upper()
        destination = input_nonempty("Kota Tujuan: ").upper()
        weight   = input_float("Berat Paket (Kg): ", minimum=0.000001)

        if not graph.has_city(origin) or not graph.has_city(destination):
            print("Pastikan kota asal dan kota tujuan sudah terdaftar di graph.")
            if not ask_yes_no("Coba input resi lagi (Y/N)? "):
                return
            continue

        distance = graph.shortest_distance(origin, destination)
        if distance is None:
            print("Rute pengiriman belum tersedia dalam jaringan!")
            if not ask_yes_no("Coba input resi lagi (Y/N)? "):
                return
            continue

        total_cost = (distance * RATE_PER_KM) + (weight * RATE_PER_KG)
        data = Receipt(
            no_resi=no_resi,
            sender=sender,
            origin=origin,
            destination=destination,
            weight=weight,
            distance_km=distance,
            total_cost=total_cost,
        )

        if bst.insert(data):
            print("\nInput Resi Berhasil!")
            print_table(
                ["No Resi", "Pengirim", "Asal", "Tujuan", "Berat (Kg)", "Jarak (KM)", "Total Biaya"],
                [[data.no_resi, data.sender, data.origin, data.destination,
                  f"{data.weight:g}", f"{data.distance_km:g}", format_money(data.total_cost)]],
                [8, 15, 12, 12, 10, 10, 16]
            )
        else:
            print("Gagal menyimpan resi karena no. resi sudah ada.")

        if not ask_yes_no("Apakah ingin melakukan input resi lagi (Y/N)? "):
            break


def show_all_receipts_menu():
    clear_screen()
    data = bst.inorder()
    print("DATA RESI TERDAFTAR")
    if not data:
        print("Belum ada data resi.")
        pause()
        return

    rows = [
        [r.no_resi, r.sender, r.origin, r.destination,
         f"{r.weight:g}", f"{r.distance_km:g}", format_money(r.total_cost)]
        for r in data
    ]
    print_table(
        ["No Resi", "Pengirim", "Asal", "Tujuan", "Berat (Kg)", "Jarak (KM)", "Total Biaya"],
        rows,
        [8, 15, 12, 12, 10, 10, 16]
    )
    pause()


def sort_receipts_menu():
    clear_screen()
    data = bst.to_list()
    print("URUTAN TRANSAKSI RESI BERDASARKAN BIAYA TERBESAR")
    if not data:
        print("Belum ada data resi.")
        pause()
        return

    sorted_data = selection_sort_desc(data)
    rows = [
        [str(i), r.no_resi, format_money(r.total_cost), r.sender,
         r.origin, r.destination, f"{r.weight:g}"]
        for i, r in enumerate(sorted_data, 1)
    ]
    print_table(
        ["Rank", "No Resi", "Total Biaya", "Pengirim", "Asal", "Tujuan", "Berat (Kg)"],
        rows,
        [4, 8, 16, 15, 12, 12, 10]
    )
    pause()


def menu_2():
    while True:
        clear_screen()
        print("MENU 2) KELOLA ADMINISTRASI RESI PENGIRIMAN")
        print("2.1) Input Resi Pengiriman Baru")
        print("2.2) Lihat Seluruh Data Resi Terdaftar")
        print("2.3) Urutkan Transaksi Resi Berdasarkan Biaya Terbesar")
        print("0) Kembali ke MENU UTAMA")

        choice = input("Pilih menu: ").strip()
        if choice == "2.1":
            input_receipt_menu()
        elif choice == "2.2":
            show_all_receipts_menu()
        elif choice == "2.3":
            sort_receipts_menu()
        elif choice == "0":
            return
        else:
            print("Pilihan tidak valid.")
            pause()


def input_courier_menu():
    while True:
        clear_screen()
        print("INPUT DATA KURIR")
        courier_id = input_nonempty("ID Kurir: ")
        if any(c.courier_id == courier_id for c in couriers):
            print("ID kurir sudah terdaftar.")
            if not ask_yes_no("Apakah ingin menambahkan data Kurir lagi (Y/N)? "):
                break
            continue

        name    = input_nonempty("Nama Kurir: ")
        vehicle = input_nonempty("Jenis Kendaraan (Motor/Mobil/Truck): ").capitalize()
        if vehicle not in ("Motor", "Mobil", "Truck"):
            print("Jenis kendaraan harus salah satu dari: Motor, Mobil, Truck.")
            if not ask_yes_no("Apakah ingin menambahkan data Kurir lagi (Y/N)? "):
                break
            continue

        couriers.append(Courier(courier_id, name, vehicle))
        manifest.setdefault(courier_id, [])
        print("Data Kurir Berhasil Diinputkan")
        if not ask_yes_no("Apakah ingin menambahkan data Kurir lagi (Y/N)? "):
            break


def show_available_receipts():
    data = bst.inorder()
    if not data:
        print("Belum ada data resi.")
        return []

    print("\nDaftar Resi:")
    rows = [
        [r.no_resi, r.origin, r.destination,
         format_money(r.total_cost),
         "Sudah dialokasikan" if r.no_resi in assigned_resi else "Tersedia"]
        for r in data
    ]
    print_table(
        ["No Resi", "Asal", "Tujuan", "Total Biaya", "Status"],
        rows,
        [8, 12, 12, 16, 18]
    )
    return data


def plotting_manifest_menu():
    clear_screen()
    print("PLOTTING PENUGASAN MANIFEST")
    if not couriers:
        print("Belum ada data kurir.")
        pause()
        return
    if not bst.inorder():
        print("Belum ada data resi.")
        pause()
        return

    print("Daftar Kurir:")
    rows_kurir = [[c.courier_id, c.name, c.vehicle_type] for c in couriers]
    print_table(["ID Kurir", "Nama", "Kendaraan"], rows_kurir, [10, 20, 12])

    courier_id = input_nonempty("\nMasukkan ID Kurir yang akan ditugaskan: ")
    target = next((c for c in couriers if c.courier_id == courier_id), None)
    if target is None:
        print("ID kurir tidak ditemukan.")
        pause()
        return

    print(f"\nKurir terpilih: {target.name} ({target.vehicle_type})")
    print("Silakan pilih resi yang akan dimasukkan ke manifest.")
    while True:
        available = show_available_receipts()
        if not available:
            pause()
            return

        no_resi = input_nonempty("\nMasukkan No. Resi yang akan ditugaskan: ")
        receipt = bst.search(no_resi)
        if receipt is None:
            print("No. resi tidak ditemukan.")
        elif no_resi in assigned_resi:
            print("Resi sudah ditugaskan ke kurir lain.")
        else:
            manifest.setdefault(courier_id, []).append(no_resi)
            assigned_resi.add(no_resi)
            print("Resi berhasil ditambahkan ke manifest kurir.")

        if not ask_yes_no("Apakah ingin memasukkan No. Resi lagi (Y/N)? "):
            break

    print("Proses plotting manifest selesai.")
    pause()


def tampil_manifest_menu():
    clear_screen()
    print("TAMPIL MANIFEST & ATURAN BONUS INSENTIF")
    if not couriers:
        print("Belum ada data kurir.")
        pause()
        return

    receipt_cache = {r.no_resi: r for r in bst.inorder()}

    for i, c in enumerate(couriers, 1):
        resi_list = manifest.get(c.courier_id, [])
        badge, bonus = calculate_badge_and_bonus(len(resi_list))

        print(f"\n{'=' * 75}")
        print_table(
            ["No", "ID Kurir", "Nama Kurir", "Kendaraan", "Jml Resi", "Lencana", "Bonus Insentif"],
            [[str(i), c.courier_id, c.name, c.vehicle_type,
              str(len(resi_list)), badge, format_money(bonus)]],
            [4, 10, 20, 10, 9, 18, 14]
        )

        if not resi_list:
            print("      Manifest kosong.")
        else:
            print("      Rincian Resi:")
            detail_rows = []
            for idx, no_resi in enumerate(resi_list, 1):
                r = receipt_cache.get(no_resi)
                if r is None:
                    detail_rows.append([str(idx), no_resi, "-", "-", "-", "-", "-"])
                else:
                    detail_rows.append([
                        str(idx), r.no_resi, r.sender,
                        r.origin, r.destination,
                        f"{r.weight:g} Kg", format_money(r.total_cost)
                    ])
            print_table(
                ["No", "No Resi", "Pengirim", "Asal", "Tujuan", "Berat", "Total Biaya"],
                detail_rows,
                [4, 8, 18, 12, 12, 8, 16],
                indent=6
            )

    print()
    pause()


def menu_3():
    while True:
        clear_screen()
        print("MENU 3) KELOLA KURIR DAN MANIFEST PENGANTARAN")
        print("3.1) Input Data Kurir")
        print("3.2) Plotting Penugasan Manifest")
        print("3.3) Tampil Manifest & Aturan Bonus Insentif")
        print("0) Kembali ke MENU UTAMA")

        choice = input("Pilih menu: ").strip()
        if choice == "3.1":
            input_courier_menu()
        elif choice == "3.2":
            plotting_manifest_menu()
        elif choice == "3.3":
            tampil_manifest_menu()
        elif choice == "0":
            return
        else:
            print("Pilihan tidak valid.")
            pause()


def main():
    seed_default_cities()

    while True:
        clear_screen()
        print("SILOG - SISTEM INFORMASI LOGISTIK")
        print("-" * 70)
        print("1) Kelola Jaringan Hub dan Rute Logistik")
        print("2) Kelola Administrasi Resi Pengiriman")
        print("3) Kelola Kurir dan Manifest Pengantaran")
        print("0) Exit Program")

        choice = input("Pilih menu utama: ").strip()
        if choice == "1":
            menu_1()
        elif choice == "2":
            menu_2()
        elif choice == "3":
            menu_3()
        elif choice == "0":
            print("Program dihentikan.")
            break
        else:
            print("Pilihan tidak valid.")
            pause()


if __name__ == "__main__":
    main()
