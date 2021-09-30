from pdf2image import convert_from_path
import cv2
import tempfile
import numpy as np
import pandas as pd
import pickle
import pytesseract

pdf_file="benign_soft_tissue_tumors-3-4-rotated.pdf"

table_ocrs=[]
with tempfile.TemporaryDirectory() as path:
    images_from_path = convert_from_path( pdf_file, output_folder=path)
    for image in images_from_path:
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

        thresh, img_bin = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        img_bin = 255 - img_bin

        kernel_len = np.array(img).shape[1] // 100

        ver_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_len))
        hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len, 1))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))

        image_1 = cv2.erode(img_bin, ver_kernel, iterations=3)
        vertical_lines = cv2.dilate(image_1, ver_kernel, iterations=3)

        image_2 = cv2.erode(img_bin, hor_kernel, iterations=3)
        horizontal_lines = cv2.dilate(image_2, hor_kernel, iterations=3)

        img_vh = cv2.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0.0)

        img_vh = cv2.erode(~img_vh, kernel, iterations=2)
        thresh, img_vh = cv2.threshold(img_vh, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        bitxor = cv2.bitwise_xor(img, img_vh)
        bitnot = cv2.bitwise_not(bitxor)
        contours, hierarchy = cv2.findContours(img_vh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        boundingBoxes = [cv2.boundingRect(c) for c in contours]
        (contours, boundingBoxes) = zip(*sorted(zip(contours, boundingBoxes),
                                            key=lambda b: b[1][1], reverse=False))

        box = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            image = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            box.append([x, y, w, h])

        row = []
        column = []
        j = 0

        # Sorting the boxes to their respective row and column
        for i in range(len(box)):

            if (i == 0):
                column.append(box[i])
                previous = box[i]

            else:
                if (box[i][1] == previous[1] ):

                    column.append(box[i])
                    previous = box[i]

                    if (i == len(box) - 1):
                        row.append(column)

                else:
                    row.append(column)
                    column = []
                    previous = box[i]
                    column.append(box[i])


        countcol = 0
        for i in range(len(row)):
            countcol = len(row[i])
            if countcol > countcol:
                countcol = countcol


        center = [int(row[i][j][0] + row[i][j][2] / 2) for j in range(len(row[i])) if row[0]]

        center = np.array(center)
        center.sort()

        finalboxes = []
        for i in range(len(row)):
            lis = []
            for k in range(countcol):
                lis.append([])
            for j in range(len(row[i])):
                diff = abs(center - (row[i][j][0] + row[i][j][2] / 4))
                minimum = min(diff)
                indexing = list(diff).index(minimum)
                lis[indexing].append(row[i][j])
            finalboxes.append(lis)

        outer = []
        for i in range(len(finalboxes)):
            for j in range(len(finalboxes[i])):
                inner = ''
                if (len(finalboxes[i][j]) == 0):
                    outer.append(' ')
                else:
                    for k in range(len(finalboxes[i][j])):
                        y, x, w, h = finalboxes[i][j][k][0], finalboxes[i][j][k][1], finalboxes[i][j][k][2], \
                                     finalboxes[i][j][k][3]
                        finalimg = bitnot[x:x + h, y:y + w]
                        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
                        border = cv2.copyMakeBorder(finalimg, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=[255, 255])
                        resizing = cv2.resize(border, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                        dilation = cv2.dilate(resizing, kernel, iterations=1)
                        erosion = cv2.erode(dilation, kernel, iterations=2)

                        out = pytesseract.image_to_string(erosion)
                        if (len(out) == 0):
                            out = pytesseract.image_to_string(erosion, config='--psm 3')
                        inner = inner + " " + out
                    outer.append(inner)



        arr = np.array(outer)
        dataframe = pd.DataFrame(arr.reshape(len(row), countcol))
        table_ocrs.append(dataframe)
table_ocr=pd.concat(table_ocrs, axis=0)
with open('table.pickle', 'wb') as handle:
    pickle.dump(table_ocr, handle, protocol=pickle.HIGHEST_PROTOCOL)