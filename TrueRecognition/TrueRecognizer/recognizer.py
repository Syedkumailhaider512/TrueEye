import cv2
import face_recognition
import numpy as np
import os
from PIL import Image, ImageDraw
import re


directory = "Database"
image_test = "img.jpg"

def trueHumanRecognizer(directory, image_test):
    threshold = 0.6
    uniqueness = True
    name = None
    encode = None

    known_encodings = []
    known_names = []
    resultant_names = []

    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(directory, filename)
            name = os.path.splitext(filename)[0]
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)[0]
            known_encodings.append(encoding)
            known_names.append(name)

    if len(known_encodings) > 1:
        distances = face_recognition.face_distance(known_encodings[:-1], known_encodings[-1])
        threshold = distances.mean() - 2 * distances.std()


    img = Image.open(image_test)
    img_np = np.array(img)

    face_locations = face_recognition.face_locations(img_np)
    if len(face_locations) == 0:
        None
    else:
        for i, face_location in enumerate(face_locations):
            top, right, bottom, left = face_location
            face_image = img.crop((left-50, top-50, right+50, bottom+50))

            face_image_resized = face_image.resize((500, 500))

            try:
                face_image_resized_rgb = cv2.cvtColor(np.array(face_image_resized), cv2.COLOR_BGR2RGB)
                test_encoding = face_recognition.face_encodings(face_image_resized_rgb)[0]

                distances = face_recognition.face_distance(known_encodings, test_encoding)
                encode = test_encoding

            except:
                break

            best_match_index = -1
            for j, distance in enumerate(distances):
                if distance < 0.25:
                    uniqueness = False
                if distance <= threshold:
                    if best_match_index == -1 or distance < distances[best_match_index]:
                        best_match_index = j

            if best_match_index != -1:
                name = re.sub(r'\d+', '', known_names[best_match_index])
                resultant_names.append(name)
                print(f"Face {i + 1}: {name}")
                name_img = name + ".jpg"
                extension = os.path.splitext(name_img)[1]

                draw = ImageDraw.Draw(img)
                draw.rectangle([left, top, right, bottom], outline='green', width=3)

                if uniqueness != False:
                    if os.path.exists(os.path.join(directory, name_img)):
                        i = 1
                        while True:
                            # If the file with the same name already exists, add an incremental number
                            new_filename = f"{os.path.splitext(name_img)[0]}{i}{extension}"
                            if not os.path.exists(os.path.join(directory, new_filename)):
                                name_img = new_filename
                                break
                            i += 1
                        face_image_resized.save(os.path.join(directory, new_filename))

            else:
                face_image_resized_np = np.array(face_image_resized)
                face_image_resized_bgr = cv2.cvtColor(face_image_resized_np, cv2.COLOR_RGB2BGR)
                cv2.rectangle(face_image_resized_bgr, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.imshow("Image", np.array(face_image_resized_rgb))
                cv2.waitKey(0)
                new_face = input("Name Him/Her: ")
                resultant_names.append(new_face)
                if new_face == "skip":
                    uniqueness == False

                new_face = new_face.title() + ".jpg"
                extension = os.path.splitext(new_face)[1]

                if os.path.exists(os.path.join(directory, new_face)):
                    i = 1
                    while True:
                        # If the file with the same name already exists, add an incremental number
                        new_filename = f"{os.path.splitext(new_face)[0]}{i}{extension}"
                        if not os.path.exists(os.path.join(directory, new_filename)):
                            name_img = new_filename
                            face_image_resized.save(os.path.join(directory, name_img))
                            break
                        i += 1

                else:
                    face_image_resized.save(os.path.join(directory, new_face))


        return resultant_names, encode, known_encodings

a = trueHumanRecognizer(directory,image_test)
print(a)