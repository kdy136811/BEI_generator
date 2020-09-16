import cv2
import os
import numpy as np
import glob
import xml.etree.ElementTree as et

VIDEO_PATH = '../videos/'
XML_PATH = '../xml/'

def saveFirstFrame(video_list):
    for video in video_list:
        vc = cv2.VideoCapture(video)
        ret, video_frame = vc.read()
        path = video.replace('videos', 'label')
        cv2.imwrite(path.replace('mp4', 'jpg'), video_frame)

def clipImage(bbox, num):
    vc = cv2.VideoCapture(VIDEO_PATH + str(num) + '.mp4')
    frame = 1
    size = 64
    thres1 = 0.012
    thres2 = 3
    end_clip = 0
    clip = []
    diff = np.zeros((size,size), np.uint8)
    ret, video_frame = vc.read()
    if not ret:
        print('Load video failed')
    while ret:
        #if not ret:
        #    ret, video_frame = vc.read()
        #    continue
        #crop -> grayscale -> gaussianblur
        crop = cv2.resize(video_frame[bbox[1]:bbox[3], bbox[0]:bbox[2]], (size, size))
        gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray,(3, 3), 0)
        #generate difference images
        motion_pixel = 0
        if frame == 1:
            prev = blur
        else:
            for i in range(size):
                for j in range(size):
                    if abs(int(blur[i][j]) - int(prev[i][j])) > 25:
                        diff[i][j] = abs(int(blur[i][j]) - int(prev[i][j]))
                        motion_pixel += 1
                    else:
                        diff[i][j] = 0
        #calculate motion ratio
        if float(motion_pixel)/float(size*size) > thres1:
            clip.append(diff.copy())
            end_clip = 0
        else:
            if len(clip) > 0:
                end_clip += 1
        if end_clip >= thres2:
            #generate basketbal energy image
            generateBEI(clip, size, frame, num)
            end_clip = 0
            clip = []
        ret, video_frame = vc.read()
        frame += 1

    print(frame)

def generateBEI(clip, size, frame, num):
    fps = 60
    bei = np.zeros((size,size), np.uint8)
    T = len(clip)
    for t in range(1, T+1):
        for i in range(size):
            for j in range(size):
                if clip[t-1][i][j] > 0:
                    bei[i][j] = t/T * 255
    start_frame = frame - T
    cv2.imwrite('bei/'+ str(num)+'_' + str(round(start_frame/fps,1))+'-' +str(round(frame/fps,1))+'.jpg', bei)

if __name__ == '__main__':
    #save the first frame in each video to do labeling
    if not (os.path.isdir('../label')):
        os.mkdir('../label')
    #saveFirstFrame(glob.glob(VIDEO_PATH +'17.mp4'))

    if not (os.path.isdir('bei')):
        os.mkdir('bei')

    #count the number of files in xml/
    num_xml = 0
    for x in os.listdir(XML_PATH):
        num_xml += 1

    #get the bboxes' coordinates
    xmin = []
    xmax = []
    ymin = []
    ymax = []
    for i in range(num_xml):
        xml = et.parse(XML_PATH + str(i) +'.xml')
        root = xml.getroot()
        obj = root.findall('object')
        bbox = obj[0].find('bndbox')
        xmin.append(int(bbox[0].text))
        ymin.append(int(bbox[1].text))
        xmax.append(int(bbox[2].text))
        ymax.append(int(bbox[3].text))

    #get BEIs
    num_xml = 19
    for i in range(num_xml,num_xml+1):
        bndbox = [xmin[16], ymin[16], xmax[16], ymax[16]]
        clipImage(bndbox, i)
