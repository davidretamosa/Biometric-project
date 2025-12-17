import time
from bitalino import BITalino

macAddress = "98:D3:21:FC:8C:30"   # MAC de tu BITalino (Bluetooth)
running_time = 30                  # segundos
batteryThreshold = 30

acqChannels = [1]                  # SOLO A1 (ECG)
samplingRate = 100                 # 100 Hz (más estable por BT que 1000)
nSamples = 10                      # leer en bloques (10 muestras)
output_filename = "ecg_raw.csv"

device = BITalino(macAddress, timeout=5)
device.battery(batteryThreshold)

time.sleep(0.3)
print(device.version())

data_file = open(output_filename, "w")
data_file.write("t,ecg\n")

start = time.time()
end = start

try:
    device.start(samplingRate, acqChannels)

    while (end - start) < running_time:
        samples = device.read(nSamples)

        for s in samples:
            t_rel = time.time() - start
            ecg = s[5]

            data_file.write(f"{t_rel:.6f},{ecg}\n")

        end = time.time()

finally:
    try:
        device.stop()
    except:
        pass
    try:
        device.close()
    except:
        pass
    data_file.close()

print(f"ECG guardat en: {output_filename}")
