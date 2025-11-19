from beamngpy import BeamNGpy, Scenario, Vehicle
from beamngpy.sensors import Camera
from os import listdir, remove
import cv2

def generate_video(sim_name):

    files = sorted(listdir(f'./data/{sim_name}/imgs'), key=lambda x: int(x[1:-4]))

    imgs = []

    for f in files:
        img = cv2.imread(f'./data/{sim_name}/imgs/{f}')
        # Adiciona no frame o step em que foi capturado
        cv2.putText(
            img,
            f[1:],
            (0, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,                # tamanho da fonte
            (0, 255, 0),      # cor verde
            2,                # espessura da linha
            cv2.LINE_AA
        )
        imgs.append(img)

    for f in files:
        remove(f'./data/{sim_name}/imgs/{f}')
    
    alt, lar, _ = imgs[0].shape

    video = cv2.VideoWriter(f"./data/{sim_name}/recording.avi",
                        cv2.VideoWriter_fourcc(*"XVID"),  # codec
                        10,                              # fps
                        (lar, alt))
    
    for frame in imgs:
        video.write(frame)

    video.release()