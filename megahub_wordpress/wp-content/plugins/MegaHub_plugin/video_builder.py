import sys
import os
import time
import cv2
import numpy as np
from moviepy.editor import ImageClip, concatenate_videoclips, CompositeVideoClip, TextClip, ImageSequenceClip
from PIL import Image, ImageDraw, ImageFont

def reformat_image(image_path, output_path, size=(1080, 1920)):
    try:
        image = cv2.imread(image_path)
        h, w = image.shape[:2]

        # Calculer les ratios de redimensionnement et sélectionner le plus petit
        scale_w = size[0] / w
        scale_h = size[1] / h
        scale = max(scale_w, scale_h)

        # Redimensionner l'image en conservant le rapport d'aspect
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized_image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

        # Recadrer l'image pour obtenir les dimensions finales
        crop_x = (new_w - size[0]) // 2
        crop_y = (new_h - size[1]) // 2
        cropped_image = resized_image[crop_y:crop_y + size[1], crop_x:crop_x + size[0]]

        cv2.imwrite(output_path, cropped_image)
        print(f"Image reformattée et sauvegardée: {output_path}")
    except Exception as e:
        print(f"Erreur lors du reformatage de l'image {image_path}: {e}")

def create_slideshow_with_text(image_paths, output_path, location_text, icon_path):
    try:
        clips = []
        duration = 2.5  # Chaque image dure 2,5 secondes

        # Ajouter les images sans effets supplémentaires
        for img_path in image_paths:
            if os.path.exists(img_path):
                img_clip = ImageClip(img_path).set_duration(duration)
                clips.append(img_clip)
            else:
                print(f"Image introuvable: {img_path}")

        if not clips:
            raise Exception("Aucune image valide n'a été trouvée.")

        # Créer le composite vidéo sans transitions
        video = concatenate_videoclips(clips, method="compose")

        # Charger l'icône et créer un fond blanc avec bords arrondis
        icon = Image.open(icon_path).convert("RGBA")
        icon_width, icon_height = icon.size
        background = Image.new('RGBA', (icon_width + 200, icon_height + 50), (255, 255, 255, 255))

        draw = ImageDraw.Draw(background)
        draw.rounded_rectangle([(0, 0), background.size], radius=25, fill=(255, 255, 255, 255))

        # Coller l'icône sur le fond blanc
        background.paste(icon, (25, 25), icon)

        # Ajouter le texte
        try:
            font = ImageFont.truetype("arial", 40)
        except IOError:
            font = ImageFont.load_default()
        
        draw.text((icon_width + 50, 25), location_text, font=font, fill="black")

        # Convertir l'image en clip vidéo
        bg_array = np.array(background)
        bg_clip = ImageClip(bg_array).set_duration(video.duration).set_position(("center", "top"))

        # Combiner le clip vidéo et le clip de texte avec icône
        final_clip = CompositeVideoClip([video, bg_clip])

        final_clip.write_videofile(output_path, fps=24, codec='libx264', remove_temp=True)
        print(f"Vidéo créée: {output_path}")
    except Exception as e:
        print(f"Erreur lors de la création de la vidéo: {e}")

if __name__ == "__main__":
    try:
        image_paths = sys.argv[1:-2]
        icon_path = sys.argv[-2]
        output_dir = sys.argv[-1]
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        output_path = os.path.join(output_dir, f"output_video_{timestamp}.mp4")

        print(f"Chemins des images: {image_paths}")
        print(f"Chemin de sortie: {output_path}")
        print(f"Icon path: {icon_path}")

        formatted_images = []
        for i, image_path in enumerate(image_paths):
            if os.path.exists(image_path):
                formatted_image_path = f"/tmp/formatted_image_{i}.jpg"
                reformat_image(image_path, formatted_image_path)
                formatted_images.append(formatted_image_path)
            else:
                print(f"Image introuvable: {image_path}")

        if formatted_images:
            create_slideshow_with_text(formatted_images, output_path, "Blagnac", icon_path)
        else:
            print("Aucune image formatée disponible pour créer la vidéo.")
    except Exception as e:
        print(f"Erreur dans le script principal: {e}")
