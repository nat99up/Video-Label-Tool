import os
import cv2
import numpy as np


def cropLoader(crop_files,dataset=None,isView=False):

    INTERVAL_ON = False

    if type(crop_files) is not list:
        print('Input should be a list of crop filenames')
        return 
    
    interval_datas = []

    for crop_file in crop_files:

        with open(crop_file,'r') as f:
            dir_path = os.path.splitext(crop_file)[0]
            for row in f:
                row = row.split()
                img_id = int(row[0])
                boxes = np.array(list(map(lambda z: float(z), row[1:]))).astype(np.int)
                img_path = os.path.join(dir_path,'{}.png'.format(img_id))

                if boxes.sum() <= 0:            # close a interval
                    INTERVAL_ON = False
                    continue
                elif INTERVAL_ON == False:      # start a new interval
                    interval_datas.append([])
                    INTERVAL_ON = True

                info = {'img_path':img_path, 'boxes':boxes}

                if isView:
                    img = cv2.imread(img_path)
                    cv2.rectangle(img,(boxes[0],boxes[1]),(boxes[2],boxes[3]),(127,0,255),2)
                    cv2.imshow('Viewer',img)
                    cv2.waitKey(1)

                if dataset is not None:
                    y_dist,y_diff,x_diff = dataset.getVal(img_path)
                    info['label'] = 1 if y_diff>0 else 1
                    info['y_dist'] = y_dist
                    info['y_diff'] = y_diff
                    info['x_diff'] = x_diff

                interval_datas[-1].append(info)
    return interval_datas

if __name__ == '__main__':
    a = cropLoader(['data/1.17/9.crop'],isView=False)
    print(a)