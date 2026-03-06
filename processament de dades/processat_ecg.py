import serial
import json

# ================== PARÀMETRES ==================
freq_mostreig = 100            # Hz (freqüència de mostreig aproximada)

ECG_VALID_MIN = 50
ECG_VALID_MAX = 1000

TEMPS_REFRACTARI_SEC = 0.45    # temps refractari fisiològic
MARGE_PIC_EXTRA = 15           # marge mínim sobre el llindar

MOSTRES_ACTUALITZAR_LLINDAR = freq_mostreig
DURADA_FINESTRA_SEC = 3
MIDA_FINESTRA = DURADA_FINESTRA_SEC * freq_mostreig

FITXER_ENTRADA = "ecg_raw.csv"

FC_MIN = 35
FC_MAX = 200

# ================== VARIABLES D’ESTAT ==================
finestra_ecg = []              # finestra lliscant del senyal ECG
index_mostra = -1

llindar_adaptatiu = None
mostres_des_de_llindar = 0

valors_fc = []                 # valors de freqüència cardíaca (bpm)
fc_min = None
fc_max = None

# Variables per a la detecció del QRS
dins_qrs = False
valor_pic_qrs = None
temps_pic_qrs = None

temps_ultim_qrs = None
# mirar si puedo ejecutar el codigo con el repositorio clonado en mi pc

# ================== FUNCIONS ==================
def calcular_llindar_adaptatiu():
    """Calcula un llindar adaptatiu basat en l’amplitud del senyal ECG."""
    if len(finestra_ecg) < 50:
        return None

    min_ecg = min(finestra_ecg)
    max_ecg = max(finestra_ecg)

    if max_ecg - min_ecg < 5:
        return None

    return min_ecg + 0.8 * (max_ecg - min_ecg)


def processar_mostra_ecg(valor_ecg, temps_sec):
    """Processa una mostra ECG i detecta batecs cardíacs."""
    global index_mostra, llindar_adaptatiu, mostres_des_de_llindar
    global fc_min, fc_max
    global dins_qrs, valor_pic_qrs, temps_pic_qrs, temps_ultim_qrs

    index_mostra += 1

    # 1) Filtrat bàsic per rang vàlid
    if ECG_VALID_MIN < valor_ecg < ECG_VALID_MAX:
        finestra_ecg.append(valor_ecg)
        if len(finestra_ecg) > MIDA_FINESTRA:
            finestra_ecg.pop(0)

    # 2) Actualització periòdica del llindar adaptatiu
    mostres_des_de_llindar += 1
    if llindar_adaptatiu is None or mostres_des_de_llindar >= MOSTRES_ACTUALITZAR_LLINDAR:
        nou_llindar = calcular_llindar_adaptatiu()
        if nou_llindar is not None:
            llindar_adaptatiu = nou_llindar
        mostres_des_de_llindar = 0

    if llindar_adaptatiu is None:
        return

    # 3) Detecció del complex QRS
    if not dins_qrs:
        if valor_ecg > llindar_adaptatiu:
            dins_qrs = True
            valor_pic_qrs = valor_ecg
            temps_pic_qrs = temps_sec
        return

    # 4) Seguiment del pic màxim
    if valor_ecg > valor_pic_qrs:
        valor_pic_qrs = valor_ecg
        temps_pic_qrs = temps_sec

    # 5) Confirmació del batec en baixar del llindar
    if valor_ecg <= llindar_adaptatiu:
        dins_qrs = False

        # Temps refractari fisiològic
        if temps_ultim_qrs is not None and (temps_pic_qrs - temps_ultim_qrs) <= TEMPS_REFRACTARI_SEC:
            return

        # Rebuig de pics petits (soroll)
        if valor_pic_qrs < llindar_adaptatiu + MARGE_PIC_EXTRA:
            return

        # 6) Càlcul de la freqüència cardíaca
        if temps_ultim_qrs is not None:
            interval_rr = temps_pic_qrs - temps_ultim_qrs
            if interval_rr > 0:
                freq_cardiaca = 60.0 / interval_rr
                if FC_MIN <= freq_cardiaca <= FC_MAX:
                    valors_fc.append(freq_cardiaca)
                    fc_min = freq_cardiaca if fc_min is None else min(fc_min, freq_cardiaca)
                    fc_max = freq_cardiaca if fc_max is None else max(fc_max, freq_cardiaca)

        temps_ultim_qrs = temps_pic_qrs


# ================== LECTURA DEL FITXER ==================
with open(FITXER_ENTRADA, "r") as f:
    for linia in f:
        linia = linia.strip()
        if not linia:
            continue

        parts = linia.split(",")
        if len(parts) < 2:
            continue

        try:
            temps = float(parts[0])
            valor_ecg = float(parts[1])
        except ValueError:
            continue

        processar_mostra_ecg(valor_ecg, temps)


# ================== RESULTATS ==================
if not valors_fc:
    print("No s’han detectat batecs vàlids.")
    exit()

# Mitjana robusta (sense valors extrems)
fc_ordenades = sorted(valors_fc)
retall = max(1, int(0.1 * len(fc_ordenades)))
fc_filtrades = fc_ordenades[retall:-retall] if len(fc_ordenades) > 2 * retall else fc_ordenades

fc_mitjana = sum(fc_filtrades) / len(fc_filtrades)

print("\nResum de la freqüència cardíaca")
print(f"FC mínima: {fc_min:.1f} bpm")
print(f"FC mitjana: {fc_mitjana:.1f} bpm")
print(f"FC màxima: {fc_max:.1f} bpm")


# ================== ENVIAMENT A L’ARDUINO ==================
ser = serial.Serial('/dev/serial0', 9600, timeout=1)

payload = {
    "fc_min": round(fc_min, 1),
    "fc_media": round(fc_mitjana, 1),
    "fc_max": round(fc_max, 1)
}

json_data = json.dumps(payload)
ser.write((json_data + "\n").encode())
ser.close()

print("\nJSON enviat a l’Arduino:")
print(json_data)
