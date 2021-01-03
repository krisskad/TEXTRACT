# import libraries
import csv
import glob
import json
import re
import os
import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'lib\Tesseract-OCR\tesseract.exe'


def pre_processing(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # converting it to binary image
    threshold_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # saving image to view threshold image
    # cv2.imwrite('temp/thresholded.png', threshold_img)

    return threshold_img


def parse_text(threshold_img):
    # configuring parameters for tesseract
    tesseract_config = r'--oem 3 --psm 6'
    # now feeding image to tesseract
    details = pytesseract.image_to_data(threshold_img, output_type=pytesseract.Output.DICT,
                                        config=tesseract_config, lang='eng')
    return details


def draw_boxes(image, details, threshold_point):
    total_boxes = len(details['text'])
    for sequence_number in range(total_boxes):
        if int(details['conf'][sequence_number]) > threshold_point:
            (x, y, w, h) = (details['left'][sequence_number], details['top'][sequence_number],
                            details['width'][sequence_number], details['height'][sequence_number])
            image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # saving image to local
    # cv2.imwrite('temp/captured_text_area.png', image)


def format_text(details):
    parse_text = []
    word_list = []
    last_word = ''
    for word in details['text']:
        if word != '':
            word_list.append(word)
            last_word = word
        if (last_word != '' and word == '') or (word == details['text'][-1]):
            parse_text.append(word_list)
            word_list = []

    return parse_text


def write_text(formatted_text, tex_file_location):
    with open(tex_file_location + 'resulted_text.txt', 'w', newline="") as file:
        csv.writer(file, delimiter=" ").writerows(formatted_text)


def jsonify_data(user_bin_text):
    main_keys = ["Address", "Phone No.", "Fax No.", "Mobile No.", "E-mail", "Website", "Product", "Constitution", "ISO Certification", "Contact Person"]

    # Using readlines()
    file1 = open(user_bin_text + "resulted_text.txt", 'r')
    Lines = file1.readlines()

    last_json = {}

    for i in range(len(Lines)):

        if len(Lines[i].strip()) != 0:
            # Address
            if re.search("Address", Lines[i]) or re.search("Add..ss", Lines[i]) or re.search("Ad....s", Lines[i]):
                if len(str(Lines[i]).strip("Address").strip("+: < > ~").strip("\n")) != 0:
                    index = re.search("Ad....s", Lines[i])
                    last_json["Address"] = str(Lines[i])[index.end():].strip("+: < > ~").strip("\n") + str(
                        Lines[i + 1]).strip()
                else:
                    last_json["Address"] = None
                continue

            # Phone No. and Fax No.
            if re.search("Phone No.", Lines[i]) or re.search("P.....No.", Lines[i]) or re.search("P.....N..", Lines[i]):
                line17 = str(Lines[i]).lstrip("Phone No.").lstrip("+: < >").rstrip("\n") + str(Lines[i + 1]).strip()
                if re.search("F...No.", line17):
                    fax_match = re.search("F...No.", line17)
                    if len(line17[:fax_match.start()].strip("+: < >")) != 0:
                        last_json["Phone_No"] = line17[:fax_match.start()].strip("+: < >")
                    else:
                        last_json["Phone_No"] = None
                    if len(line17[fax_match.end():].lstrip(" : ")) != 0:
                        last_json["Fax_No"] = line17[fax_match.end():].lstrip("+: < >")
                    else:
                        last_json["Fax_No"] = None
                continue

            # Mobile Number
            if re.search("Mobile No.", Lines[i]) or re.search("Mo.....No.", Lines[i]) or re.search("M......N..",
                                                                                                   Lines[i]):
                if len(str(Lines[i]).strip("Mobile No.").strip("+: < > ~").rstrip("\n")) != 0:
                    index = re.search("M......N..", Lines[i])
                    last_json["Mobile_No"] = str(Lines[i])[index.end():].strip("+: < > ~").rstrip("\n")
                else:
                    last_json["Mobile_No"] = None
                continue

            # Email
            if re.search("E-mail", Lines[i]) or re.search("E.m..l", Lines[i]) or re.search("E.ma..", Lines[i]):
                if len(str(Lines[i]).strip("E-mail").strip("+: < > ~").rstrip("\n")) != 0:
                    index = re.search("E.m...", Lines[i])
                    last_json["E-mail"] = str(Lines[i])[index.end():].strip("+: < > ~").rstrip("\n")
                else:
                    last_json["E-mail"] = None
                continue

            # Website
            if re.search("Website", Lines[i]) or re.search("W.bs.t.", Lines[i]) or re.search("W.bs...", Lines[i]):
                if len(str(Lines[i]).strip("Website").strip("+: < > ~").rstrip("\n")) != 0:
                    index = re.search("W.bs.t.", Lines[i])
                    last_json["Website"] = str(Lines[i])[index.end():].strip("+: < > ~").rstrip("\n")
                else:
                    last_json["Website"] = None
                continue

            # Product
            if re.search("Product", Lines[i]) or re.search("P.od.c.", Lines[i]) or re.search("P.od...", Lines[i]):
                if len(str(Lines[i]).strip("Product").strip("+: < > ~").rstrip("\n")) != 0:
                    index = re.search("P.od.c.", Lines[i])
                    last_json["Product"] = str(Lines[i])[index.end():].strip("+: < > ~").rstrip("\n")
                else:
                    last_json["Product"] = None
                continue

            # Constitution and ISO
            if re.search("Constitution", Lines[i]) or re.search("Cons......on", Lines[i]) or re.search("C..s......on",
                                                                                                       Lines[i]):
                line17 = str(Lines[i]).lstrip("Constitution").lstrip("+: < >").rstrip("\n") + str(Lines[i + 1]).strip()
                if re.search("ISO Certification", line17) or re.search(".SO Cer..f.ca..on", line17) or re.search(
                        ".SO Cer....c...on", line17):
                    fax_match = re.search(".SO Cert.f.ca..on", line17)
                    if len(line17[:fax_match.start()].strip("+: < >")) != 0:
                        last_json["Constitution"] = line17[:fax_match.start()].strip("+: < >")
                    else:
                        last_json["Constitution"] = None
                    if len(line17[fax_match.end():].lstrip(" : ")) != 0:
                        last_json["ISO_Certification"] = line17[fax_match.end():].lstrip("+: < >")
                    else:
                        last_json["ISO_Certification"] = None
                continue

            # Contact Person
            if re.search("Contact Person", Lines[i]) or re.search("Con.ac..P..son", Lines[i]) or re.search(
                    "Co...c..P..son", Lines[i]):
                if len(str(Lines[i]).strip("Contact Person").strip("+: < > ~").rstrip("\n")) != 0:
                    index = re.search("Co...c..P..son", Lines[i])
                    last_json["Contact_Person"] = str(Lines[i]).strip("Contact Person").strip("+: < > ~").rstrip("\n")
                else:
                    last_json["Contact_Person"] = None
                continue

            # Company
            last_json["Company"] = str(Lines[0]).strip()

    return last_json


def convert_json(key, value):
    json_world = {}
    json_world[key] = []
    json_world[key].append(value)
    # convert into JSON:
    all_data = json.dumps(json_world)
    return all_data


def detect_text(user_bin_images):
    images_list = [files for files in glob.glob(user_bin_images + "*.png")]
    json_dumping = []

    for i in range(len(images_list)):
        # reading image from local
        image = cv2.imread(images_list[i])
        # calling pre_processing function to perform pre-processing on input image.
        thresholds_image = pre_processing(image)
        # calling parse_text function to get text from image by Tesseract.
        parsed_data = parse_text(thresholds_image)
        # defining threshold for draw box
        # accuracy_threshold = 30
        # calling draw_boxes function which will draw dox around text area.
        # draw_boxes(thresholds_image, parsed_data, accuracy_threshold)
        # calling format_text function which will format text according to input image
        arranged_text = format_text(parsed_data)
        # calling write_text function which will write arranged text into file
        write_text(arranged_text, user_bin_images)

        FINAL_JSON = jsonify_data(user_bin_images)
        json_dumping.append(FINAL_JSON)
        os.remove(images_list[i])

    # convert into JSON
    JSON_DATA = json.dumps(json_dumping)
    return JSON_DATA
