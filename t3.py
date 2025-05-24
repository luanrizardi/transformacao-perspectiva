import cv2
import numpy as np
import sys
import tkinter as tk
from tkinter import filedialog

# Iniciar interface gráfica
root = tk.Tk()
root.withdraw()

# Selecionar imagem fonte (ex: pintura)
caminho_img1 = filedialog.askopenfilename(
    title="Selecione a imagem que será colocada (imagem 1)",
    filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp")]
)
if not caminho_img1:
    print("Nenhuma imagem selecionada para imagem 1. Encerrando.")
    sys.exit(0)

# Selecionar imagem de destino (ex: parede, moldura, ambiente)
caminho_img2 = filedialog.askopenfilename(
    title="Selecione a imagem de fundo (imagem 2)",
    filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp")]
)
if not caminho_img2:
    print("Nenhuma imagem selecionada para imagem 2. Encerrando.")
    sys.exit(0)

# Carregar imagens
img1 = cv2.imread(caminho_img1)
img2 = cv2.imread(caminho_img2)

if img1 is None or img2 is None:
    print("Erro ao carregar uma das imagens.")
    sys.exit(1)

img1_original = img1.copy()
img2_original = img2.copy()
pontos1 = []
pontos2 = []

# Função para selecionar pontos na imagem 1
def selecionar_ponto1(event, x, y, flags, param):
    global pontos1, img1
    if event == cv2.EVENT_LBUTTONDOWN and len(pontos1) < 4:
        pontos1.append([x, y])
        cv2.circle(img1, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow("Selecione 4 pontos da imagem 1", img1)

# Função para selecionar pontos na imagem 2
def selecionar_ponto2(event, x, y, flags, param):
    global pontos2, img2
    if event == cv2.EVENT_LBUTTONDOWN and len(pontos2) < 4:
        pontos2.append([x, y])
        cv2.circle(img2, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow("Selecione 4 pontos da imagem 2", img2)

try:
    print("\n[Imagem 1] Clique nos 4 cantos da região da imagem que será colocada.")
    cv2.imshow("Selecione 4 pontos da imagem 1", img1)
    cv2.setMouseCallback("Selecione 4 pontos da imagem 1", selecionar_ponto1)
    while len(pontos1) < 4:
        if cv2.getWindowProperty("Selecione 4 pontos da imagem 1", cv2.WND_PROP_VISIBLE) < 1:
            print("Janela fechada. Encerrando.")
            sys.exit(0)
        cv2.waitKey(1)
    cv2.destroyWindow("Selecione 4 pontos da imagem 1")

    print("\n[Imagem 2] Clique nos 4 pontos onde a imagem será colocada.")
    cv2.imshow("Selecione 4 pontos da imagem 2", img2)
    cv2.setMouseCallback("Selecione 4 pontos da imagem 2", selecionar_ponto2)
    while len(pontos2) < 4:
        if cv2.getWindowProperty("Selecione 4 pontos da imagem 2", cv2.WND_PROP_VISIBLE) < 1:
            print("Janela fechada. Encerrando.")
            sys.exit(0)
        cv2.waitKey(1)
    cv2.destroyWindow("Selecione 4 pontos da imagem 2")

except KeyboardInterrupt:
    print("\nEncerrado pelo usuário com Ctrl+C.")
    cv2.destroyAllWindows()
    sys.exit(0)

pts_orig = np.float32(pontos1)
pts_dest = np.float32(pontos2)

# Criar uma bounding box ao redor dos pontos da imagem 1
xs = [p[0] for p in pontos1]
ys = [p[1] for p in pontos1]
x_min, x_max = min(xs), max(xs)
y_min, y_max = min(ys), max(ys)

# Recortar somente a região de interesse da imagem 1
img1_crop = img1_original[y_min:y_max, x_min:x_max]

# Ajustar os pontos para o novo sistema de coordenadas da imagem recortada
pts_orig_corrigidos = np.float32([[x - x_min, y - y_min] for (x, y) in pontos1])

# Calcular a homografia com a imagem recortada
h = cv2.getPerspectiveTransform(pts_orig_corrigidos, pts_dest)
img1_warp = cv2.warpPerspective(img1_crop, h, (img2.shape[1], img2.shape[0]))

# Criar máscara da região de destino e mesclar as imagens
mascara = np.zeros((img2.shape[0], img2.shape[1]), dtype=np.uint8)
cv2.fillConvexPoly(mascara, np.int32(pts_dest), 255)
mascara_invertida = cv2.bitwise_not(mascara)
img2_mascara = cv2.bitwise_and(img2_original, img2_original, mask=mascara_invertida)

resultado = cv2.add(img2_mascara, img1_warp)

# Mostrar e salvar resultado
cv2.imshow("Imagem Fundida", resultado)
cv2.imwrite("imagem_colocada.jpg", resultado)
print("\nResultado salvo como 'imagem_colocada.jpg'")
cv2.waitKey(1)
cv2.destroyAllWindows()
sys.exit(0)
