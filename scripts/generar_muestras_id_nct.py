# Cuadrícula 5x2: 5 imágenes al azar de una clase ID (test) junto a 5 de una clase de NCT-CRC.
# uso: generar_muestras_id_nct.py <clase ID> <titulo ID> <clase NCT> <titulo NCT> <salida.pdf> [semilla=0]
import random, os, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
ID="/mnt/homeGPU/slcerro/tfg/TrainTest/test/"+sys.argv[1]
NCT="/mnt/homeGPU/slcerro/OpenOOD/ood_data/nct_crc_nonorm/"+sys.argv[3]
random.seed(int(sys.argv[6]) if len(sys.argv)>6 else 0)
cols=[(ID,sys.argv[2]),(NCT,sys.argv[4])]
fig,ax=plt.subplots(5,2,figsize=(4.4,10.5))
for j,(d,t) in enumerate(cols):
    fs=random.sample(sorted(os.listdir(d)),5)
    print(t.replace("\n"," "),fs)
    ax[0,j].set_title(t,fontsize=10)
    for i,f in enumerate(fs):
        ax[i,j].imshow(Image.open(os.path.join(d,f)).convert("RGB")); ax[i,j].axis("off")
fig.tight_layout(); fig.savefig(sys.argv[5],bbox_inches="tight")
